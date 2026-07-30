import os
from jinja2 import Environment, FileSystemLoader

def render_newsletter(data: dict) -> str:
    """
    수집된 데이터를 받아 HTML 뉴스레터 템플릿을 렌더링합니다.
    """
    # 현재 파일의 디렉토리 경로
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Jinja2 환경 설정
    env = Environment(loader=FileSystemLoader(current_dir))
    template = env.get_template('newsletter.html')
    
    # 렌더링
    rendered_html = template.render(data=data)
    return rendered_html
