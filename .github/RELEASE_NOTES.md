## How to use the Windows exe

### What to download

- **`Propogate-Kodi-Config-windows.zip`** (recommended) — includes `config.ini.sample`
- **`Propogate-Kodi-Config.exe`** — program only

### Step 1 — Put everything in one folder

Create a folder, for example:

`C:\Tools\Propogate-Kodi-Config\`

Unzip or copy files so you have:

```
C:\Tools\Propogate-Kodi-Config\
  Propogate-Kodi-Config.exe
  config.ini.sample
```

**Important:** `config.ini` must be in the **same folder as the exe**.

### Step 2 — Create your config

1. Copy `config.ini.sample` and rename the copy to **`config.ini`**.
2. Open `config.ini` in Notepad and add your Fire TVs:

```ini
[firesticks]
LivingRoom=android-4
Basement=192.168.1.50
```

Use each stick’s network name (e.g. `android-4`) or its IP address. Edit this file anytime; restart the program to pick up changes.

### Step 3 — Prepare your Fire TVs (once per device)

On each Fire TV: **Settings → My Fire TV → Developer Options → ADB debugging** → **On**.

The TV must be on the same network as your PC.

### Step 4 — Run the program

Double-click **`Propogate-Kodi-Config.exe`**, or from PowerShell:

```powershell
cd C:\Tools\Propogate-Kodi-Config
.\Propogate-Kodi-Config.exe
```

**First run only:** the app downloads Android platform-tools into an `adb` folder next to the exe (internet required once).

### Step 5 — Use the menu

| Option | What it does |
|--------|----------------|
| **1. Test connection** | Checks that a device is reachable and authorized. |
| **2. Propagate Kodi config** | Copies Kodi data from one Fire TV to another. |
| **3. Exit** | Closes the program. |

### Troubleshooting

| Problem | What to try |
|---------|-------------|
| `config.ini not found` | Create `config.ini` next to the exe (copy from `config.ini.sample`). |
| Cannot connect | Confirm ADB debugging is on and the name/IP in `config.ini` is correct. |
| “Not authorized” | On the Fire TV, accept the debugging prompt, then run **Test connection** again. |

### Files created next to the exe

| File or folder | Purpose |
|----------------|---------|
| `config.ini` | Your device list (you create this) |
| `adb\` | Downloaded automatically on first run |
| `temp\` | Used during propagation; removed when finished |

### Requirements

- Windows 10 or 11
- Fire TV with **ADB debugging** enabled
- PC and Fire TVs on the **same network**
