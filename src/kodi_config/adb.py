from __future__ import annotations

import socket
import subprocess
import zipfile
from pathlib import Path
from urllib.request import urlretrieve

from kodi_config.config import is_ipv4_address

ADB_DOWNLOAD_URL = (
    "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"
)
KODI_REMOTE_PATH = "/sdcard/Android/data/org.xbmc.kodi/files/.kodi"


class AdbError(Exception):
    """ADB operation failed."""
    pass


class HostnameResolutionError(AdbError):
    """Could not resolve a hostname to an IP address."""
    pass


def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


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


def connect_and_verify(adb: Path, target: str) -> None:
    """Connect to a device over the network and verify it is authorized."""
    address = resolve_hostname(target)
    run_adb(adb, "disconnect", check=False)
    run_adb(adb, "connect", address)

    devices = run_adb(adb, "devices", check=False)
    for line in devices.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[0] == address and parts[1] == "device":
            return

    raise AdbError(f"Device {address} not connected or not authorized")


def disconnect(adb: Path, target: str | None = None) -> None:
    if target:
        run_adb(adb, "disconnect", resolve_hostname(target), check=False)
    else:
        run_adb(adb, "disconnect", check=False)


def is_device_connected(adb: Path, ip: str) -> bool:
    devices = run_adb(adb, "devices", check=False)
    for line in devices.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[0] == ip and parts[1] == "device":
            return True
    return False


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
