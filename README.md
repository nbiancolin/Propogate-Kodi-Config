# Propogate-Kodi-Config

Windows utility to clone Kodi configs between Fire TV sticks over ADB.

The Python version is the recommended entry point: core logic is separated from the interactive menu so it can be unit-tested without hardware.

## Prerequisites

- Windows with Python 3.10 or newer
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
   ```

   On first run, platform-tools are downloaded into `adb/` (same behavior as the legacy batch scripts).

## Running

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
| `main.py` | CLI entry point |
| `kodi_config/config.py` | Parse `config.ini`, validate menu input |
| `kodi_config/adb.py` | ADB download, DNS resolve, connect/pull/push |
| `kodi_config/propagate.py` | Source → temp → destination transfer |
| `kodi_config/cli.py` | Interactive menu |
| `tests/` | Pytest suite |
