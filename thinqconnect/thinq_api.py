from __future__ import annotations

"""
    * SPDX-FileCopyrightText: Copyright 2024 LG Electronics Inc.
    * SPDX-License-Identifier: Apache-2.0
"""
"""Support for LG ThinQ Connect API."""

import base64
import logging
import uuid
from typing import Any

from aiohttp import ClientResponse, ClientSession
from aiohttp.hdrs import METH_DELETE, METH_GET, METH_POST
from aiohttp.typedefs import StrOrURL

from .const import API_KEY
from .country import get_region_from_country

_LOGGER = logging.getLogger(__name__)


class ThinQAPIErrorCodes:
    """The class that represents the error codes for LG ThinQ Connect API."""

    UNKNOWN_ERROR = "0000"
    BAD_REQUEST = "1000"
    MISSING_PARAMETERS = "1101"
    UNACCEPTABLE_PARAMETERS = "1102"
    INVALID_TOKEN = "1103"
    INVALID_MESSAGE_ID = "1104"
    NOT_REGISTERED_ADMIN = "1201"
    NOT_REGISTERED_USER = "1202"
    NOT_REGISTERED_SERVICE = "1203"
    NOT_SUBSCRIBED_EVENT = "1204"
    NOT_REGISTERED_DEVICE = "1205"
    NOT_SUBSCRIBED_PUSH = "1206"
    ALREADY_SUBSCRIBED_PUSH = "1207"
    NOT_REGISTERED_SERVICE_BY_ADMIN = "1208"
    NOT_REGISTERED_USER_IN_SERVICE = "1209"
    NOT_REGISTERED_DEVICE_IN_SERVICE = "1210"
    NOT_REGISTERED_DEVICE_BY_USER = "1211"
    NOT_OWNED_DEVICE = "1212"
    NOT_REGISTERED_DEVICE = "1213"
    NOT_SUBSCRIBABLE_DEVICE = "1214"
    INCORRECT_HEADER = "1216"
    ALREADY_DEVICE_DELETED = "1217"
    INVALID_TOKEN_AGAIN = "1218"
    NOT_SUPPORTED_MODEL = "1219"
    NOT_SUPPORTED_FEATURE = "1220"
    NOT_SUPPORTED_PRODUCT = "1221"
    NOT_CONNECTED_DEVICE = "1222"
    INVALID_STATUS_DEVICE = "1223"
    INVALID_DEVICE_ID = "1224"
    DUPLICATE_DEVICE_ID = "1225"
    INVALID_SERVICE_KEY = "1301"
    NOT_FOUND_TOKEN = "1302"
    NOT_FOUND_USER = "1303"
    NOT_ACCEPTABLE_TERMS = "1304"
    NOT_ALLOWED_API = "1305"
    EXCEEDED_API_CALLS = "1306"
    NOT_SUPPORTED_COUNTRY = "1307"
    NO_CONTROL_AUTHORITY = "1308"
    NOT_ALLOWED_API_AGAIN = "1309"
    NOT_SUPPORTED_DOMAIN = "1310"
    BAD_REQUEST_FORMAT = "1311"
    EXCEEDED_NUMBER_OF_EVENT_SUBSCRIPTION = "1312"
    INTERNAL_SERVER_ERROR = "2000"
    NOT_SUPPORTED_MODEL_AGAIN = "2101"
    NOT_PROVIDED_FEATURE = "2201"
    NOT_SUPPORTED_PRODUCT_AGAIN = "2202"
    NOT_EXISTENT_MODEL_JSON = "2203"
    INVALID_DEVICE_STATUS = "2205"
    INVALID_COMMAND_ERROR = "2207"
    FAIL_DEVICE_CONTROL = "2208"
    DEVICE_RESPONSE_DELAY = "2209"
    RETRY_REQUEST = "2210"
    SYNCING = "2212"
    RETRY_AFTER_DELETING_DEVICE = "2213"
    FAIL_REQUEST = "2214"
    COMMAND_NOT_SUPPORTED_IN_REMOTE_OFF = "2301"
    COMMAND_NOT_SUPPORTED_IN_STATE = "2302"
    COMMAND_NOT_SUPPORTED_IN_ERROR = "2303"
    COMMAND_NOT_SUPPORTED_IN_POWER_OFF = "2304"
    COMMAND_NOT_SUPPORTED_IN_MODE = "2305"


