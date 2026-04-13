#!/usr/bin/env python3
"""
God Mode — Model Watcher
Polls LM Studio every 30s. When a new model appears, auto-runs probe.

Run as background daemon:
    nohup python probe_watcher.py &

Or install as LaunchAgent:
    python probe_watcher.py --install-launchagent

Or run once (no loop):
    python probe_watcher.py --once
"""

import asyncio
import aiohttp
import json
import time
import argparse
import subprocess
import sys
from pathlib import Path

LMSTUDIO_BASE = "http://127.0.0.1:1234/v1"
POLL_INTERVAL = 30  # seconds
PROFILES_FILE = Path(__file__).parent / "model_profiles.json"

PLIST_PATH = Path.home() / "Library/LaunchAgents/ai.openclaw.god-mode-watcher.plist"
PLIST_LABEL = "ai.openclaw.god-mode-watcher"


def load_profiles() -> dict:
    if PROFILES_FILE.exists():
        return json.loads(PROFILES_FILE.read_text())
    return {}


async def get_loaded_models() -> list:
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{LMSTUDIO_BASE}/models",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as r:
                if r.status != 200:
                    return []
                data = await r.json()
                return [
                    m["id"] for m in data.get("data", [])
                    if not any(ex in m["id"].lower() for ex in ["embed", "text-embedding"])
                ]
    except Exception:
        return []


async def run_once():
    """Check for new models and probe them."""
    sys.path.insert(0, str(Path(__file__).parent))
    from probe import probe_model, load_profiles, save_profiles

    models = await get_loaded_models()
    if not models:
        return

    profiles = load_profiles()
    new_models = [m for m in models if m not in profiles]

    if not new_models:
        return

    print(f"[god-mode-watcher] {len(new_models)} new model(s) detected: {new_models}")
    for model_id in new_models:
        print(f"[god-mode-watcher] Probing: {model_id}")
        result = await probe_model(model_id, verbose=False)
        profiles[model_id] = result
        save_profiles(profiles)
        print(f"[god-mode-watcher] Result: {model_id} → {result['status']} (technique: {result.get('technique') or 'none'})")


async def watch_loop():
    print(f"[god-mode-watcher] Started — polling LM Studio every {POLL_INTERVAL}s")
    while True:
        try:
            await run_once()
        except Exception as e:
            print(f"[god-mode-watcher] Error: {e}")
        await asyncio.sleep(POLL_INTERVAL)


def install_launchagent():
    script_path = Path(__file__).resolve()
    python_path = sys.executable
    log_path = Path.home() / "Library/Logs/god-mode-watcher.log"

    plist = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>{PLIST_LABEL}</string>
    <key>ProgramArguments</key>
    <array>
        <string>{python_path}</string>
        <string>{script_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>{log_path}</string>
    <key>StandardErrorPath</key>
    <string>{log_path}</string>
</dict>
</plist>
"""
    PLIST_PATH.write_text(plist)
    print(f"Written: {PLIST_PATH}")

    result = subprocess.run(
        ["launchctl", "load", str(PLIST_PATH)],
        capture_output=True, text=True
    )
    if result.returncode == 0:
        print(f"✅ LaunchAgent loaded: {PLIST_LABEL}")
        print(f"   Logs: {log_path}")
    else:
        print(f"⚠️  launchctl load failed: {result.stderr}")
        print("Try manually: launchctl load", PLIST_PATH)


def uninstall_launchagent():
    subprocess.run(["launchctl", "unload", str(PLIST_PATH)], capture_output=True)
    if PLIST_PATH.exists():
        PLIST_PATH.unlink()
        print(f"✅ Removed: {PLIST_PATH}")
    else:
        print("LaunchAgent not found.")


def main():
    parser = argparse.ArgumentParser(description="God Mode Model Watcher")
    parser.add_argument("--once", action="store_true", help="Run once and exit")
    parser.add_argument("--install-launchagent", action="store_true", help="Install as LaunchAgent")
    parser.add_argument("--uninstall-launchagent", action="store_true", help="Remove LaunchAgent")
    args = parser.parse_args()

    if args.install_launchagent:
        install_launchagent()
        return

    if args.uninstall_launchagent:
        uninstall_launchagent()
        return

    if args.once:
        asyncio.run(run_once())
        return

    asyncio.run(watch_loop())


if __name__ == "__main__":
    main()
