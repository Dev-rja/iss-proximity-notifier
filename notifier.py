# notifier.py
import platform
import subprocess

def notify(title, message):
    """
    Send a desktop notification.
    Works on Windows, macOS, and Linux.
    Falls back to a console beep if no GUI is available.
    """
    system = platform.system()

    try:
        if system == "Darwin":   # macOS
            subprocess.run([
                "osascript", "-e",
                f'display notification "{message}" with title "{title}"'
            ])
        elif system == "Linux":
            subprocess.run(["notify-send", title, message])
        elif system == "Windows":
            # requires: pip install plyer
            from plyer import notification
            notification.notify(title=title, message=message, timeout=10)
        else:
            print(f"\a[ALERT] {title}: {message}")  # terminal bell
    except Exception as e:
        print(f"[NOTIFY] {title}: {message} (GUI notification failed: {e})")
