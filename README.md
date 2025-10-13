# Performance Test Script Converter (PTSC)

성능 테스트 스크립트를 JMeter와 LoadRunner 간 양방향 변환하는 웹 기반 도구입니다.

## 주요 기능

- **JMeter → LoadRunner 변환**: JMX 파일을 LoadRunner C 스크립트로 변환
- **LoadRunner → JMeter 변환**: LoadRunner C 스크립트를 JMX 파일로 변환
- **직관적인 웹 UI**: Streamlit 기반의 사용하기 쉬운 인터페이스
- **코드 프리뷰**: 변환 전후 코드를 나란히 비교
- **변환 로그**: 상세한 변환 과정 및 경고 메시지 제공

## 개발 환경 설정

### 1. 가상환경 생성

```bash
python -m venv .venv
```

### 2. 가상환경 활성화

**Windows:**
```bash
.venv\Scripts\activate
```

**Mac/Linux:**
```bash
source .venv/bin/activate
```

### 3. 패키지 설치

```bash
pip install -r requirements.txt
```

## 실행 방법

```bash
streamlit run app.py
```

브라우저에서 자동으로 `http://localhost:8501`이 열립니다.

## 테스트 실행

```bash
# 모든 테스트 실행
pytest tests/

# 커버리지와 함께 실행
pytest --cov=. --cov-report=html tests/
```

## 프로젝트 구조

```
PTSC/
├── app.py                  # Streamlit 메인 애플리케이션
├── requirements.txt        # Python 의존성 패키지
├── converters/            # 변환기 모듈
├── parsers/               # 파싱 엔진
├── generators/            # 코드 생성기
├── utils/                 # 유틸리티 함수
├── tests/                 # 테스트 코드
└── samples/               # 샘플 파일
```

## 기술 스택

- **Python 3.9+**
- **Streamlit**: 웹 UI 프레임워크
- **lxml**: XML 파싱
- **pytest**: 테스트 프레임워크

## 라이선스

MIT License

## 기여하기

이슈와 풀 리퀘스트를 환영합니다!

## 문의

프로젝트 관련 문의사항은 이슈를 등록해주세요.
