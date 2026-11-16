"""Tag lines can carry a friendly name (``= Name``) and flags (``| push[:s]``, ``| range:min-max``, ``| area:name``)."""

from __future__ import annotations

import pytest

from custom_components.s7_plus.const import DEFAULT_PULSE_DURATION
from custom_components.s7_plus.coordinator import parse_tag_line, parse_tag_specs, parse_tags


def test_plain_address_has_no_extras() -> None:
    assert parse_tag_line("DB1.DBD0:REAL") == ("DB1.DBD0:REAL", None, None, None, None)


def test_name_after_equals() -> None:
    assert parse_tag_line("DB1.DBX6.0:BOOL = Wohnzimmer Licht EIN") == (
        "DB1.DBX6.0:BOOL",
        "Wohnzimmer Licht EIN",
        None,
        None,
        None,
    )


def test_push_flag_default_duration() -> None:
    assert parse_tag_line("M10.0:BOOL|push") == ("M10.0:BOOL", None, DEFAULT_PULSE_DURATION, None, None)


def test_push_flag_custom_duration() -> None:
    assert parse_tag_line("M10.0:BOOL | push:1.5") == ("M10.0:BOOL", None, 1.5, None, None)


def test_name_and_push_combined() -> None:
    assert parse_tag_line("DB2.DBX0.0:BOOL=Licht EIN|push:0.2") == ("DB2.DBX0.0:BOOL", "Licht EIN", 0.2, None, None)


def test_nodes7_address_with_name() -> None:
    assert parse_tag_line("DB1,R8=Restlaufzeit") == ("DB1,R8", "Restlaufzeit", None, None, None)


def test_range_flag() -> None:
    assert parse_tag_line("DB5802.DBW2:INT=Helligkeit|range:0-100") == (
        "DB5802.DBW2:INT",
        "Helligkeit",
        None,
        (0.0, 100.0),
        None,
    )


def test_range_flag_negative_and_float() -> None:
    assert parse_tag_line("DB1.DBD0:REAL|range:-20.5-80") == ("DB1.DBD0:REAL", None, None, (-20.5, 80.0), None)


def test_area_flag() -> None:
    assert parse_tag_line("DB5802.DBX0.0:BOOL=Light1 On|push|area:Bar") == (
        "DB5802.DBX0.0:BOOL",
        "Light1 On",
        DEFAULT_PULSE_DURATION,
        None,
        "Bar",
    )


def test_all_flags_combined() -> None:
    assert parse_tag_line("DB5802.DBW2:INT = Light1 SP | range:0-100 | area:Bar") == (
        "DB5802.DBW2:INT",
        "Light1 SP",
        None,
        (0.0, 100.0),
        "Bar",
    )


@pytest.mark.parametrize(
    "line",
    [
        "DB1.DBD0:REAL=",  # empty name
        "=Nur ein Name",  # empty address
        "M10.0:BOOL|foo",  # unknown option
        "M10.0:BOOL|push:abc",  # duration is not a number
        "M10.0:BOOL|push:0.01",  # below the minimum
        "M10.0:BOOL|push:120",  # above the maximum
        "DB1.DBW4:INT|range:100-0",  # minimum above the maximum
        "DB1.DBW4:INT|range:abc-def",  # not numbers
        "M10.0:BOOL|area:",  # empty area name
    ],
)
def test_bad_lines_raise(line: str) -> None:
    with pytest.raises(ValueError, match="Invalid tag"):
        parse_tag_specs([line])


def test_range_needs_a_numeric_tag() -> None:
    with pytest.raises(ValueError, match="only valid for numeric"):
        parse_tag_specs(["M10.0:BOOL|range:0-100"])
    specs = parse_tag_specs(["DB1.DBW4:INT|range:0-100"])
    assert specs["DB1.DBW4:INT"].value_range == (0.0, 100.0)


def test_specs_are_keyed_by_bare_address() -> None:
    specs = parse_tag_specs(["DB1.DBD0:REAL=Temperatur", "M10.0:BOOL=Taster|push|area:Flur"])
    assert list(specs) == ["DB1.DBD0:REAL", "M10.0:BOOL"]
    assert specs["DB1.DBD0:REAL"].name == "Temperatur"
    assert specs["M10.0:BOOL"].push_duration == DEFAULT_PULSE_DURATION
    assert specs["M10.0:BOOL"].area == "Flur"


def test_parse_tags_wrapper_drops_extras() -> None:
    tags = parse_tags(["DB1.DBD0:REAL=Temperatur"])
    assert list(tags) == ["DB1.DBD0:REAL"]
    assert tags["DB1.DBD0:REAL"].datatype.upper() == "REAL"


def test_push_needs_a_writable_bool() -> None:
    with pytest.raises(ValueError, match="only valid for BOOL"):
        parse_tag_specs(["DB1.DBW4:INT|push"])
    with pytest.raises(ValueError, match="must be writable"):
        parse_tag_specs(["I0.0:BOOL|push"])


def test_conflicting_duplicate_address_raises() -> None:
    with pytest.raises(ValueError, match="already configured"):
        parse_tag_specs(["M10.0:BOOL=A", "M10.0:BOOL=B"])


def test_identical_repeat_is_one_tag() -> None:
    specs = parse_tag_specs(["M10.0:BOOL=A", "M10.0:BOOL=A"])
    assert list(specs) == ["M10.0:BOOL"]
