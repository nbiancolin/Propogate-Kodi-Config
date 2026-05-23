# Propogate-Kodi-Config

Windows utility to clone Kodi configs between Fire TV sticks over ADB.

The Python version is the recommended entry point: core logic is separated from the interactive menu so it can be unit-tested without hardware.

## Prerequisites

- Windows 10 or 11
- Python 3.10 or newer (only if running from source; not needed for the pre-built exe)
- Fire TV devices with **ADB debugging** enabled (Settings → My Fire TV → Developer Options)
- Devices reachable on your network (hostname or IP in `config.ini`)

## Setup

1. Copy `config.ini.sample` to `config.ini` and add your devices under `[firesticks]`:

   ```ini
   [firesticks]
   LivingRoom=android-4
   Basement=192.168.1.50
   ```

   Use a network hostname (e.g. `android-4`) or an IP address. Hostnames are resolved automatically.

2. Create and activate a virtual environment, then install dependencies:

   ```powershell
   cd path\to\Propogate-Kodi-Config
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements-dev.txt
   pip install -e .
   ```

   The Python package lives under `src/kodi_config/` only (there is no duplicate at the repo root).

   Place `config.ini` in the **repository root** (next to `main.py`), not under `src/`.

   On first run, platform-tools are downloaded to **`adb/` in the repository root** (next to `main.py`), not under `src/`. A temporary `temp/` folder for transfers is also created at the root during propagation.

## Pre-built Windows exe

Tagged releases (`v*`, e.g. `v1.0.0`) publish `Propogate-Kodi-Config.exe` on the [Releases](https://github.com/nbiancolin/Propogate-Kodi-Config/releases) page. CI builds on every push to `main` as well; download artifacts from **Actions** → latest run → **Propogate-Kodi-Config-windows**.

### Configuration (exe)

The exe reads **`config.ini` from the same folder as the executable** at runtime (not from inside the exe or a system directory). Edit that file any time; changes apply on the next launch.

1. Download the release zip or exe (the zip includes `config.ini.sample`).
2. Put `Propogate-Kodi-Config.exe` in a folder you control (e.g. `C:\Tools\Propogate-Kodi-Config\`).
3. Copy `config.ini.sample` to **`config.ini` in that same folder** and add your Fire TV devices.
4. Run `Propogate-Kodi-Config.exe`.

On first run, platform-tools download to **`adb/` next to the exe**. A `temp/` folder may appear during propagation and is removed afterward.

### Publishing a release

From a commit on `main`:

```powershell
git tag v1.0.0
git push origin v1.0.0
```

GitHub Actions runs tests, builds the exe, and attaches it to a new GitHub Release for that tag.

## Running from source

With the virtual environment activated:

### Interactive menu

Run `main.py`. Lists devices from `config.ini` and offers:

1. Test connection to a device  
2. Propagate Kodi config between two devices  
3. Exit  

```powershell
python main.py
```

### Direct propagation (two IPs)

Skips the menu and copies Kodi data from source to destination:

```powershell
python main.py 192.168.1.10 192.168.1.20
```

Hostnames work as well if they resolve on your network:

```powershell
python main.py android-4 android-5
```

### Run tests

No Fire TV or ADB connection required; ADB calls are mocked in tests.

```powershell
pytest
```

Verbose output:

```powershell
pytest -v
```

### Without activating the venv

You can run commands through the venv interpreter directly:

```powershell
.\.venv\Scripts\python.exe main.py
.\.venv\Scripts\pytest.exe
```

## Project layout

| Path | Role |
|------|------|
| `main.py` | CLI entry point when running from source (repo root) |
| `Propogate-Kodi-Config.exe` | Standalone build (same folder layout as repo root for config/data) |
| `config.ini` | Your device list (next to `main.py` or the exe; copy from `config.ini.sample`) |
| `adb/` | Downloaded platform-tools (next to `main.py` or the exe; created on first run) |
| `temp/` | Staging folder during propagation (removed after run) |
| `src/kodi_config/` | Python package source |
| `tests/` | Pytest suite |
