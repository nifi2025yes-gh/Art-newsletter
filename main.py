import os
from datetime import datetime

from templates import render_newsletter
from mailer import NewsletterMailer

def main():
    print(f"[{datetime.now()}] 뉴스레터 생성을 시작합니다...")

    from scrapers import (
        MetScraper, TateScraper, LouvreScraper, NationalGalleryScraper, VAMScraper,
        LACMAScraper, WhitneyScraper, MoriScraper, NMKScraper, ChicagoScraper
    )
    
    # 10대 미술관 파이프라인 (총 10곳)
    scraper_classes = [
        MetScraper, TateScraper, LouvreScraper, NationalGalleryScraper, VAMScraper,
        LACMAScraper, WhitneyScraper, MoriScraper, NMKScraper, ChicagoScraper
    ]
    newsletter_data = {}
    for ScraperCls in scraper_classes:
        scraper = ScraperCls()
        print(f"{scraper.museum_name} 데이터 수집 중...")
        try:
            exhibitions = scraper.get_exhibitions()
            if exhibitions:
                newsletter_data[scraper.museum_name] = exhibitions
                print(f" -> {len(exhibitions)}개의 전시 정보 수집 완료.")
            else:
                print(" -> 수집된 전시가 없거나 파싱에 실패했습니다.")
        except Exception as e:
            print(f" -> 수집 실패 (오류: {e})")

    # 3. HTML 렌더링
    print("HTML 렌더링 중...")
    html_content = render_newsletter(data=newsletter_data)
    
    # 디버깅을 위해 로컬에 HTML 파일로 저장
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preview.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"미리보기 파일 생성 완료: {output_path}")

    # 4. 이메일 발송
    print("이메일 발송 준비 중...")
    mailer = NewsletterMailer()
    
    # 환경변수에서 구독자 목록 가져오기 (없으면 사용자가 제공한 이메일 사용)
    receiver_email = os.getenv("RECEIVER_EMAIL", "nifi2025yes@gmail.com")
    subscribers = [e.strip() for e in receiver_email.split(",") if e.strip()]
    
    subject = f"🎨 세계 10대 미술관 전시 동향 ({datetime.now().strftime('%Y-%m-%d')})"
    
    success = mailer.send_email(
        recipients=subscribers,
        subject=subject,
        html_content=html_content
    )
    
    if success:
        print("뉴스레터 작업 완료!")
    else:
        print("작업을 완료했지만 이메일 발송은 로컬 콘솔 미리보기로 대체되었습니다.")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    main()
