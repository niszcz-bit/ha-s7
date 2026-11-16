"""A ``| push`` tag is a momentary button, not a switch; a name renames the entity."""

from __future__ import annotations

from homeassistant.components.button import DOMAIN as BUTTON_DOMAIN
from homeassistant.components.button import SERVICE_PRESS
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry
from snap7.client import Client

from custom_components.s7_plus.const import CONF_HOST, CONF_PORT, CONF_RACK, CONF_SLOT, CONF_TAGS, DOMAIN

BIT = "DB2.DBX0.0:BOOL"


async def _setup(hass: HomeAssistant, port: int, tags: list[str]) -> MockConfigEntry:
    entry = MockConfigEntry(
        domain=DOMAIN,
        data={CONF_HOST: "127.0.0.1", CONF_RACK: 0, CONF_SLOT: 0, CONF_PORT: port, CONF_TAGS: tags},
    )
    entry.add_to_hass(hass)
    await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


def _entity_id(hass: HomeAssistant, port: int, address: str, platform: str) -> str | None:
    registry = er.async_get(hass)
    unique_id = f"127.0.0.1:{port}:0:0_{address}"
    entry = registry.async_get_entity_id(platform, DOMAIN, unique_id)
    return entry


def _bit_on_the_plc(port: int) -> bool:
    client = Client()
    client.connect("127.0.0.1", 0, 0, port)
    try:
        return bool(client.db_read(2, 0, 1)[0] & 1)
    finally:
        client.disconnect()


async def test_push_tag_is_a_button_not_a_switch(hass: HomeAssistant, s7_server) -> None:
    port = s7_server[1]
    entry = await _setup(hass, port, [f"{BIT}=Licht EIN|push:0.1"])
    button = _entity_id(hass, port, BIT, BUTTON_DOMAIN)
    assert button is not None
    assert _entity_id(hass, port, BIT, "switch") is None
    state = hass.states.get(button)
    assert state is not None
    assert state.name == "Licht EIN"

    await hass.services.async_call(BUTTON_DOMAIN, SERVICE_PRESS, {ATTR_ENTITY_ID: button}, blocking=True)
    await hass.async_block_till_done()
    assert not await hass.async_add_executor_job(_bit_on_the_plc, port)
    await hass.config_entries.async_unload(entry.entry_id)


async def test_named_tag_shows_its_name(hass: HomeAssistant, s7_server) -> None:
    port = s7_server[1]
    entry = await _setup(hass, port, ["DB1.DBD0:REAL=Temperatur Vorlauf"])
    entity_id = _entity_id(hass, port, "DB1.DBD0:REAL", "sensor")
    assert entity_id is not None
    state = hass.states.get(entity_id)
    assert state is not None
    assert state.name == "Temperatur Vorlauf"
    await hass.config_entries.async_unload(entry.entry_id)
