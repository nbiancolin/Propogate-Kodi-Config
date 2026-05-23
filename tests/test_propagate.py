from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from kodi_config.propagate import propagate_kodi


@patch("kodi_config.propagate.disconnect")
@patch("kodi_config.propagate.push_kodi_data")
@patch("kodi_config.propagate.pull_kodi_data")
@patch("kodi_config.propagate.connect_and_verify")
@patch("kodi_config.propagate.ensure_adb")
def test_propagate_kodi_happy_path(
    mock_ensure_adb: MagicMock,
    mock_connect: MagicMock,
    mock_pull: MagicMock,
    mock_push: MagicMock,
    mock_disconnect: MagicMock,
    tmp_path: Path,
) -> None:
    mock_ensure_adb.return_value = tmp_path / "adb.exe"

    propagate_kodi("10.0.0.1", "10.0.0.2", root=tmp_path, temp_dir=tmp_path / "work")

    assert mock_connect.call_args_list == [
        ((tmp_path / "adb.exe", "10.0.0.1"),),
        ((tmp_path / "adb.exe", "10.0.0.2"),),
    ]
    mock_pull.assert_called_once()
    mock_push.assert_called_once()
    assert mock_disconnect.call_count == 2
    assert not (tmp_path / "work").exists()


def test_propagate_kodi_requires_ips() -> None:
    with pytest.raises(ValueError, match="source"):
        propagate_kodi("", "10.0.0.2")
    with pytest.raises(ValueError, match="destination"):
        propagate_kodi("10.0.0.1", "")
