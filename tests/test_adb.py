import socket
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from kodi_config.adb import (
    HostnameResolutionError,
    connect_and_verify,
    ensure_adb,
    is_device_connected,
    resolve_hostname,
    run_adb,
)


def test_resolve_hostname_returns_ipv4_unchanged() -> None:
    assert resolve_hostname("192.168.0.10") == "192.168.0.10"


@patch("kodi_config.adb.socket.gethostbyname", return_value="10.0.0.5")
def test_resolve_hostname_dns(mock_gethostbyname: MagicMock) -> None:
    assert resolve_hostname("android-4") == "10.0.0.5"
    mock_gethostbyname.assert_called_once_with("android-4")


@patch("kodi_config.adb.socket.gethostbyname", side_effect=socket.gaierror("fail"))
def test_resolve_hostname_failure(_mock_gethostbyname: MagicMock) -> None:
    with pytest.raises(HostnameResolutionError):
        resolve_hostname("missing-host")


def test_ensure_adb_skips_download_when_present(tmp_path: Path) -> None:
    adb_dir = tmp_path / "adb"
    adb_dir.mkdir()
    exe = adb_dir / "adb.exe"
    exe.write_text("stub", encoding="utf-8")

    with patch("kodi_config.adb.urlretrieve") as mock_download:
        path = ensure_adb(tmp_path)

    assert path == exe
    mock_download.assert_not_called()


@patch("kodi_config.adb.run_adb")
def test_connect_and_verify_success(mock_run_adb: MagicMock, tmp_path: Path) -> None:
    adb = tmp_path / "adb.exe"

    def side_effect(_adb: Path, *args: str, check: bool = True) -> MagicMock:
        if args == ("devices",):
            result = MagicMock(returncode=0)
            result.stdout = "List of devices attached\n10.0.0.5\tdevice\n"
            return result
        return MagicMock(returncode=0, stdout="", stderr="")

    mock_run_adb.side_effect = side_effect
    connect_and_verify(adb, "10.0.0.5")
    mock_run_adb.assert_any_call(adb, "connect", "10.0.0.5")


@patch("kodi_config.adb.run_adb")
def test_is_device_connected(mock_run_adb: MagicMock, tmp_path: Path) -> None:
    adb = tmp_path / "adb.exe"
    mock_run_adb.return_value = MagicMock(
        returncode=0,
        stdout="List of devices attached\n192.168.1.2\tdevice\n",
    )
    assert is_device_connected(adb, "192.168.1.2") is True
    assert is_device_connected(adb, "192.168.1.99") is False
