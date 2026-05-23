# Propogate-Kodi-Config



Clone Kodi settings between Fire TV sticks on your home network. **Most people should use the pre-built Windows exe** — no Python install required.



---



## How to use the Windows exe



### Step 1 — Download



Get the latest build from **[Releases](https://github.com/nbiancolin/Propogate-Kodi-Config/releases)**.



- Download **`Propogate-Kodi-Config-windows.zip`** (recommended — includes a sample config), or  

- Download **`Propogate-Kodi-Config.exe`** only.



### Step 2 — Put files in one folder



Create a folder anywhere you like, for example:



`C:\Tools\Propogate-Kodi-Config\`



Unzip or copy into that folder so it contains at least:



```

C:\Tools\Propogate-Kodi-Config\

  Propogate-Kodi-Config.exe

  config.ini.sample

```



**Important:** `config.ini` must live in the **same folder as the exe**, not in Downloads, not inside the zip forever, and not in `Program Files` unless you are okay editing config there.



### Step 3 — Create your config



1. Copy `config.ini.sample` → rename the copy to **`config.ini`** (same folder as the exe).

2. Open `config.ini` in Notepad and list your Fire TVs under `[firesticks]`:



   ```ini

   [firesticks]

   LivingRoom=android-4

   Basement=192.168.1.50

   ```



   Use each stick’s network name (e.g. `android-4`) or its IP address. You can edit this file anytime; restart the program to pick up changes.



### Step 4 — Prepare your Fire TVs (once per device)



On each Fire TV: **Settings → My Fire TV → Developer Options → ADB debugging** → **On**.



The TV must be on the same network as your PC.



### Step 5 — Run the program



Double-click **`Propogate-Kodi-Config.exe`**, or from PowerShell:



```powershell

cd C:\Tools\Propogate-Kodi-Config

.\Propogate-Kodi-Config.exe

```



**First run only:** the app downloads Android platform-tools into an `adb` folder next to the exe. You need internet once for that.



### Step 6 — Use the menu



| Option | What it does |

|--------|----------------|

| **1. Test connection** | Connects to one device to check it is reachable and authorized. |

| **2. Propagate Kodi config** | Copies Kodi data from one Fire TV to another (you pick source and destination). |

| **3. Exit** | Closes the program. |



If propagation fails, check that both TVs have ADB debugging on and that you accepted any “Allow USB debugging?” prompt on the TV.



### Troubleshooting



| Problem | What to try |

|---------|-------------|

| `config.ini not found` | Create `config.ini` in the **same folder as the exe** (copy from `config.ini.sample`). |

| Cannot connect to a device | Confirm ADB debugging is on, the TV is on the network, and the name/IP in `config.ini` is correct. |

| “Not authorized” | On the Fire TV, accept the debugging authorization prompt, then run **Test connection** again. |



### What gets created next to the exe



| File or folder | Purpose |

|----------------|---------|

| `config.ini` | **You create this** — your device list |

| `adb\` | Downloaded automatically on first run |

| `temp\` | Used during propagation; removed when finished |



---



## Prerequisites (all users)



- **Windows 10 or 11**

- Fire TV devices with **ADB debugging** enabled

- PCs and Fire TVs on the **same network**



Python is **not** required for the exe.



---



## Running from source (developers)



### Setup



1. Copy `config.ini.sample` to `config.ini` in the repo root and add devices under `[firesticks]` (same format as above).



2. Create a virtual environment and install:



   ```powershell

   cd path\to\Propogate-Kodi-Config

   python -m venv .venv

   .\.venv\Scripts\Activate.ps1

   pip install -r requirements-dev.txt

   pip install -e .

   ```



   Place `config.ini` next to `main.py`. Platform-tools download to `adb/` next to `main.py` on first run.



### Interactive menu



```powershell

python main.py

```



### Direct propagation (two addresses, no menu)



```powershell

python main.py 192.168.1.10 192.168.1.20

python main.py android-4 android-5

```



### Tests



```powershell

pytest

pytest -v

```



Without activating the venv:



```powershell

.\.venv\Scripts\python.exe main.py

.\.venv\Scripts\pytest.exe

```



---



## Building and publishing (maintainers)

The workflow runs **only when you start it** (not on every push).

1. On GitHub, open **Actions** → **Build Windows exe** → **Run workflow** (pick the branch with the commit you want, usually `main`).
2. When the run finishes, open the new entry on [Releases](https://github.com/nbiancolin/Propogate-Kodi-Config/releases). Each run creates a tag on that commit (e.g. `v1.0.0-build.42`, from `pyproject.toml` version + run number) and attaches the exe and zip.
3. Artifacts are also on the workflow run under **Propogate-Kodi-Config-windows**.

**Customize release notes:** edit [`.github/RELEASE_NOTES.md`](.github/RELEASE_NOTES.md) in the repo. That file is copied into every GitHub Release description when you run the workflow.



---



## Project layout



| Path | Role |

|------|------|

| `Propogate-Kodi-Config.exe` | Standalone app — keep `config.ini` beside it |

| `config.ini` | Your device list (copy from `config.ini.sample`) |

| `adb/` | Downloaded platform-tools (created on first run) |

| `temp/` | Staging during propagation (removed after run) |

| `main.py` | Entry point when running from source |

| `src/kodi_config/` | Python package source |

| `tests/` | Pytest suite |


