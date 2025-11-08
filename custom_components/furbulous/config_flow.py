"""Config flow for Furbulous Cat integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN
from .furbulous_api import FurbulousCatAPI, FurbulousCatAuthError

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_EMAIL): str,
        vol.Required(CONF_PASSWORD): str,
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Furbulous Cat."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                # Use email/password authentication with account_type = 1 (default)
                if not user_input.get(CONF_EMAIL) or not user_input.get(CONF_PASSWORD):
                    errors["base"] = "missing_credentials"
                else:
                    api = FurbulousCatAPI(
                        email=user_input[CONF_EMAIL],
                        password=user_input[CONF_PASSWORD],
                        account_type=1  # Always use account_type = 1
                    )
                    await self.hass.async_add_executor_job(api.authenticate)

                    # Create the entry
                    await self.async_set_unique_id(user_input[CONF_EMAIL])
                    self._abort_if_unique_id_configured()

                    return self.async_create_entry(
                        title=f"Furbulous Cat ({user_input[CONF_EMAIL]})",
                        data={
                            CONF_EMAIL: user_input[CONF_EMAIL],
                            CONF_PASSWORD: user_input[CONF_PASSWORD],
                            "account_type": 1,
                        },
                    )

            except FurbulousCatAuthError:
                errors["base"] = "invalid_auth"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
