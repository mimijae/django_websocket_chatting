# django_websocket_chatting

Django와 Channels를 활용하여 구현된 웹소켓 기반의 실시간 채팅 애플리케이션

## 주요 기능

1. **실시간 채팅**: 사용자들 간의 실시간 채팅을 지원
2. **멀티룸 지원**: 다양한 채팅방에서 동시에 채팅 가능


## 시작하기

### 필요 사항

- Python
- Django 
- Django Channels
- Redis (채널 레이어 및 비동기 지원을 위해)

### 설치 및 실행

```bash
# 가상 환경 설정
python -m venv venv

# 가상환경 접속
venv\Scripts\activate

# 필요한 패키지 설치
pip install -r requirements.txt

# DB 마이그레이션
python manage.py migrate

# 서버 실행
python manage.py runserver
```
