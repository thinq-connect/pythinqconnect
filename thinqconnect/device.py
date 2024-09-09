from __future__ import annotations

"""
    * SPDX-FileCopyrightText: Copyright 2024 LG Electronics Inc.
    * SPDX-License-Identifier: Apache-2.0
"""
"""class for base device"""

from .thinq_api import ThinQApi


class BaseDevice:
    """The base implementation of LG ThinQ Device."""

    thinq_api: ThinQApi

    def __init__(
        self,
        thinq_api: ThinQApi,
        device_id: str,
        device_type: str,
        model_name: str,
        alias: str,
        reportable: bool,
    ):
        self.thinq_api = thinq_api
        self.device_id = device_id
        self.device_type = device_type
        self.model_name = model_name
        self.alias = alias
        self.reportable = reportable

    @property
    def device_type(self) -> str:
        return self._device_type

    @device_type.setter
    def device_type(self, device_type: str):
        self._device_type = device_type

    @property
    def model_name(self) -> str:
        return self._model_name

    @model_name.setter
    def model_name(self, model_name: str):
        self._model_name = model_name

    @property
    def alias(self) -> str:
        return self._alias

    @alias.setter
    def alias(self, alias: str):
        self._alias = alias

    @property
    def reportable(self) -> bool:
        return self._reportable

    @reportable.setter
    def reportable(self, reportable: bool):
        self._reportable = reportable

    @property
    def device_id(self) -> str:
        return self._device_id

    @device_id.setter
    def device_id(self, device_id: str):
        self._device_id = device_id
