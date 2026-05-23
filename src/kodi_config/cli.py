from __future__ import annotations

import sys
import time
from pathlib import Path

from kodi_config.adb import (
    AdbError,
    HostnameResolutionError,
    adb_executable,
    config_ini_path,
    connect_and_verify,
    disconnect,
    ensure_adb,
    project_root,
    resolve_hostname,
)
from kodi_config.config import Device, load_devices, parse_menu_choice
from kodi_config.propagate import propagate_kodi


def _clear_screen() -> None:
    print("\033[2J\033[H", end="")


def _pause() -> None:
    input("\nPress Enter to continue...")


def _list_devices(devices: list[Device]) -> None:
    for index, device in enumerate(devices, start=1):
        print(f"  {index}. {device.name}")


def _prompt_device_index(prompt: str, count: int) -> int:
    selection = input(prompt)
    return parse_menu_choice(selection, min_value=1, max_value=count)


def test_connection(device: Device, adb_path: Path) -> None:
    print(f"\nResolving hostname for {device.name} ({device.hostname})...")
    try:
        ip = resolve_hostname(device.hostname)
    except HostnameResolutionError as exc:
        print(f"ERROR: {exc}")
        return

    print(f"Resolved to IP: {ip}")
    print(f"\nConnecting to {device.name} ({device.hostname} - {ip})...")

    try:
        connect_and_verify(adb_path, device.hostname)
        print(f"Successfully connected to {device.name}!")
    except AdbError as exc:
        print(f"ERROR: {exc}")
        return

    print("\nDisconnecting...")
    disconnect(adb_path, device.hostname)
    print("Disconnected successfully.")


def run_propagate_flow(devices: list[Device]) -> None:
    print("\nAvailable devices:\n")
    _list_devices(devices)

    try:
        src_index = _prompt_device_index(
            f"\nSelect SOURCE device (1-{len(devices)}): ", len(devices)
        )
        dst_index = _prompt_device_index(
            f"Select DESTINATION device (1-{len(devices)}): ", len(devices)
        )
    except ValueError as exc:
        print(f"\nERROR: {exc}")
        return

    if src_index == dst_index:
        print("\nERROR: Source and destination cannot be the same device")
        return

    src = devices[src_index - 1]
    dst = devices[dst_index - 1]

    print("\nResolving hostnames...")
    try:
        print(f"Resolving source: {src.name} ({src.hostname})...")
        src_ip = resolve_hostname(src.hostname)
        print(f"  Resolved to: {src_ip}")

        print(f"Resolving destination: {dst.name} ({dst.hostname})...")
        dst_ip = resolve_hostname(dst.hostname)
        print(f"  Resolved to: {dst_ip}")
    except HostnameResolutionError as exc:
        print(f"\nERROR: {exc}")
        return

    print(f"\nPropagating Kodi settings from {src.name} to {dst.name}...\n")
    try:
        propagate_kodi(src_ip, dst_ip)
        print("\nPropagation completed successfully!")
    except (AdbError, ValueError, OSError) as exc:
        print(f"\nERROR: Propagation failed: {exc}")


def main_menu(root: Path | None = None) -> int:
    root = root or project_root()

    try:
        ensure_adb(root)
        devices = load_devices(config_ini_path(root))
    except (AdbError, FileNotFoundError, ValueError) as exc:
        print(f"ERROR: {exc}")
        return 1

    adb_path = adb_executable(root)

    while True:
        _clear_screen()
        print(
            "\n========================================\n"
            "   Kodi Configuration Manager\n"
            "========================================\n\n"
            "Available devices:\n"
        )
        _list_devices(devices)
        print(
            "\nOptions:\n"
            "  1. Test connection to a device\n"
            "  2. Propagate Kodi config between devices\n"
            "  3. Exit\n"
        )

        choice = input("\nSelect an option (1-3): ").strip()

        if choice == "1":
            print(
                "\n========================================\n"
                "   Test Connection\n"
                "========================================\n\n"
                "Available devices:\n"
            )
            _list_devices(devices)
            try:
                index = _prompt_device_index(
                    f"\nSelect a device to test (1-{len(devices)}): ",
                    len(devices),
                )
            except ValueError as exc:
                print(f"\nERROR: {exc}")
                time.sleep(2)
                continue

            test_connection(devices[index - 1], adb_path)
            _pause()

        elif choice == "2":
            print(
                "\n========================================\n"
                "   Propagate Kodi Config\n"
                "========================================\n"
            )
            run_propagate_flow(devices)
            _pause()

        elif choice == "3":
            print("\nGoodbye!")
            return 0

        else:
            print("\nInvalid choice. Please try again.")
            time.sleep(2)


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]

    if len(argv) == 2:
        try:
            propagate_kodi(argv[0], argv[1])
            return 0
        except (AdbError, ValueError, OSError) as exc:
            print(f"ERROR: {exc}")
            return 1

    return main_menu()


if __name__ == "__main__":
    raise SystemExit(main())
