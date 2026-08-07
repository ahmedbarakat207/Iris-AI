# الرمز التعريفي للمحادثة: Convo_368

User:
How do I create a simple Python script to monitor my home server's disk space and send alerts when it goes below 10%?

---

Bot
Here's a simple Python script to monitor your disk space and alert when it drops below 10%:

```python
import shutil
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def check_disk_space():
    # Check root filesystem (or specify your server's disk)
    total, used, free = shutil.disk_usage("/")
    
    # Calculate percentage used
    percent_used = (used / total) * 100
    
    if percent_used > 90:  # Alert when space drops below 10%
        send_alert(percent_used, free)
    
    return percent_used, free

def send_alert(percentage, free_space):
    # Configure email settings
    sender_email = "your_email@gmail.com"
    sender_password = "your_app_password"
    recipient_email = "your_email@gmail.com"
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = "Low Disk Space Alert"
    
    body = f"""
    Your server is running low on disk space!
    
    Current usage: {percentage:.1f}%
    Free space: {free_space // (1024**3)} GB
    
    Please take action to free up space.
    """
    
    msg.attach(MIMEText(body, 'plain'))
    
    # Send email
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        server.quit()
        print("Alert sent successfully")
    except Exception as e:
        print(f"Failed to send alert: {e}")

# Run the check
if __name__ == "__main__":
    percent, free = check_disk_space()
    print(f"Disk usage: {percent:.1f}% ({free // (1024**3)} GB free)")
```

To use this script:

1. Replace the email settings with your actual credentials
2. Set up an app password for Gmail or modify for your email provider
3. Run it manually to test, then set up a cron job for automated checks

For automation, add to crontab:
```bash
# Check every hour
0 * * * * /usr/bin/python3 /path/to/disk_monitor.py
```

The script will alert you when your disk space drops below 10%. Adjust the threshold as needed or modify the email settings for your preferred notification method.

---

User:
What's the deal with the email stuff? Do I really need to set up a Gmail account just to get alerts? Can't I just have it log to a file or something?

---

Bot
Ah, a thoughtful question that cuts to the heart of practical implementation versus theoretical elegance. You're absolutely right to question the email dependency—this script does assume a certain level of infrastructure that might not be necessary for your use case.

Let's explore why the email approach was chosen and whether there are better alternatives:

First, you could indeed log to a file instead. But consider this: if you're monitoring a server, what happens when the disk space is so low that even logging becomes problematic? What if your system is unreachable via network but still running?

What if we shift our focus from "alerting" to "detecting"? Instead of email, could we use simpler methods like:
- Writing to a log file in a separate location (like /var/log/)
- Triggering a systemd alert or notification
- Using a simple HTTP POST to a monitoring service

And here's the more provocative question: What if we're overcomplicating this? The script assumes you want immediate email alerts, but what if the real issue is not about sending alerts at all, but about understanding your actual usage patterns?

What are the potential trade-offs in terms of system reliability when the alert mechanism itself might fail due to the very condition it's trying to monitor?

---

