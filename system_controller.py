# system_controller.py
# ARIS HARDWARE & OS EXECUTION CORE

import subprocess
import os
import psutil
import pyautogui

def get_live_telemetry():
    """Live Battery, CPU, RAM metrics read karta hai"""
    try:
        battery = psutil.sensors_battery()
        batt_str = f"{battery.percent}% ({'Charging' if battery.power_plugged else 'Battery'})" if battery else "AC Line"
        cpu = psutil.cpu_percent(interval=0.2)
        ram = psutil.virtual_memory().percent
        return f"⚡ Telemetry: CPU Load {cpu}%, Memory Usage {ram}%, Power {batt_str}."
    except Exception as e:
        return f"Telemetry read error: {str(e)}"

def execute_os_action(action_tag: str, target: str = ""):
    """Windows commands, apps aur shortcuts execute karta hai"""
    action = action_tag.upper().strip()
    tgt = target.lower().strip()
    
    try:
        # 1. APP LAUNCH PROTOCOLS
        if action == "OPEN_APP":
            if "code" in tgt or "vs" in tgt:
                subprocess.Popen("code", shell=True)
                return "VS Code command matrix launched, Boss."
            elif "chrome" in tgt or "browser" in tgt:
                subprocess.Popen("start chrome", shell=True)
                return "Chrome operational."
            elif "notepad" in tgt:
                subprocess.Popen("notepad", shell=True)
                return "Notepad online."
            elif "calc" in tgt:
                subprocess.Popen("calc", shell=True)
                return "Calculator engaged."
            elif "cmd" in tgt or "terminal" in tgt:
                subprocess.Popen("start cmd", shell=True)
                return "Command terminal initialized."
            else:
                subprocess.Popen(f"start {target}", shell=True)
                return f"App execute attempt sent for: {target}."

        # 2. AUDIO & VOLUME CONTROLS
        elif action == "VOLUME":
            if "mute" in tgt:
                pyautogui.press("volumemute")
                return "Audio systems muted, Boss."
            elif "up" in tgt:
                pyautogui.press("volumeup", presses=5)
                return "Volume increased (+10%)."
            elif "down" in tgt:
                pyautogui.press("volumedown", presses=5)
                return "Volume decreased (-10%)."

        # 3. SCREENSHOT MATRIX
        elif action == "SCREENSHOT":
            os.makedirs("captures", exist_ok=True)
            shot_file = "captures/screen_recon.png"
            pyautogui.screenshot(shot_file)
            return f"Screen captured and saved to {shot_file}."

        # 4. SECURITY LOCKDOWN
        elif action == "LOCK":
            subprocess.run("rundll32.exe user32.dll,LockWorkStation", shell=True)
            return "Terminal locked down under Commander Protocol."

        # 5. HARDWARE STATS
        elif action == "TELEMETRY":
            return get_live_telemetry()

    except Exception as e:
        return f"Hardware execution fault: {str(e)}"
    
    return "Action protocol unmapped."
