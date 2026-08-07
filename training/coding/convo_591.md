# الرمز التعريفي للمحادثة: Convo_591

User:
How can I create a simple Python script to monitor my home server's disk usage and automatically send alerts when it exceeds 85%?

---

Bot
Here's a straightforward Python script to monitor your disk usage and send alerts when it exceeds 85%:

```python
import shutil
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time

def check_disk_usage(path="/"):
    """Check disk usage for the specified path"""
    total, used, free = shutil.disk_usage(path)
    usage_percent = (used / total) * 100
    return usage_percent

def send_alert(subject, message):
    """Send email alert - configure your SMTP settings"""
    # Replace with your email configuration
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = "your_email@gmail.com"
    sender_password = "your_password"
    recipient_email = "alert_recipient@gmail.com"
    
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    
    msg.attach(MIMEText(message, 'plain'))
    
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        server.quit()
        print("Alert sent successfully")
    except Exception as e:
        print(f"Failed to send alert: {e}")

def main():
    threshold = 85.0
    while True:
        try:
            usage = check_disk_usage("/")
            if usage > threshold:
                subject = f"Disk Usage Alert: {usage:.1f}%"
                message = f"Warning: Your disk usage has reached {usage:.1f}%. Please take action to free up space."
                send_alert(subject, message)
            else:
                print(f"Disk usage: {usage:.1f}% - OK")
            
            time.sleep(3600)  # Check every hour
        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(60)  # Wait a minute before retrying

if __name__ == "__main__":
    main()
```

To use this script:

1. Install required packages: `pip install` (no external dependencies beyond standard library)
2. Configure your email settings in the `send_alert` function
3. Adjust the path if monitoring a specific directory instead of root
4. Run with `python disk_monitor.py`

The script checks disk usage every hour and sends an email alert when usage exceeds 85%. You can adjust the frequency or threshold as needed.

For production use, consider:
- Adding logging to track when alerts were sent
- Implementing more sophisticated notification methods (webhooks, SMS)
- Adding error handling for network issues
- Running as a background service with proper process management

The script will run continuously until manually stopped.

---

User:
Oh, so I just need to change the email settings and it'll work right? What if I don't want to use Gmail though? Can I use like, Outlook or something else?

---

Bot
Ah, you're assuming that the script is a plug-and-play solution, but let's examine that assumption more carefully. You're focusing on the email configuration part, but what about the broader implications of this approach?

First, changing the SMTP settings isn't just a matter of swapping out host and port—it's about ensuring compatibility with the authentication protocols of different providers. Outlook, for example, uses different endpoints and may require OAuth2 instead of basic authentication. If you're using Microsoft 365 or Outlook.com, you'd need to adjust both the server address and potentially implement more complex authentication flows.

But here's a more provocative question: Why assume that email is the best form of alerting for a server monitoring system? What if the server itself is running low on resources and can't reliably maintain an SMTP connection? What if your monitoring needs are more sophisticated—perhaps you want to log alerts to a centralized system, send them to Slack, or trigger automated scaling?

The script's design implies that email notifications are sufficient, but consider this: if you're building a production environment, what happens when your alerting system itself becomes a point of failure? The script doesn't account for reliability in the alerting mechanism—what if the network is down or the SMTP server is unreachable?

What other methods of alerting might be more resilient to these failures? And how does the choice of notification medium affect your overall system's robustness and maintainability?

---

