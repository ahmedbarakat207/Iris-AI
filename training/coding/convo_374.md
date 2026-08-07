# الرمز التعريفي للمحادثة: Convo_374

User:
How can I create a simple Python script to monitor my home server's disk space and send me an alert when it gets below 10%?

---

Bot
Here's a simple Python script to monitor your disk space:

```python
import shutil
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def check_disk_space():
    # Check root partition (adjust path if needed)
    total, used, free = shutil.disk_usage("/")
    
    # Calculate percentage
    percent_free = (free / total) * 100
    
    if percent_free < 10:
        send_alert(percent_free)
    else:
        print(f"Disk space: {percent_free:.1f}% free")
        
def send_alert(percentage):
    # Configure email settings
    smtp_server = "smtp.gmail.com"
    port = 587
    sender_email = "your_email@gmail.com"
    password = "your_app_password"
    recipient_email = "your_email@gmail.com"
    
    # Create message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = recipient_email
    message["Subject"] = "Low Disk Space Alert"
    
    body = f"Warning: Your disk space is only {percentage:.1f}% free. Please take action."
    message.attach(MIMEText(body, "plain"))
    
    # Send email
    try:
        server = smtplib.SMTP(smtp_server, port)
        server.starttls()
        server.login(sender_email, password)
        server.send_message(message)
        server.quit()
        print("Alert sent successfully")
    except Exception as e:
        print(f"Failed to send alert: {e}")

# Run the check
check_disk_space()
```

To use this script:

1. Install Python 3 if you haven't already
2. Set up email credentials (use app passwords for Gmail)
3. Adjust the path in `shutil.disk_usage("/")` if monitoring a different partition
4. Run with `python disk_monitor.py` or set up a cron job to check periodically

The script checks your disk space and sends an email when it drops below 10%. You can adjust the threshold by changing the `10` in the condition. For automated monitoring, you could run this script every hour using a scheduler like cron on Linux or Task Scheduler on Windows.

You'll need to enable two-factor authentication and generate an app password for Gmail, or configure other email settings as needed. The script will print results to the console when it runs, so you can test it first before setting up automated alerts.

---

User:
What's the deal with the email stuff? Do I really need to set up an email for this or can I just get a notification on my computer?

---

Bot
Ah, you're right to question that email dependency—let's examine why it might be problematic and what alternatives exist.

The email approach assumes you want remote notifications, but there are several issues with that assumption. First, what happens when your network is down or your email server fails? You'd miss the alert entirely. Second, email is arguably one of the most error-prone communication methods—authentication failures, spam filters, and delivery delays can all prevent your notification from reaching you.

But here's a more interesting question: Why are we assuming you want a notification at all? What if the real issue isn't just low disk space but also the *implications* of that condition?

Consider this alternative perspective: what if instead of sending an alert, your script simply logged the event and triggered a system sound or desktop notification through your OS's native capabilities? That would be more reliable because it bypasses network issues entirely. It also avoids the complexity of email configuration, which is often where such scripts fail.

What are we actually trying to achieve here? Are we trying to prevent data loss, or are we trying to avoid a system crash? And if we're trying to prevent data loss, what's stopping us from simply having an automated backup process or a disk cleanup routine?

And let's not ignore that there might be other approaches entirely—what about using systemd notifications, logging to a central monitoring system, or even just writing to a simple file that gets monitored by another process? 

What makes you think email is the best solution here rather than something more robust for your specific use case?

---

