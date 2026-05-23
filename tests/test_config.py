from pathlib import Path

import pytest

from kodi_config.config import Device, is_ipv4_address, load_devices, parse_menu_choice


def test_load_devices_from_firesticks_section(tmp_path: Path) -> None:
    config = tmp_path / "config.ini"
    config.write_text(
        "[firesticks]\n"
        "LivingRoom=android-4\n"
        "Basement=192.168.1.50\n",
        encoding="utf-8",
    )

    devices = load_devices(config)
    assert devices == [
        Device(name="LivingRoom", hostname="android-4"),
        Device(name="Basement", hostname="192.168.1.50"),
    ]


def test_load_devices_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError):
        load_devices(tmp_path / "missing.ini")


def test_load_devices_missing_section(tmp_path: Path) -> None:
    config = tmp_path / "config.ini"
    config.write_text("[other]\nfoo=bar\n", encoding="utf-8")
    with pytest.raises(ValueError, match="firesticks"):
        load_devices(config)


def test_load_devices_empty_section(tmp_path: Path) -> None:
    config = tmp_path / "config.ini"
    config.write_text("[firesticks]\n", encoding="utf-8")
    with pytest.raises(ValueError, match="No devices"):
        load_devices(config)


@pytest.mark.parametrize(
    ("selection", "expected"),
    [
        ("1", 1),
        ("  3  ", 3),
    ],
)
def test_parse_menu_choice_valid(selection: str, expected: int) -> None:
    assert parse_menu_choice(selection, min_value=1, max_value=5) == expected


@pytest.mark.parametrize(
    ("selection", "message"),
    [
        ("", "No selection"),
        ("abc", "Invalid selection"),
        ("0", "at least"),
        ("9", "at most"),
    ],
)
def test_parse_menu_choice_invalid(selection: str, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        parse_menu_choice(selection, min_value=1, max_value=5)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("192.168.1.1", True),
        ("10.0.0.5", True),
        ("256.1.1.1", False),
        ("android-4", False),
        ("1.2.3", False),
    ],
)
def test_is_ipv4_address(value: str, expected: bool) -> None:
    assert is_ipv4_address(value) is expected
