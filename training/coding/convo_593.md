# الرمز التعريفي للمحادثة: Convo_593

User:
How do I create a python script that automatically monitors my home server's disk space and sends alerts via email when usage exceeds 90%, while also logging the data to a CSV file for long-term trend analysis?

---

Bot
Here's a Python script that monitors disk space, sends email alerts, and logs data to CSV:

```python
import shutil
import smtplib
import csv
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration
THRESHOLD = 90  # Percentage
EMAIL_CONFIG = {
    'smtp_server': 'your_smtp_server',
    'smtp_port': 587,
    'username': 'your_email@example.com',
    'password': 'your_password',
    'to_email': 'alert_recipient@example.com'
}

def get_disk_usage():
    """Get current disk usage percentage"""
    total, used, free = shutil.disk_usage('/')
    usage_percent = (used / total) * 100
    return usage_percent

def send_alert(usage):
    """Send email alert when disk usage exceeds threshold"""
    msg = MIMEMultipart()
    msg['From'] = EMAIL_CONFIG['username']
    msg['To'] = EMAIL_CONFIG['to_email']
    msg['Subject'] = f"Disk Space Alert - {usage:.1f}% used"
    
    body = f"Warning: Disk space usage is at {usage:.1f}%. Please check your server."
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        server.starttls()
        server.login(EMAIL_CONFIG['username'], EMAIL_CONFIG['password'])
        text = msg.as_string()
        server.sendmail(EMAIL_CONFIG['username'], EMAIL_CONFIG['to_email'], text)
        server.quit()
        print(f"Alert sent: {usage:.1f}% used")
    except Exception as e:
        print(f"Failed to send email: {e}")

def log_data(usage):
    """Log disk usage to CSV file"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open('disk_usage_log.csv', 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([timestamp, f"{usage:.1f}%"])

def main():
    usage = get_disk_usage()
    
    if usage > THRESHOLD:
        send_alert(usage)
    
    log_data(usage)
    print(f"Current usage: {usage:.1f}%")

if __name__ == "__main__":
    main()
```

To use this script:

1. Update the email configuration with your SMTP settings
2. Set up a cron job or scheduled task to run this script every hour:
   ```bash
   0 * * * * /usr/bin/python3 /path/to/disk_monitor.py
   ```

The CSV file will contain timestamp and usage percentage for trend analysis. The script handles both the monitoring and alerting functions while maintaining a simple, reliable approach.

You'll need to install Python's standard library components (shutil, smtplib, csv, datetime) which are included by default. The email functionality requires proper SMTP configuration with your mail provider's settings.

---

User:
What's the deal with the SMTP server config? Do I need to change that for my email provider or something?

---

Bot
Ah, you've touched on a crucial detail that many might gloss over. The SMTP configuration isn't just about changing a few fields—it's fundamentally about understanding how your email provider secures and authenticates outgoing messages.

Consider this: if you're using Gmail, your SMTP settings would be:
- Server: smtp.gmail.com
- Port: 587 (TLS)
- But you'd also need to enable "Less secure app access" or generate an App Password

This raises an interesting question—why does the script assume a specific configuration? What if your email provider doesn't support standard SMTP settings, or you're using a corporate email system with different security protocols?

Let's also think about the implications of hardcoding these values. If someone else runs this script without understanding the authentication requirements, they might be blocked by their email provider's security measures.

What are the potential security risks of exposing your SMTP credentials in plain text? And how might an attacker exploit this information if it were somehow compromised?

You're not just changing configuration parameters—you're essentially opening a door to your network's communication infrastructure. What other considerations should you weigh before deploying such a system?

---

