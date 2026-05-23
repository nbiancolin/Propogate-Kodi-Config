from __future__ import annotations

import socket
import subprocess
import sys
import time
import zipfile
from pathlib import Path
from urllib.request import urlretrieve

from kodi_config.config import is_ipv4_address

ADB_DOWNLOAD_URL = (
    "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
)
KODI_REMOTE_PATH = "/sdcard/Android/data/org.xbmc.kodi/files/.kodi"
ADB_CONNECT_PORT = 5555
CONNECT_POLL_TIMEOUT_SECONDS = 10.0
CONNECT_POLL_INTERVAL_SECONDS = 0.5


class AdbError(Exception):
    """ADB operation failed."""
    pass


class HostnameResolutionError(AdbError):
    """Could not resolve a hostname to an IP address."""
    pass


def project_root() -> Path:
    """Directory for config.ini, adb/, and temp/ (repo root or folder containing the exe)."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    for directory in Path(__file__).resolve().parents:
        if (directory / "main.py").is_file():
            return directory
    raise RuntimeError(
        "Could not locate project root. Run from the repo that contains main.py."
    )


def config_ini_path(root: Path | None = None) -> Path:
    """Path to the user-editable config.ini (always beside main.py or the exe)."""
    return (root or project_root()) / "config.ini"


def adb_executable(root: Path | None = None) -> Path:
    root = root or project_root()
    return root / "adb" / "adb.exe"


def ensure_adb(root: Path | None = None) -> Path:
    """Download and extract platform-tools if adb.exe is missing."""
    root = root or project_root()
    exe = adb_executable(root)
    if exe.is_file():
        return exe

    print("ADB not found. Downloading platform-tools...")
    zip_path = root / "platform-tools-latest-windows.zip"

    try:
        urlretrieve(ADB_DOWNLOAD_URL, zip_path)
        with zipfile.ZipFile(zip_path, "r") as archive:
            archive.extractall(root)
    except OSError as exc:
        raise AdbError("Failed to download or extract ADB") from exc
    finally:
        if zip_path.is_file():
            zip_path.unlink()

    extracted = root / "platform-tools"
    target_dir = root / "adb"
    if extracted.is_dir():
        if target_dir.exists():
            import shutil

            shutil.rmtree(target_dir)
        extracted.rename(target_dir)

    if not exe.is_file():
        raise AdbError("ADB extraction failed")

    return exe


def resolve_hostname(hostname: str) -> str:
    """Resolve a hostname to an IPv4 address, or return the IP unchanged."""
    hostname = hostname.strip()
    if is_ipv4_address(hostname):
        return hostname

    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror as exc:
        raise HostnameResolutionError(
            f'Failed to resolve hostname "{hostname}"'
        ) from exc


def run_adb(adb: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        [str(adb), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if check and result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        raise AdbError(detail or f"adb {' '.join(args)} failed")
    return result


def adb_connect_target(address: str) -> str:
    """Address passed to ``adb connect`` (Fire TV network debugging uses port 5555)."""
    address = address.strip()
    if ":" in address:
        return address
    if is_ipv4_address(address):
        return f"{address}:{ADB_CONNECT_PORT}"
    return address


def adb_host_from_serial(serial: str) -> str:
    """Normalize ``adb devices`` serial (e.g. ``10.0.0.5:5555``) to a host for comparison."""
    if serial.count(":") == 1:
        host, port = serial.rsplit(":", 1)
        if port.isdigit():
            return host
    return serial


def serial_matches_address(serial: str, address: str) -> bool:
    """True when an ``adb devices`` line refers to the same host as ``address``."""
    resolved = resolve_hostname(address)
    return serial == resolved or serial == adb_connect_target(resolved) or (
        adb_host_from_serial(serial) == adb_host_from_serial(resolved)
    )


def list_device_states(adb: Path) -> dict[str, str]:
    """Map ``adb devices`` serials to states (``device``, ``unauthorized``, etc.)."""
    devices = run_adb(adb, "devices", check=False)
    states: dict[str, str] = {}
    for line in devices.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[0] != "List":
            states[parts[0]] = parts[1]
    return states


def device_state(adb: Path, address: str) -> str | None:
    """Return the ``adb devices`` state for ``address``, or ``None`` if not listed."""
    for serial, state in list_device_states(adb).items():
        if serial_matches_address(serial, address):
            return state
    return None


def connect_and_verify(adb: Path, target: str) -> str:
    """Connect to a device over the network and verify it is authorized.

    Returns the resolved host/IP. Raises ``AdbError`` on failure.
    """
    address = resolve_hostname(target)
    connect_target = adb_connect_target(address)

    run_adb(adb, "disconnect", check=False)
    result = run_adb(adb, "connect", connect_target, check=False)
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "").strip()
        raise AdbError(detail or f"adb connect {connect_target} failed")

    deadline = time.monotonic() + CONNECT_POLL_TIMEOUT_SECONDS
    while time.monotonic() < deadline:
        state = device_state(adb, address)
        if state == "device":
            return address
        if state == "unauthorized":
            raise AdbError(
                f"Device {address} is connected but not authorized. "
                "On the Fire TV, accept the ADB debugging prompt and try again."
            )
        time.sleep(CONNECT_POLL_INTERVAL_SECONDS)

    states = list_device_states(adb)
    listed = [
        f"{serial} ({state})"
        for serial, state in states.items()
        if serial_matches_address(serial, address)
    ]
    if listed:
        detail = ", ".join(listed)
    elif states:
        detail = f"adb devices: {states!r}"
    else:
        detail = "device not listed in adb devices"
    raise AdbError(f"Device {address} not ready: {detail}")


def disconnect(adb: Path, target: str | None = None) -> None:
    if target:
        address = resolve_hostname(target)
        run_adb(adb, "disconnect", adb_connect_target(address), check=False)
        run_adb(adb, "disconnect", address, check=False)
    else:
        run_adb(adb, "disconnect", check=False)


def is_device_connected(adb: Path, address: str) -> bool:
    return device_state(adb, address) == "device"


def pull_kodi_data(adb: Path, local_dir: Path) -> None:
    local_dir.mkdir(parents=True, exist_ok=True)
    kodi_dir = local_dir / ".kodi"
    if kodi_dir.exists():
        import shutil

        shutil.rmtree(kodi_dir)
    run_adb(adb, "pull", KODI_REMOTE_PATH, str(kodi_dir))


def push_kodi_data(adb: Path, local_dir: Path) -> None:
    kodi_dir = local_dir / ".kodi"
    if not kodi_dir.is_dir():
        raise AdbError("Local .kodi directory not found after pull")
    remote_parent = "/sdcard/Android/data/org.xbmc.kodi/files/"
    run_adb(adb, "push", str(kodi_dir), remote_parent)
