from __future__ import annotations

import configparser
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Device:
    name: str
    hostname: str


def load_devices(config_path: Path) -> list[Device]:
    """Load devices from the [firesticks] section of config.ini."""
    if not config_path.is_file():
        raise FileNotFoundError(f"config.ini not found: {config_path}")

    parser = configparser.ConfigParser()
    parser.optionxform = str  # preserve device name casing from config.ini
    parser.read(config_path, encoding="utf-8")

    if "firesticks" not in parser:
        raise ValueError("No [firesticks] section in config.ini")

    devices: list[Device] = []
    for name, hostname in parser["firesticks"].items():
        hostname = hostname.strip()
        if hostname:
            devices.append(Device(name=name, hostname=hostname))

    if not devices:
        raise ValueError("No devices found in config.ini [firesticks] section")

    return devices


def parse_menu_choice(selection: str, *, min_value: int, max_value: int) -> int:
    """Parse a 1-based menu index from user input."""
    if not selection.strip():
        raise ValueError("No selection made")

    try:
        value = int(selection.strip())
    except ValueError as exc:
        raise ValueError("Invalid selection") from exc

    if value < min_value:
        raise ValueError(f"Selection must be at least {min_value}")
    if value > max_value:
        raise ValueError(f"Selection must be at most {max_value}")

    return value


_IPV4_RE = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")


def is_ipv4_address(value: str) -> bool:
    if not _IPV4_RE.match(value):
        return False
    return all(0 <= int(part) <= 255 for part in value.split("."))
