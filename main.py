import csv
import io
import os
import re
from datetime import datetime
import requests

from templates import render_newsletter
from mailer import NewsletterMailer

# 구글 폼 응답이 실제 저장되는 구글 스프레드시트 ID 및 탭 GID 목록
GOOGLE_SHEET_ID = os.getenv(
    "GOOGLE_SHEET_ID",
    "1fF_a3IyWbuJqu1xhzxpNBqpfl7FYzHuz_nFwFi_0MVU"
)

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")


def fetch_subscribers_from_google_sheet(sheet_id: str) -> list[str]:
    """구글 스프레드시트(모든 응답 시트 탭 포함)에서 구독자 이메일 목록을 자동으로 가져옵니다."""
    if not sheet_id:
        return []

    # 기본 시트 + '설문지 응답 시트1'(gid=445734083) + '설문지 응답 시트2'(gid=187989430) 모두 스캔
    csv_urls = [
        f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=445734083",
        f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv",
        f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=187989430",
        f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv",
    ]

    found_emails = []
    for url in csv_urls:
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200 and res.text.strip():
                reader = csv.reader(io.StringIO(res.text))
                for row in reader:
                    for cell in row:
                        matches = EMAIL_REGEX.findall(cell.strip())
                        for email in matches:
                            email_lower = email.lower()
                            if email_lower not in found_emails:
                                found_emails.append(email_lower)
        except Exception as e:
            print(f"구글 시트 구독자 조회 중 오류 ({url}): {e}")

    return found_emails


def main():
    print(f"[{datetime.now()}] 뉴스레터 생성을 시작합니다...")

    from scrapers import (
        MetScraper, TateScraper, LouvreScraper, NationalGalleryScraper, VAMScraper,
        LACMAScraper, WhitneyScraper, MoriScraper, NMKScraper, ChicagoScraper
    )

    # 10대 미술관 목록 (총 10개)
    scraper_classes = [
        MetScraper, TateScraper, LouvreScraper, NationalGalleryScraper, VAMScraper,
        LACMAScraper, WhitneyScraper, MoriScraper, NMKScraper, ChicagoScraper
    ]
    newsletter_data = {}
    for ScraperCls in scraper_classes:
        scraper = ScraperCls()
        print(f"{scraper.museum_name} 전시 정보 수집 중...")
        try:
            exhibitions = scraper.get_exhibitions()
            if exhibitions:
                newsletter_data[scraper.museum_name] = exhibitions
                print(f" -> {len(exhibitions)}개 전시 정보 수집 완료.")
            else:
                print(" -> 수집된 전시가 없거나 파싱에 실패했습니다.")
        except Exception as e:
            print(f" -> 수집 실패 (오류: {e})")

    # 3. HTML 렌더링
    print("HTML 렌더링 중...")
    html_content = render_newsletter(data=newsletter_data)

    # 검증을 위해 로컬에 HTML 파일로도 저장
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preview.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"미리보기 파일 생성 완료: {output_path}")

    # 4. 이메일 발송 (기본 이메일 + 구글 스프레드시트 구독자 통합)
    print("이메일 발송 준비 중...")
    mailer = NewsletterMailer()

    # 환경변수에서 기본 수신자 목록 가져오기
    receiver_email = os.getenv("RECEIVER_EMAIL", "nifi2025yes@gmail.com")
    base_subscribers = [e.strip().lower() for e in receiver_email.split(",") if e.strip()]

    # 구글 시트에서 신청자 이메일 실시간 가져오기
    sheet_subscribers = fetch_subscribers_from_google_sheet(GOOGLE_SHEET_ID)
    print(f"구글 시트에서 불러온 구독자 수: {len(sheet_subscribers)}명 -> {sheet_subscribers}")

    # 중복 제거하여 전체 구독자 리스트 완성
    subscribers = list(dict.fromkeys(base_subscribers + sheet_subscribers))
    print(f"최종 발송 대상 구독자 ({len(subscribers)}명): {subscribers}")

    subject = f"🏛️ 세계 10대 미술관 주간 전시 뉴스레터 ({datetime.now().strftime('%Y-%m-%d')})"

    success = mailer.send_email(
        recipients=subscribers,
        subject=subject,
        html_content=html_content
    )

    if success:
        print("모든 작업 완료!")
    else:
        print("작업 완료 (이메일 발송은 생략되거나 콘솔 미리보기로 대체되었습니다).")


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    main()
