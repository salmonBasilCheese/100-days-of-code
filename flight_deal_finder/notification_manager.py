from email.mime.text import MIMEText
import os
import smtplib
import requests


class NotificationManager:
    """Discord Webhook および SMTP メールによるディール配信を行うクラス。"""

    def __init__(self) -> None:
        self.webhook_url = os.environ.get("DISCORD_WEBHOOK_URL")
        self.smtp_email = os.environ.get("MY_EMAIL")
        self.smtp_password = os.environ.get("MY_EMAIL_PASSWORD")

    def send_deal_alert(self, message: str) -> bool:
        """Discord Webhook へメッセージを送信する。"""
        if not self.webhook_url:
            return False

        try:
            response = requests.post(
                self.webhook_url, json={"content": message}, timeout=10
            )
            response.raise_for_status()
            print("[Success] Discord deal alert dispatched.")
            return True
        except requests.exceptions.RequestException as e:
            print(f"[Error] Failed to send Discord alert: {e}")
            return False

    def send_emails(self, users: list[dict], message_body: str) -> None:
        """登録顧客リスト全員に個別のメールを配信する。"""
        if not self.smtp_email or not self.smtp_password:
            print("[Skip] Email credentials not configured in environment.")
            return

        try:
            with smtplib.SMTP("smtp.gmail.com", port=587, timeout=15) as server:
                server.starttls()
                server.login(user=self.smtp_email, password=self.smtp_password)

                for user in users:
                    first_name = user["first_name"]
                    to_email = user["email"]

                    content = f"Hi {first_name}!\n\nWe found an incredible flight deal for you:\n\n{message_body}\n\nHappy travels!"
                    msg = MIMEText(content, "plain", "utf-8")
                    msg["Subject"] = "New Flight Deal Found!"
                    msg["From"] = self.smtp_email
                    msg["To"] = to_email

                    server.sendmail(
                        from_addr=self.smtp_email,
                        to_addrs=to_email,
                        msg=msg.as_string(),
                    )
                    print(f"[Success] Deal email sent to {to_email}")

        except smtplib.SMTPException as e:
            print(f"[Error] SMTP delivery failed: {e}")
