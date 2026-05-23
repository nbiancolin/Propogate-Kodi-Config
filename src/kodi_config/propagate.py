from __future__ import annotations

import shutil
from pathlib import Path

from kodi_config.adb import (
    connect_and_verify,
    disconnect,
    ensure_adb,
    project_root,
    pull_kodi_data,
    push_kodi_data,
)


def propagate_kodi(
    src_ip: str,
    dst_ip: str,
    *,
    root: Path | None = None,
    temp_dir: Path | None = None,
) -> None:
    """Pull Kodi config from source and push it to the destination device."""
    if not src_ip.strip():
        raise ValueError("Missing source IP")
    if not dst_ip.strip():
        raise ValueError("Missing destination IP")

    root = root or project_root()
    adb = ensure_adb(root)
    work_dir = temp_dir or (root / "temp")

    if work_dir.exists():
        shutil.rmtree(work_dir)
    work_dir.mkdir(parents=True)

    try:
        print(f"Propagating Kodi settings from {src_ip} to {dst_ip}...")

        connect_and_verify(adb, src_ip)
        pull_kodi_data(adb, work_dir)
        disconnect(adb)

        connect_and_verify(adb, dst_ip)
        push_kodi_data(adb, work_dir)
        disconnect(adb)

        print("Kodi config data successfully transferred. Have a nice day!")
    finally:
        if work_dir.exists():
            shutil.rmtree(work_dir, ignore_errors=True)
