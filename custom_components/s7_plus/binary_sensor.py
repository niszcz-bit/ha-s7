"""Binary sensor platform — BOOL tags in read-only (input) area."""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from snap7.type import Area

from .entity import S7BaseEntity

if TYPE_CHECKING:
    from . import S7ConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,
    entry: S7ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    entities: list[S7BinarySensor] = []
    # BOOL tags from the input area (read-only), plus any BOOL flagged
    # ``| readonly`` — status bits in DB/M/Q, e.g. a blind's open/closed state.
    # Writable BOOLs without the flag become switches or push buttons instead.
    for raw, tag in coordinator.parsed_tags.items():
        if tag.datatype.upper() == "BOOL" and (tag.area == Area.PE or coordinator.tag_readonly(raw)):
            entities.append(S7BinarySensor(coordinator, raw))
    async_add_entities(entities)


class S7BinarySensor(S7BaseEntity, BinarySensorEntity):
    @property
    def is_on(self) -> bool | None:
        value = self._value()
        return bool(value) if value is not None else None
