# ClickLock for Windows

ClickLock lets you highlight, drag, and scroll without holding the mouse button down. You click and hold briefly to "lock" the button, move the mouse, then click again to release. It's built into every copy of Windows — this script just turns it on.

## Why would I want this?

- **Hand or wrist strain.** Holding down the mouse button while dragging is one of the most tiring mouse actions. ClickLock removes it.
- **Selecting large blocks of text.** Lock the click, scroll down as far as you need, click to finish. No death grip required.
- **Drag and drop.** Lock, move the file, click to drop. Much more relaxed.

## Why use this script instead of a third-party app?

This script does not install any software. It flips a single Windows setting — the same one you can find buried in **Settings > Devices > Mouse > Additional mouse options > ClickLock**. The script just saves you the trip through five menus.

No background processes, no tray icons, no auto-updater, no account sign-up, no unknown code running on your machine. It's 15 lines that change one setting and tell Windows to apply it.

## How to use it

### 1. Download the script

Save `enable_clicklock.ps1` somewhere on your computer (e.g. your Desktop or Downloads folder).

### 2. Open PowerShell

Press **Win + S**, type **PowerShell**, and open **Windows PowerShell**.

### 3. Run the script

Navigate to where you saved the file and run it:

```powershell
cd ~\Downloads
.\enable_clicklock.ps1
```

If you get an error about "execution policy", run this first (one-time step):

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then try again.

### 4. (Optional) Set the hold time

By default, Windows uses its own hold duration. If you want to set how long you hold before the click locks (in milliseconds), pass it as an argument:

```powershell
.\enable_clicklock.ps1 -LockTime 500
```

Lower numbers mean a shorter hold. 200–600 ms is a good range to experiment with.

## How to turn it off

Open **Settings > Devices > Mouse > Additional mouse options** and uncheck **Turn on ClickLock**. Or run this in PowerShell:

```powershell
reg add "HKCU\Control Panel\Mouse" /v MouseClickLock /t REG_SZ /d 0 /f
```

## FAQ

**Does this need admin rights?**
No. It changes a setting in your own user profile.

**Does it survive restarts?**
Yes. It's a registry setting, so it sticks until you change it.

**Can it break anything?**
No. ClickLock is a standard Windows accessibility feature. Turning it off restores normal behavior immediately.
