import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List
import os

class NewsletterMailer:
    """
    이메일 발송을 담당하는 클래스입니다.
    """
    def __init__(self, smtp_server: str = "smtp.gmail.com", smtp_port: int = 587):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        # 환경변수에서 이메일 계정 정보 가져오기
        self.sender_email = os.getenv("SENDER_EMAIL", "your_email@gmail.com")
        self.sender_password = os.getenv("SENDER_PASSWORD", "your_app_password")

    def send_email(self, recipients: List[str], subject: str, html_content: str) -> bool:
        """
        주어진 HTML 내용을 이메일로 발송합니다.
        실제 발송을 위해서는 SENDER_EMAIL과 SENDER_PASSWORD 환경변수가 세팅되어야 합니다.
        """
        if self.sender_email == "your_email@gmail.com":
            print("[경고] 환경변수에 발신자 이메일(SENDER_EMAIL, SENDER_PASSWORD)이 설정되지 않았습니다.")
            print("--- 발송될 내용 미리보기 ---")
            print(html_content[:500] + "\n... (생략)")
            return False

        try:
            # 이메일 메시지 구성
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.sender_email
            msg['To'] = ", ".join(recipients)

            # HTML 내용 첨부
            part = MIMEText(html_content, 'html')
            msg.attach(part)

            # SMTP 서버 연결 및 발송
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, recipients, msg.as_string())
            
            print(f"[성공] {len(recipients)}명의 수신자에게 메일을 발송했습니다.")
            return True
        except Exception as e:
            print(f"[실패] 이메일 발송 중 오류가 발생했습니다: {e}")
            return False
