# mailer.py
"""
Sends an email alert via Gmail SMTP when ISS is near CDO.
Requires env vars:
  GMAIL_USER         — your Gmail address (sender)
  GMAIL_APP_PASSWORD — 16-char app password from myaccount.google.com/apppasswords
  ALERT_EMAIL        — recipient email (can be same as GMAIL_USER)
"""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

GMAIL_USER         = os.environ.get("GMAIL_USER", "")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")
ALERT_EMAIL        = os.environ.get("ALERT_EMAIL", "")


def send_iss_alert(distance_km: float, latitude: float, longitude: float,
                   altitude: float, velocity: float, city: str) -> bool:
    """
    Send ISS proximity alert email via Gmail SMTP.
    Returns True if sent successfully, False otherwise.
    """
    if not GMAIL_USER or not GMAIL_APP_PASSWORD or not ALERT_EMAIL:
        print("  [MAILER] Skipping — GMAIL_USER, GMAIL_APP_PASSWORD, or ALERT_EMAIL not set")
        return False

    subject = f"🛰️ ISS is {round(distance_km)} km from {city}!"

    html_body = f"""
    <div style="font-family:monospace;background:#07090f;color:#d0daea;padding:32px;border-radius:8px;max-width:520px">
      <div style="font-size:11px;letter-spacing:0.1em;color:#556278;margin-bottom:8px;text-transform:uppercase">
        ISS Proximity Notifier · Ground Station CDO-01
      </div>
      <div style="font-size:28px;font-weight:700;color:#00e5a0;margin-bottom:4px">
        🛰️ ISS NEARBY
      </div>
      <div style="font-size:14px;color:#3b9eff;margin-bottom:24px">
        The International Space Station is within alert radius!
      </div>

      <table style="width:100%;border-collapse:collapse">
        <tr style="border-bottom:1px solid #1e2d45">
          <td style="padding:10px 0;font-size:11px;color:#556278;text-transform:uppercase;letter-spacing:0.08em">Distance to {city}</td>
          <td style="padding:10px 0;font-size:18px;font-weight:700;color:#00e5a0;text-align:right">{round(distance_km):,} km</td>
        </tr>
        <tr style="border-bottom:1px solid #1e2d45">
          <td style="padding:10px 0;font-size:11px;color:#556278;text-transform:uppercase;letter-spacing:0.08em">Latitude</td>
          <td style="padding:10px 0;font-size:14px;color:#d0daea;text-align:right">{latitude:.2f}°</td>
        </tr>
        <tr style="border-bottom:1px solid #1e2d45">
          <td style="padding:10px 0;font-size:11px;color:#556278;text-transform:uppercase;letter-spacing:0.08em">Longitude</td>
          <td style="padding:10px 0;font-size:14px;color:#d0daea;text-align:right">{longitude:.2f}°</td>
        </tr>
        <tr style="border-bottom:1px solid #1e2d45">
          <td style="padding:10px 0;font-size:11px;color:#556278;text-transform:uppercase;letter-spacing:0.08em">Altitude</td>
          <td style="padding:10px 0;font-size:14px;color:#d0daea;text-align:right">{altitude:.0f} km</td>
        </tr>
        <tr>
          <td style="padding:10px 0;font-size:11px;color:#556278;text-transform:uppercase;letter-spacing:0.08em">Velocity</td>
          <td style="padding:10px 0;font-size:14px;color:#d0daea;text-align:right">{round(velocity):,} km/h</td>
        </tr>
      </table>

      <div style="margin-top:24px;padding:12px 16px;background:#0c1120;border:1px solid #1e2d45;border-left:3px solid #3b9eff;font-size:12px;color:#8892a8">
        Look up at the sky over {city} — the ISS may be visible to the naked eye!
      </div>

      <div style="margin-top:24px;text-align:center">
        <a href="https://iss-proximity-notifier.vercel.app"
           style="display:inline-block;padding:10px 24px;background:#3b9eff;color:#fff;text-decoration:none;font-size:12px;letter-spacing:0.08em;text-transform:uppercase">
          Open Live Tracker ↗
        </a>
      </div>

      <div style="margin-top:24px;font-size:10px;color:#556278;text-align:center">
        ISS Proximity Notifier · Cagayan de Oro, Philippines · 8.48°N 124.65°E
      </div>
    </div>
    """

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = f"ISS Notifier <{GMAIL_USER}>"
        msg["To"]      = ALERT_EMAIL
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            smtp.sendmail(GMAIL_USER, ALERT_EMAIL, msg.as_string())

        print(f"  [MAILER] Alert sent → {ALERT_EMAIL}")
        return True

    except smtplib.SMTPAuthenticationError:
        print("  [MAILER] Auth failed — check GMAIL_USER and GMAIL_APP_PASSWORD")
        return False
    except Exception as e:
        print(f"  [MAILER] Failed to send alert: {e}")
        return False