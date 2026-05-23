import socket
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from kodi_config.adb import (
    HostnameResolutionError,
    adb_connect_target,
    adb_executable,
    config_ini_path,
    connect_and_verify,
    ensure_adb,
    is_device_connected,
    project_root,
    resolve_hostname,
    run_adb,
    serial_matches_address,
)


def test_project_root_is_repository_root() -> None:
    root = project_root()
    assert root.name != "src"
    assert (root / "main.py").is_file()
    assert (root / "config.ini.sample").is_file()
    assert adb_executable(root) == root / "adb" / "adb.exe"


def test_project_root_when_frozen(tmp_path: Path) -> None:
    fake_exe = tmp_path / "Propogate-Kodi-Config.exe"
    fake_exe.write_text("", encoding="utf-8")
    with (
        patch.object(sys, "frozen", True, create=True),
        patch.object(sys, "executable", str(fake_exe)),
    ):
        assert project_root() == tmp_path


def test_config_ini_path_beside_exe_when_frozen(tmp_path: Path) -> None:
    fake_exe = tmp_path / "Propogate-Kodi-Config.exe"
    fake_exe.write_text("", encoding="utf-8")
    with (
        patch.object(sys, "frozen", True, create=True),
        patch.object(sys, "executable", str(fake_exe)),
    ):
        assert config_ini_path() == tmp_path / "config.ini"


def test_config_ini_path_beside_project_root() -> None:
    root = project_root()
    assert config_ini_path(root) == root / "config.ini"


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


def test_adb_connect_target_adds_port_for_ipv4() -> None:
    assert adb_connect_target("10.0.0.5") == "10.0.0.5:5555"
    assert adb_connect_target("10.0.0.5:5555") == "10.0.0.5:5555"


def test_serial_matches_address_accepts_port_suffix() -> None:
    assert serial_matches_address("10.0.0.5:5555", "10.0.0.5")
    assert serial_matches_address("10.0.0.5", "10.0.0.5")
    assert not serial_matches_address("10.0.0.6:5555", "10.0.0.5")


@patch("kodi_config.adb.run_adb")
def test_connect_and_verify_success(mock_run_adb: MagicMock, tmp_path: Path) -> None:
    adb = tmp_path / "adb.exe"

    def side_effect(_adb: Path, *args: str, check: bool = True) -> MagicMock:
        if args == ("devices",):
            result = MagicMock(returncode=0)
            result.stdout = "List of devices attached\n10.0.0.5:5555\tdevice\n"
            return result
        return MagicMock(returncode=0, stdout="", stderr="")

    mock_run_adb.side_effect = side_effect
    assert connect_and_verify(adb, "10.0.0.5") == "10.0.0.5"
    mock_run_adb.assert_any_call(adb, "connect", "10.0.0.5:5555", check=False)


@patch("kodi_config.adb.time.sleep")
@patch("kodi_config.adb.run_adb")
def test_connect_and_verify_polls_until_ready(
    mock_run_adb: MagicMock, mock_sleep: MagicMock, tmp_path: Path
) -> None:
    adb = tmp_path / "adb.exe"
    devices_calls = 0

    def side_effect(_adb: Path, *args: str, check: bool = True) -> MagicMock:
        nonlocal devices_calls
        if args == ("devices",):
            devices_calls += 1
            result = MagicMock(returncode=0)
            if devices_calls < 2:
                result.stdout = "List of devices attached\n"
            else:
                result.stdout = "List of devices attached\n10.0.0.5:5555\tdevice\n"
            return result
        return MagicMock(returncode=0, stdout="", stderr="")

    mock_run_adb.side_effect = side_effect
    connect_and_verify(adb, "10.0.0.5")
    assert devices_calls >= 2
    mock_sleep.assert_called()


@patch("kodi_config.adb.run_adb")
def test_connect_and_verify_unauthorized(mock_run_adb: MagicMock, tmp_path: Path) -> None:
    from kodi_config.adb import AdbError

    adb = tmp_path / "adb.exe"

    def side_effect(_adb: Path, *args: str, check: bool = True) -> MagicMock:
        if args == ("devices",):
            result = MagicMock(returncode=0)
            result.stdout = "List of devices attached\n10.0.0.5:5555\tunauthorized\n"
            return result
        return MagicMock(returncode=0, stdout="", stderr="")

    mock_run_adb.side_effect = side_effect
    with pytest.raises(AdbError, match="not authorized"):
        connect_and_verify(adb, "10.0.0.5")


@patch("kodi_config.adb.run_adb")
def test_is_device_connected(mock_run_adb: MagicMock, tmp_path: Path) -> None:
    adb = tmp_path / "adb.exe"
    mock_run_adb.return_value = MagicMock(
        returncode=0,
        stdout="List of devices attached\n192.168.1.2:5555\tdevice\n",
    )
    assert is_device_connected(adb, "192.168.1.2") is True
    assert is_device_connected(adb, "192.168.1.99") is False
