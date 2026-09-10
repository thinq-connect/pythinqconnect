from __future__ import annotations

"""
    * SPDX-FileCopyrightText: Copyright 2024 LG Electronics Inc.
    * SPDX-License-Identifier: Apache-2.0
"""
"""Support for LG ThinQ Connect API."""

import asyncio
import logging
from enum import Enum
from typing import Callable

from aiohttp import ClientTimeout, request
from awscrt import io, mqtt
from awsiot import mqtt_connection_builder
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

from .thinq_api import ThinQApi

FILE_ROOT_CA = "AmazonRootCA1.pem"
ROOT_CA_REPOSITORY = "https://www.amazontrust.com/repository"
PRIVATE_KEY_SIZE = 2048

_LOGGER = logging.getLogger(__name__)

CLIENT_BODY = {"type": "MQTT", "service-code": "SVC202", "device-type": "607", "allowExist": True}


class ClientConnectionState(str, Enum):
    """client connection state."""

    CLIENT_CONNECTED = "client_connected"
    CLIENT_DISCONNECTED = "client_disconnected"

    def __str__(self):
        return self.name


class ThinQMQTTClient:
    """A class for LG Connect-Client API calls."""

    def __init__(
        self,
        thinq_api: ThinQApi,
        client_id: str,
        on_message_received: Callable,
        on_connection_interrupted: Callable = None,
        on_connection_success: Callable = None,
        on_connection_failure: Callable = None,
        on_connection_closed: Callable = None,
    ):
        self._thinq_api = thinq_api
        self._client_id = client_id
        self._mqtt_connection: mqtt.Connection = None
        self._on_message_received = on_message_received
        self._on_connection_interrupted = on_connection_interrupted
        self._on_connection_success = on_connection_success
        self._on_connection_failure = on_connection_failure
        self._on_connection_closed = on_connection_closed
        self._state: str = ClientConnectionState.CLIENT_DISCONNECTED

    def __await__(self):
        yield from self.async_init().__await__()
        return self

    async def async_init(self):
        route_response = await self._thinq_api.async_get_route()
        self._mqtt_server = route_response.get("mqttServer").replace("mqtts://", "").split(":", maxsplit=1)[0]

    @property
    def mqtt_server(self) -> str:
        return self._mqtt_server

    @mqtt_server.setter
    def mqtt_server(self, mqtt_server: str):
        self._mqtt_server = mqtt_server

    @property
    def bytes_root_ca(self) -> bytes:
        """Return root CA certificate bytes."""
        return self._bytes_root_ca

    @bytes_root_ca.setter
    def bytes_root_ca(self, bytes_root_ca: bytes):
        """Set root CA certificate bytes."""
        self._bytes_root_ca = bytes_root_ca

    @property
    def bytes_private_key(self) -> bytes:
        """Return private key bytes."""
        return self._bytes_private_key

    @bytes_private_key.setter
    def bytes_private_key(self, bytes_private_key: bytes):
        """Set private key bytes."""
        self._bytes_private_key = bytes_private_key

    @property
    def bytes_certificate(self) -> bytes:
        """Return client certificate bytes."""
        return self._bytes_certificate

    @bytes_certificate.setter
    def bytes_certificate(self, bytes_certificate: bytes):
        """Set client certificate bytes."""
        self._bytes_certificate = bytes_certificate

    @property
    def csr_str(self) -> str:
        """Return client CSR string."""
        return self._csr_str

    @csr_str.setter
    def csr_str(self, csr_str: str):
        """Set client CSR string."""
        self._csr_str = csr_str

    @property
    def topic_subscription(self) -> str:
        """Return subscription topics."""
        return self._topic_subscription

    @topic_subscription.setter
    def topic_subscription(self, topic_subscription: str):
        """Set subscription topics."""
        self._topic_subscription = topic_subscription

    @property
    def is_connected(self) -> bool:
        """Return true if the client is connected to the mqtt."""
        return self._state == ClientConnectionState.CLIENT_CONNECTED

    async def async_prepare_mqtt(self) -> bool:
        """Prepare for MQTT connection."""
        await self._thinq_api.async_post_client_register(payload=CLIENT_BODY)
        if not await self.generate_csr():
            return False
        if not await self.issue_certificate():
            return False
        return True

    async def _on_disconnect(self) -> None:
        """Handle client disconnect."""
        result = await self._thinq_api.async_delete_client_register(payload=CLIENT_BODY)
        _LOGGER.debug("Delete client register, result: %s", result)
        self._state = ClientConnectionState.CLIENT_DISCONNECTED

    async def generate_csr(self) -> bool:
        """Create CSR."""
        cert_data = await self._get_root_certificate()

        if cert_data is None:
            _LOGGER.error("Root certification download failed")
            return False

        self.bytes_root_ca = cert_data.encode("utf-8")

        key = rsa.generate_private_key(public_exponent=65537, key_size=PRIVATE_KEY_SIZE)
        self.bytes_private_key = key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        csr = (
            x509.CertificateSigningRequestBuilder()
            .subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "lg_thinq")]))
            .sign(key, hashes.SHA512())
        )
        csr_pem = csr.public_bytes(serialization.Encoding.PEM).decode("ascii")
        self.csr_str = "".join(csr_pem.strip().splitlines()[1:-1])
        return True

    async def issue_certificate(self) -> bool:
        """Create client certificate."""
        if not self.csr_str:
            _LOGGER.error("No device specified. skip.")
            return False
        body = {
            "service-code": "SVC202",
            "csr": self.csr_str,
        }
        _LOGGER.info("Request client certificate, body: %s", body)

        response = await self._thinq_api.async_post_client_certificate(body)
        if response is None:
            return False

        _LOGGER.debug("Request client certificate, result: %s", response)
        certificate_pem: str = response.get("result").get("certificatePem")
        subscriptions: list[str] = response.get("result").get("subscriptions")
        if certificate_pem is None or subscriptions is None:
            return False

        self.bytes_certificate = certificate_pem.encode("utf-8")
        self.topic_subscription = subscriptions[0]

        return True

    async def _get_root_certificate(self, timeout: int = 15) -> str | None:
        """Get aws root CA certificate."""
        url = f"{ROOT_CA_REPOSITORY}/{FILE_ROOT_CA}"
        _LOGGER.debug("get_root_certificate. url=%s", url)
        client_timeout = ClientTimeout(total=timeout)
        async with request("GET", url=url, timeout=client_timeout) as response:
            result = await response.text()
            if response.status != 200 or "error" in result:
                _LOGGER.error(
                    "Failed to call API: status=%s, result=%s",
                    response.status,
                    result,
                )
                return None
            return result

    async def async_connect_mqtt(self) -> None:
        """Start push/event subscribes."""

        def connect_mqtt():
            event_loop_group = io.EventLoopGroup(1)
            host_resolver = io.DefaultHostResolver(event_loop_group)
            client_bootstrap = io.ClientBootstrap(event_loop_group, host_resolver)
            mqtt_connection = mqtt_connection_builder.mtls_from_bytes(
                endpoint=self._mqtt_server,
                port=None,
                cert_bytes=self.bytes_certificate,
                pri_key_bytes=self.bytes_private_key,
                client_bootstrap=client_bootstrap,
                ca_bytes=self.bytes_root_ca,
                on_connection_interrupted=self._on_connection_interrupted,
                on_connection_success=self._on_connection_success,
                on_connection_failure=self._on_connection_failure,
                on_connection_closed=self._on_connection_closed,
                client_id=self._client_id,
                clean_session=False,
                keep_alive_secs=6,
                http_proxy_options=None,
            )
            return mqtt_connection

        loop = asyncio.get_running_loop()
        mqtt_connection = await loop.run_in_executor(None, connect_mqtt)

        _LOGGER.debug(
            "Connecting to endpoint=%s, client_id: %s",
            self.mqtt_server,
            self._client_id,
        )

        try:
            connect_future = mqtt_connection.connect()
            connect_result = connect_future.result()
            _LOGGER.debug(
                "Connect with session_present : %s",
                connect_result["session_present"],
            )
            self._state = ClientConnectionState.CLIENT_CONNECTED
        except Exception as err:
            _LOGGER.error("Failed to connect endpoint: %s", err)
            return None
        self._mqtt_connection = mqtt_connection
        if self._mqtt_connection is not None:
            try:
                subscribe_future, _ = self._mqtt_connection.subscribe(
                    topic=self.topic_subscription,
                    qos=mqtt.QoS.AT_LEAST_ONCE,
                    callback=self._on_message_received,
                )
                subscribe_future.result()
                _LOGGER.debug("Complete subscription!")
            except Exception as err:
                _LOGGER.error("Failed to subscription: %s", err)

    async def async_disconnect(self) -> None:
        """Unregister client and disconnects handlers"""
        if self._mqtt_connection is not None:
            self._mqtt_connection.unsubscribe(topic=self.topic_subscription)
        await self._on_disconnect()