error_code_mapping = {value: name for name, value in vars(ThinQAPIErrorCodes).items()}


class ThinQAPIException(Exception):
    """The class that represents an exception for LG ThinQ Connect API."""

    def __init__(self, code: str, message: str, headers: dict):
        """Initialize the exception."""
        self.code = code
        self.message = message
        self.headers = headers
        self.error_name = error_code_mapping.get(code, "UNKNOWN_ERROR")
        super().__init__(f"Error: {self.error_name} ({self.code}) - {self.message}")

    def __str__(self) -> str:
        return f"ThinQAPIException: {self.error_name} ({self.code}) - {self.message}"


class ThinQApi:
    """The class for using LG ThinQ Connect API."""

    def __init__(
        self,
        session: ClientSession,
        access_token: str,
        country_code: str,
        client_id: str,
        mock_response: bool = False,
    ):
        """Initialize settings."""
        self._access_token = access_token
        self._client_id = client_id
        self._api_key = API_KEY
        self._session = session
        self._phase = "OP"
        self._country_code = country_code
        self._region_code = get_region_from_country(country_code)
        self._mock_response = mock_response

    def __await__(self):
        yield from self.async_init().__await__()
        return self

    async def async_init(self):
        pass

    def set_log_level(self, level):
        numeric_level = getattr(logging, level.upper(), None)
        if not isinstance(numeric_level, int):
            raise ValueError(f"Invalid log level: {level}")
        _LOGGER.setLevel(numeric_level)

    def _get_url_from_endpoint(self, endpoint: str) -> str:
        """Returns the URL to connect from the given endpoint."""
        return f"https://api-{self._region_code.lower()}.lgthinq.com/{endpoint}"

    def _generate_headers(self, headers: dict = {}) -> dict:
        """Generate common headers for request."""
        return {
            "Authorization": f"Bearer {self._access_token}",
            "x-country": self._country_code,
            "x-message-id": self._generate_message_id(),
            "x-client-id": self._client_id,
            "x-api-key": self._api_key,
            "x-service-phase": self._phase,
            **headers,
        }

    async def _async_fetch(self, method: str, url: StrOrURL, **kwargs: Any) -> ClientResponse:
        headers: dict[str, Any] = kwargs.pop("headers", {})
        if self._session is None:
            self._session = ClientSession()
        return await self._session.request(
            method=method,
            url=url,
            **kwargs,
            headers=headers,
        )

    async def async_get_device_list(self, timeout: int | float = 15) -> list | None:
        return await self.async_request(method=METH_GET, endpoint="devices", timeout=timeout)

    async def async_get_device_profile(self, device_id: str, timeout: int | float = 15) -> dict | None:
        return await self.async_request(
            method=METH_GET,
            endpoint=f"devices/{device_id}/profile",
            timeout=timeout,
        )

    async def async_get_device_status(self, device_id: str, timeout: int | float = 15) -> dict | None:
        return await self.async_request(method=METH_GET, endpoint=f"devices/{device_id}/state", timeout=timeout)

    async def async_post_device_control(self, device_id: str, payload: Any, timeout: int | float = 15) -> dict | None:
        headers = {"x-conditional-control": "true"}
        return await self.async_request(
            method=METH_POST,
            endpoint=f"devices/{device_id}/control",
            json=payload,
            timeout=timeout,
            headers=headers,
        )

    async def async_post_client_register(self, payload: Any, timeout: int | float = 15) -> dict | None:
        return await self.async_request(
            method=METH_POST,
            endpoint="client",
            json=payload,
            timeout=timeout,
        )

    async def async_delete_client_register(self, payload: Any, timeout: int | float = 15) -> dict | None:
        return await self.async_request(
            method=METH_DELETE,
            endpoint="client",
            json=payload,
            timeout=timeout,
        )

    async def async_post_client_certificate(self, payload: Any, timeout: int | float = 15) -> dict | None:
        return await self.async_request(
            method=METH_POST,
            endpoint="client/certificate",
            json=payload,
            timeout=timeout,
        )

    async def async_get_push_list(self, timeout: int | float = 15) -> dict | None:
        return await self.async_request(
            method=METH_GET,
            endpoint="push",
            timeout=timeout,
        )

    async def async_post_push_subscribe(self, device_id: str, timeout: int | float = 15) -> dict | None:
        return await self.async_request(
            method=METH_POST,
            endpoint=f"push/{device_id}/subscribe",
            timeout=timeout,
        )

    async def async_delete_push_subscribe(self, device_id: str, timeout: int | float = 15) -> dict | None:
        return await self.async_request(
            method=METH_DELETE,
            endpoint=f"push/{device_id}/unsubscribe",
            timeout=timeout,
        )

    async def async_get_event_list(self, timeout: int | float = 15) -> dict | None:
        return await self.async_request(
            method=METH_GET,
            endpoint="event",
            timeout=timeout,
        )

    async def async_post_event_subscribe(self, device_id: str, timeout: int | float = 15) -> dict | None:
        """Subscribe to event notifications for the device."""
        return await self.async_request(
            method=METH_POST,
            endpoint=f"event/{device_id}/subscribe",
            json={"expire": {"unit": "HOUR", "timer": 4464}},
            timeout=timeout,
        )

    async def async_delete_event_subscribe(self, device_id: str, timeout: int | float = 15) -> dict | None:
        """Unsubscribe to event notifications for the device."""
        return await self.async_request(
            method=METH_DELETE,
            endpoint=f"event/{device_id}/unsubscribe",
            timeout=timeout,
        )

    async def async_get_push_devices_list(self, timeout: int | float = 15) -> dict | None:
        """Get the list of clients subscribed to push notifications for devices registered,unregistered, and alias updated."""
        return await self.async_request(
            method=METH_GET,
            endpoint="push/devices",
            timeout=timeout,
        )

    async def async_post_push_devices_subscribe(self, timeout: int | float = 15) -> dict | None:
        """Subscribe to push notifications for devices registered,unregistered, and alias updated."""
        return await self.async_request(
            method=METH_POST,
            endpoint="push/devices",
            timeout=timeout,
        )

    async def async_delete_push_devices_subscribe(self, timeout: int | float = 15) -> dict | None:
        """Unsubscribe to push notifications for devices registered,unregistered, and alias updated."""
        return await self.async_request(
            method=METH_DELETE,
            endpoint="push/devices",
            timeout=timeout,
        )

    async def async_get_route(self, timeout: int | float = 15) -> dict | None:
        return await self.async_request(
            method=METH_GET,
            endpoint="route",
            timeout=timeout,
        )

    async def async_request(self, method: str, endpoint: str, **kwargs: Any) -> dict | list | None:
        url = self._get_url_from_endpoint(endpoint)
        headers = self._generate_headers(kwargs.pop("headers", {}))
        _LOGGER.debug(
            "async_request. method=%s, headers=%s, url=%s, kwargs=%s",
            method,
            headers,
            url,
            kwargs,
        )

        if self._mock_response:
            return {"message": "Mock Response", "body": kwargs.get("json")}

        async with await self._async_fetch(method=method, url=url, **kwargs, headers=headers) as response:
            payload = await response.json()
            if response.ok:
                return payload.get("response")
            else:
                raise ThinQAPIException(
                    code=payload.get("error").get("code", "unknown error code"),
                    message=payload.get("error").get("message", "unknown error message"),
                    headers=headers,
                )

    def _generate_message_id(self) -> str:
        return base64.urlsafe_b64encode(uuid.uuid4().bytes)[:-2].decode("utf-8")
