"""Button platform — BOOL tags flagged with ``| push`` become momentary buttons.

Pressing the button pulses the tag: True, wait the configured duration, then
False again (with the coordinator's retry logic, so the bit does not stay
set). This fits PLC programs with separate set/reset logic — for example a
light that has its own ON and OFF bits — where a latching switch would have
to be switched off by hand after every press.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.components.button import ButtonEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DEFAULT_PULSE_DURATION, WRITABLE_AREAS
from .entity import S7BaseEntity

if TYPE_CHECKING:
    from . import S7ConfigEntry


async def async_setup_entry(
    hass: HomeAssistant,
    entry: S7ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    entities: list[S7PushButton] = []
    for raw, tag in coordinator.parsed_tags.items():
        if tag.datatype.upper() == "BOOL" and tag.area in WRITABLE_AREAS and coordinator.push_duration(raw) is not None:
            entities.append(S7PushButton(coordinator, raw))
    async_add_entities(entities)


class S7PushButton(S7BaseEntity, ButtonEntity):
    """A momentary push button: writes True, waits, writes False."""

    async def async_press(self) -> None:
        duration = self.coordinator.push_duration(self._tag)
        await self.coordinator.async_pulse_tag(self._tag, duration if duration is not None else DEFAULT_PULSE_DURATION)
