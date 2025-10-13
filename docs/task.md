# Task List: Performance Test Script Converter (Updated)

## 프로젝트 설정 및 환경 구성

### TASK-001: 프로젝트 초기 설정
- [x] Git 저장소 생성
- [x] .gitignore 파일 작성 (Python, IDE 설정, .venv 추가)
- [x] README.md 기본 구조 작성
- [x] LICENSE 파일 추가
- [x] 프로젝트 디렉토리 구조 생성

### TASK-002: Python 가상환경 설정 (.venv)
- [x] Python 3.9+ 설치 확인
- [x] .venv 가상환경 생성
  ```bash
  python -m venv .venv
  ```
- [x] 가상환경 활성화 스크립트 확인
  - Windows: `.venv\Scripts\activate`
  - Mac/Linux: `source .venv/bin/activate`
- [x] 가상환경 활성화 테스트
- [x] pip 업그레이드
  ```bash
  python -m pip install --upgrade pip
  ```
- [x] .gitignore에 .venv/ 추가 확인

### TASK-003: 의존성 패키지 설치
- [x] requirements.txt 파일 작성
  ```
  streamlit>=1.28.0
  lxml>=4.9.0
  pytest>=7.4.0
  pytest-cov>=4.1.0
  black>=23.0.0
  flake8>=6.0.0
  mypy>=1.5.0
  ```
- [ ] 개발 의존성 requirements-dev.txt 작성 (선택사항)
  ```
  pytest>=7.4.0
  pytest-cov>=4.1.0
  black>=23.0.0
  flake8>=6.0.0
  mypy>=1.5.0
  ipython>=8.0.0
  ```
- [x] 가상환경에 패키지 설치
  ```bash
  pip install -r requirements.txt
  ```
- [x] 설치된 패키지 확인
  ```bash
  pip list
  ```
- [x] requirements.txt 동결 (freeze)
  ```bash
  pip freeze > requirements-lock.txt
  ```

### TASK-004: 개발 환경 설정
- [ ] pre-commit hooks 설정 (선택사항)
- [ ] VSCode 설정 파일 작성 (.vscode/settings.json)
  ```json
  {
    "python.defaultInterpreterPath": ".venv/bin/python",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true
  }
  ```
- [ ] PyCharm 설정 (인터프리터를 .venv로 지정)

### TASK-005: 가상환경 문서화
- [ ] README.md에 가상환경 설정 가이드 추가
  ```markdown
  ## 개발 환경 설정
  
  ### 1. 가상환경 생성
  \```bash
  python -m venv .venv
  \```
  
  ### 2. 가상환경 활성화
  - Windows:
    \```bash
    .venv\Scripts\activate
    \```
  - Mac/Linux:
    \```bash
    source .venv/bin/activate
    \```
  
  ### 3. 패키지 설치
  \```bash
  pip install -r requirements.txt
  \```
  ```
- [ ] 가상환경 비활성화 방법 문서화
  ```bash
  deactivate
  ```

### TASK-006: 프로젝트 구조 생성
- [x] `converters/` 디렉토리 및 `__init__.py` 생성
- [x] `parsers/` 디렉토리 및 `__init__.py` 생성
- [x] `generators/` 디렉토리 및 `__init__.py` 생성
- [x] `utils/` 디렉토리 및 `__init__.py` 생성
- [x] `tests/` 디렉토리 및 `__init__.py` 생성
- [x] `assets/` 디렉토리 생성 (로고, 아이콘 등)
- [x] `samples/` 디렉토리 생성 (샘플 파일)

### TASK-007: 가상환경 검증
- [x] Python 버전 확인
  ```bash
  python --version
  ```
- [x] 가상환경 내 pip 위치 확인
  ```bash
  which pip  # Mac/Linux
  where pip  # Windows
  ```
- [x] Streamlit 설치 확인
  ```bash
  streamlit --version
  ```
- [ ] 테스트 Streamlit 앱 실행
  ```bash
  streamlit hello
  ```

---

## Phase 1: 기본 UI 구조 개발

### TASK-101: Streamlit 기본 앱 구조
- [x] `app.py` 파일 생성
- [x] Streamlit 페이지 설정 (title, icon, layout)
- [x] 기본 레이아웃 구성 (헤더, 메인, 푸터)
- [x] 페이지 스타일 CSS 작성
- [x] 가상환경에서 앱 실행 테스트
  ```bash
  streamlit run app.py
  ```

### TASK-102: 헤더 영역 구현
- [x] 애플리케이션 제목 표시
- [x] 부제목 표시
- [x] 로고 이미지 추가 (선택사항)
- [x] 버전 정보 표시

### TASK-103: 변환 방향 선택 UI
- [x] 탭 위젯 구현 (JMeter→LoadRunner / LoadRunner→JMeter)
- [x] 탭 전환 이벤트 핸들러
- [x] 선택된 방향에 따른 UI 상태 관리
- [x] 탭별 안내 메시지 표시

### TASK-104: 파일 업로드 영역 구현
- [x] Streamlit file_uploader 위젯 추가
- [x] 파일 형식 필터 설정 (.jmx, .c)
- [x] Drag & Drop 영역 스타일링
- [x] 업로드된 파일명 표시
- [x] 파일 크기 표시 (MB 단위)
- [x] 파일 삭제 버튼 추가

### TASK-105: 코드 프리뷰 영역 구현
- [x] 2컬럼 레이아웃 생성 (원본 / 변환)
- [x] 원본 코드 표시 영역 (읽기 전용)
- [x] 변환된 코드 표시 영역 (읽기 전용)
- [x] 구문 하이라이팅 적용 (st.code 활용)
- [x] 라인 번호 표시
- [ ] 스크롤 동기화 (선택사항)

### TASK-106: 액션 버튼 구현
- [x] Convert 버튼 생성 및 스타일링
- [x] Download 버튼 생성 및 스타일링
- [x] Clear 버튼 생성 및 스타일링
- [x] 버튼 활성화/비활성화 로직
- [ ] 버튼 클릭 이벤트 핸들러 연결 (다음 단계)

### TASK-107: 로그 및 상태 표시 영역
- [x] 로그 메시지 표시 컨테이너 생성
- [x] 성공 메시지 스타일 (초록색)
- [x] 경고 메시지 스타일 (주황색)
- [x] 오류 메시지 스타일 (빨간색)
- [ ] 진행 상태 표시 (프로그레스 바) (다음 단계)
- [ ] 변환 통계 정보 표시 (다음 단계)

### TASK-108: 전체 UI 통합 및 테스트
- [x] 모든 UI 컴포넌트 통합
- [x] 반응형 레이아웃 테스트
- [x] 다양한 화면 크기에서 테스트
- [x] 브라우저 호환성 테스트

---

## Phase 2: Utility 모듈 개발

### TASK-201: 파일 검증 유틸리티
- [ ] `utils/validators.py` 파일 생성
- [ ] 파일 확장자 검증 함수
- [ ] 파일 크기 검증 함수 (최대 10MB)
- [ ] MIME 타입 검증 함수
- [ ] XML 형식 검증 함수
- [ ] C 파일 구문 검증 함수
- [ ] 악성 코드 패턴 필터링 함수

### TASK-202: 코드 포매팅 유틸리티
- [ ] `utils/formatters.py` 파일 생성
- [ ] C 코드 들여쓰기 함수
- [ ] XML 코드 들여쓰기 함수
- [ ] 구문 하이라이팅 헬퍼 함수
- [ ] 코드 정렬 함수

### TASK-203: 공통 헬퍼 함수
- [ ] `utils/helpers.py` 파일 생성
- [ ] 파일명 생성 함수
- [ ] 타임스탬프 생성 함수
- [ ] 에러 메시지 포매팅 함수
- [ ] 로그 메시지 생성 함수

### TASK-204: 상수 및 설정 파일
- [ ] `utils/constants.py` 파일 생성
- [ ] JMeter 엘리먼트 타입 상수 정의
- [ ] LoadRunner 함수명 상수 정의
- [ ] 파일 확장자 상수 정의
- [ ] 에러 코드 상수 정의

---

## Phase 3: JMeter JMX 파싱 엔진 개발

### TASK-301: JMX 파일 로더
- [ ] `parsers/jmx_parser.py` 파일 생성
- [ ] JMXParser 클래스 정의
- [ ] XML 파일 읽기 함수
- [ ] XML 트리 구조 파싱
- [ ] 인코딩 처리 (UTF-8, EUC-KR 등)
- [ ] 파싱 에러 핸들링

### TASK-302: TestPlan 파싱
- [ ] TestPlan 엘리먼트 추출 함수
- [ ] TestPlan 속성 파싱 (이름, 설명)
- [ ] UserDefinedVariables 추출
- [ ] 전역 설정 파싱

### TASK-303: ThreadGroup 파싱
- [ ] ThreadGroup 엘리먼트 추출 함수
- [ ] 스레드 수 파싱
- [ ] Ramp-up 시간 파싱
- [ ] Loop Count 파싱
- [ ] Scheduler 설정 파싱
- [ ] 중첩된 ThreadGroup 처리

### TASK-304: HTTP Sampler 파싱
- [ ] HTTPSamplerProxy 추출 함수
- [ ] HTTP 메소드 파싱 (GET, POST, PUT, DELETE)
- [ ] 도메인 및 포트 파싱
- [ ] 경로(Path) 파싱
- [ ] Query Parameters 파싱
- [ ] Body Data 파싱
- [ ] Content-Type 파싱

### TASK-305: HTTP Header Manager 파싱
- [ ] HeaderManager 엘리먼트 추출
- [ ] 헤더 키-값 쌍 파싱
- [ ] 다중 헤더 처리
- [ ] 헤더 병합 로직

### TASK-306: Cookie Manager 파싱
- [ ] CookieManager 엘리먼트 추출
- [ ] 쿠키 정책 파싱
- [ ] 쿠키 클리어 설정 파싱

### TASK-307: Assertions 파싱
- [ ] ResponseAssertion 추출
- [ ] 응답 코드 검증 규칙 파싱
- [ ] 응답 본문 검증 규칙 파싱
- [ ] Duration Assertion 파싱

### TASK-308: Timers 파싱
- [ ] ConstantTimer 추출
- [ ] UniformRandomTimer 추출
- [ ] Think Time 계산 로직

### TASK-309: Regular Expression Extractor 파싱
- [ ] RegexExtractor 엘리먼트 추출
- [ ] 변수명 파싱
- [ ] 정규표현식 패턴 파싱
- [ ] Template 파싱
- [ ] Match Number 파싱
- [ ] Default Value 파싱

### TASK-310: JSON Extractor 파싱
- [ ] JSONPostProcessor 엘리먼트 추출
- [ ] JSONPath 표현식 파싱
- [ ] 변수명 파싱
- [ ] Default Value 파싱

### TASK-311: 변수 및 파라미터 파싱
- [ ] ${variable} 형식 변수 추출
- [ ] __P() 함수 파싱
- [ ] CSV Data Set Config 파싱

### TASK-312: 컨트롤러 파싱
- [ ] LoopController 파싱
- [ ] IfController 파싱
- [ ] WhileController 파싱
- [ ] TransactionController 파싱

### TASK-313: JMX 파싱 통합 테스트
- [ ] 단순 JMX 파일 파싱 테스트
- [ ] 복잡한 JMX 파일 파싱 테스트
- [ ] 잘못된 JMX 파일 에러 처리 테스트
- [ ] 대용량 JMX 파일 성능 테스트

---

## Phase 4: LoadRunner C 스크립트 생성기 개발

### TASK-401: LoadRunner 코드 생성기 기본 구조
- [ ] `generators/lr_generator.py` 파일 생성
- [ ] LRGenerator 클래스 정의
- [ ] 코드 템플릿 정의
- [ ] 들여쓰기 관리 로직

### TASK-402: 스크립트 헤더 생성
- [ ] 파일 헤더 주석 생성
- [ ] Include 문 생성 (#include "web_api.h")
- [ ] 전역 변수 선언 생성

### TASK-403: vuser_init() 함수 생성
- [ ] vuser_init() 함수 템플릿
- [ ] 초기화 설정 코드 생성
- [ ] 전역 변수 초기화
- [ ] 로깅 설정

### TASK-404: Action() 함수 생성
- [ ] Action() 함수 템플릿
- [ ] 트랜잭션 시작/종료 코드
- [ ] 메인 로직 코드 배치

### TASK-405: vuser_end() 함수 생성
- [ ] vuser_end() 함수 템플릿
- [ ] 정리(cleanup) 코드 생성

### TASK-406: web_url() 함수 생성
- [ ] GET 요청 변환 로직
- [ ] URL 파라미터 생성
- [ ] 옵션 파라미터 생성 (Resource, Mode 등)
- [ ] LAST 파라미터 추가

### TASK-407: web_submit_data() 함수 생성
- [ ] POST 요청 변환 로직
- [ ] ITEMDATA 배열 생성
- [ ] 폼 데이터 변환
- [ ] EXTRARES 처리

### TASK-408: web_custom_request() 함수 생성
- [ ] PUT/DELETE 메소드 처리
- [ ] JSON Body 처리
- [ ] Custom Headers 처리
- [ ] Method 파라미터 생성

### TASK-409: web_add_header() 함수 생성
- [ ] HTTP 헤더 변환
- [ ] 다중 헤더 처리
- [ ] 특수 문자 이스케이프

### TASK-410: web_set_cookie() 함수 생성
- [ ] 쿠키 설정 코드 생성
- [ ] 쿠키 파라미터 변환

### TASK-411: web_reg_save_param() 함수 생성
- [ ] 정규표현식 → LB/RB 변환
- [ ] JSONPath → JSON 파라미터 변환
- [ ] Ordinal 설정
- [ ] SaveOffset 설정

### TASK-412: web_reg_save_param_json() 함수 생성
- [ ] JSON 추출 로직 변환
- [ ] JSONPath 표현식 변환
- [ ] 배열 인덱스 처리

### TASK-413: lr_think_time() 함수 생성
- [ ] Timer 값 변환
- [ ] 랜덤 Think Time 처리

### TASK-414: 트랜잭션 함수 생성
- [ ] lr_start_transaction() 생성
- [ ] lr_end_transaction() 생성
- [ ] 트랜잭션 이름 설정

### TASK-415: 조건문 및 반복문 생성
- [ ] if 문 생성 (IfController 변환)
- [ ] for 문 생성 (LoopController 변환)
- [ ] while 문 생성

### TASK-416: 변수 처리 코드 생성
- [ ] lr_save_string() 생성
- [ ] lr_eval_string() 사용 처리
- [ ] 파라미터 치환 로직

### TASK-417: 에러 처리 코드 생성
- [ ] lr_error_message() 생성
- [ ] lr_abort() 생성 (Assertion 실패 시)
- [ ] 조건부 에러 처리

### TASK-418: 코드 포매팅 및 최적화
- [ ] 들여쓰기 정리
- [ ] 빈 줄 추가
- [ ] 주석 추가
- [ ] 중복 코드 제거

### TASK-419: LoadRunner 코드 생성 통합 테스트
- [ ] 단순 스크립트 생성 테스트
- [ ] 복잡한 스크립트 생성 테스트
- [ ] 생성된 코드 구문 검증
- [ ] LoadRunner에서 실행 가능 여부 확인

---

## Phase 5: JMeter → LoadRunner 변환기 통합

### TASK-501: 변환기 기본 클래스
- [ ] `converters/base_converter.py` 파일 생성
- [ ] BaseConverter 추상 클래스 정의
- [ ] validate_input() 추상 메소드
- [ ] convert() 추상 메소드
- [ ] generate_output() 추상 메소드

### TASK-502: JMeter→LoadRunner 변환기 클래스
- [ ] `converters/jmeter_to_lr.py` 파일 생성
- [ ] JMeterToLRConverter 클래스 정의
- [ ] BaseConverter 상속

### TASK-503: 변환 파이프라인 구현
- [ ] 파일 검증 단계
- [ ] JMX 파싱 단계
- [ ] 데이터 변환 단계
- [ ] LoadRunner 코드 생성 단계
- [ ] 결과 반환 단계

### TASK-504: HTTP Sampler 변환 로직
- [ ] GET 요청 변환
- [ ] POST 요청 변환
- [ ] PUT/DELETE 요청 변환
- [ ] Query Parameters 처리
- [ ] Body Data 처리

### TASK-505: ThreadGroup 변환 로직
- [ ] ThreadGroup → vuser 구조 변환
- [ ] Loop 설정 반영
- [ ] Ramp-up 주석 처리

### TASK-506: Correlation 변환 로직
- [ ] RegexExtractor → web_reg_save_param
- [ ] JSONExtractor → web_reg_save_param_json
- [ ] 변수 사용처 치환

### TASK-507: Header/Cookie 변환 로직
- [ ] HeaderManager → web_add_header
- [ ] CookieManager → 주석 처리

### TASK-508: Assertion 변환 로직
- [ ] ResponseAssertion → 조건문 + lr_error_message
- [ ] Duration Assertion 처리

### TASK-509: Timer 변환 로직
- [ ] ConstantTimer → lr_think_time
- [ ] RandomTimer → lr_think_time with random

### TASK-510: 변환 로그 생성
- [ ] 변환 성공 항목 로깅
- [ ] 변환 실패 항목 로깅
- [ ] 경고 메시지 로깅
- [ ] 통계 정보 수집

### TASK-511: 변환 결과 검증
- [ ] 생성된 코드 구문 검증
- [ ] 필수 함수 존재 여부 확인
- [ ] 변수 일관성 검증

### TASK-512: End-to-End 변환 테스트
- [ ] 샘플 JMX 파일 10개 준비
- [ ] 각 샘플에 대한 변환 테스트
- [ ] 변환 결과 검증
- [ ] 변환 실패 케이스 처리

---

## Phase 6: Streamlit 앱과 변환기 통합

### TASK-601: 파일 업로드 처리
- [ ] 업로드된 파일 임시 저장
- [ ] 파일 읽기 및 인코딩 처리
- [ ] 파일 내용 검증

### TASK-602: 변환 실행 연결
- [ ] Convert 버튼 클릭 이벤트 처리
- [ ] JMeterToLRConverter 인스턴스 생성
- [ ] 변환 실행 및 결과 수신
- [ ] 에러 핸들링

### TASK-603: 프리뷰 업데이트
- [ ] 원본 코드 표시
- [ ] 변환된 코드 표시
- [ ] 구문 하이라이팅 적용
- [ ] 로딩 스피너 표시

### TASK-604: 다운로드 기능 구현
- [ ] 변환 결과를 파일로 저장
- [ ] download 버튼 활성화
- [ ] 파일명 자동 생성 (원본명_converted.c)
- [ ] Streamlit download_button 연결

### TASK-605: 로그 메시지 표시
- [ ] 변환 로그를 UI에 표시
- [ ] 성공/경고/에러 메시지 스타일링
- [ ] 통계 정보 표시 (변환된 항목 수)

### TASK-606: Clear 기능 구현
- [ ] 업로드 파일 초기화
- [ ] 프리뷰 영역 초기화
- [ ] 로그 메시지 초기화
- [ ] 상태 초기화

### TASK-607: 에러 처리
- [ ] 파일 업로드 에러 표시
- [ ] 파싱 에러 표시
- [ ] 변환 에러 표시
- [ ] 사용자 친화적 에러 메시지

### TASK-608: 성능 최적화
- [ ] 캐싱 적용 (@st.cache_data)
- [ ] 불필요한 재실행 방지
- [ ] 대용량 파일 처리 최적화

---

## Phase 7: LoadRunner C 파싱 엔진 개발

### TASK-701: LoadRunner 파서 기본 구조
- [ ] `parsers/lr_parser.py` 파일 생성
- [ ] LRParser 클래스 정의
- [ ] C 파일 읽기 함수
- [ ] 인코딩 처리

### TASK-702: 함수 추출
- [ ] vuser_init() 함수 추출
- [ ] Action() 함수 추출
- [ ] vuser_end() 함수 추출
- [ ] 사용자 정의 함수 추출

### TASK-703: web_url() 파싱
- [ ] 함수 호출 탐지
- [ ] URL 파라미터 추출
- [ ] 옵션 파라미터 추출
- [ ] 문자열 이스케이프 처리

### TASK-704: web_submit_data() 파싱
- [ ] 함수 호출 탐지
- [ ] URL 파라미터 추출
- [ ] ITEMDATA 배열 파싱
- [ ] Name-Value 쌍 추출

### TASK-705: web_custom_request() 파싱
- [ ] 함수 호출 탐지
- [ ] Method 파라미터 추출
- [ ] Body 파라미터 추출
- [ ] Headers 파라미터 추출

### TASK-706: web_add_header() 파싱
- [ ] 함수 호출 탐지
- [ ] 헤더 문자열 파싱
- [ ] 다중 헤더 처리

### TASK-707: web_reg_save_param() 파싱
- [ ] 함수 호출 탐지
- [ ] 변수명 추출
- [ ] LB/RB 경계 추출
- [ ] Ordinal 추출

### TASK-708: lr_think_time() 파싱
- [ ] 함수 호출 탐지
- [ ] Think Time 값 추출

### TASK-709: 트랜잭션 파싱
- [ ] lr_start_transaction() 탐지
- [ ] lr_end_transaction() 탐지
- [ ] 트랜잭션 이름 추출
- [ ] 중첩 트랜잭션 처리

### TASK-710: 변수 및 파라미터 파싱
- [ ] lr_save_string() 파싱
- [ ] lr_eval_string() 파싱
- [ ] 변수 사용처 추적

### TASK-711: 제어문 파싱
- [ ] if 문 파싱
- [ ] for 문 파싱
- [ ] while 문 파싱
- [ ] switch 문 파싱

### TASK-712: 주석 처리
- [ ] 한 줄 주석 제거 또는 보존
- [ ] 블록 주석 제거 또는 보존
- [ ] Runtime Settings 주석 파싱

### TASK-713: LoadRunner 파싱 통합 테스트
- [ ] 단순 스크립트 파싱 테스트
- [ ] 복잡한 스크립트 파싱 테스트
- [ ] 구문 오류 처리 테스트

---

## Phase 8: JMeter JMX 생성기 개발

### TASK-801: JMX 생성기 기본 구조
- [ ] `generators/jmx_generator.py` 파일 생성
- [ ] JMXGenerator 클래스 정의
- [ ] XML 트리 구조 생성 로직

### TASK-802: TestPlan 생성
- [ ] TestPlan 엘리먼트 생성
- [ ] TestPlan 속성 설정
- [ ] hashTree 엘리먼트 추가

### TASK-803: ThreadGroup 생성
- [ ] ThreadGroup 엘리먼트 생성
- [ ] 스레드 수 설정
- [ ] Ramp-up 시간 설정
- [ ] Loop Count 설정

### TASK-804: HTTPSamplerProxy 생성
- [ ] HTTPSamplerProxy 엘리먼트 생성
- [ ] HTTP 메소드 설정
- [ ] 도메인 설정
- [ ] 경로 설정
- [ ] 파라미터 설정

### TASK-805: HeaderManager 생성
- [ ] HeaderManager 엘리먼트 생성
- [ ] 헤더 컬렉션 생성
- [ ] 개별 헤더 추가

### TASK-806: CookieManager 생성
- [ ] CookieManager 엘리먼트 생성
- [ ] 쿠키 정책 설정

### TASK-807: RegexExtractor 생성
- [ ] RegexExtractor 엘리먼트 생성
- [ ] LB/RB → 정규표현식 변환
- [ ] 변수명 설정
- [ ] Template 설정

### TASK-808: ConstantTimer 생성
- [ ] ConstantTimer 엘리먼트 생성
- [ ] Think Time 설정

### TASK-809: ResponseAssertion 생성
- [ ] ResponseAssertion 엘리먼트 생성
- [ ] 검증 규칙 설정

### TASK-810: XML 포매팅 및 출력
- [ ] XML 들여쓰기 설정
- [ ] XML 선언 추가
- [ ] 인코딩 설정 (UTF-8)
- [ ] 파일 저장 함수

### TASK-811: JMX 생성 통합 테스트
- [ ] 단순 JMX 생성 테스트
- [ ] 복잡한 JMX 생성 테스트
- [ ] JMeter에서 로드 가능 여부 확인

---

## Phase 9: LoadRunner → JMeter 변환기 통합

### TASK-901: 변환기 클래스 생성
- [ ] `converters/lr_to_jmeter.py` 파일 생성
- [ ] LRToJMeterConverter 클래스 정의
- [ ] BaseConverter 상속

### TASK-902: 변환 파이프라인 구현
- [ ] 파일 검증 단계
- [ ] LoadRunner 파싱 단계
- [ ] 데이터 변환 단계
- [ ] JMX 생성 단계
- [ ] 결과 반환 단계

### TASK-903: web_url() 변환 로직
- [ ] web_url() → HTTPSamplerProxy (GET)
- [ ] URL 파싱 및 분해
- [ ] 도메인/경로/파라미터 분리

### TASK-904: web_submit_data() 변환 로직
- [ ] web_submit_data() → HTTPSamplerProxy (POST)
- [ ] ITEMDATA → Body Parameters 변환

### TASK-905: web_custom_request() 변환 로직
- [ ] Method에 따른 HTTPSamplerProxy 생성
- [ ] Body 데이터 변환

### TASK-906: web_add_header() 변환 로직
- [ ] web_add_header() → HeaderManager
- [ ] 헤더 그룹화

### TASK-907: web_reg_save_param() 변환 로직
- [ ] LB/RB → 정규표현식 변환
- [ ] RegexExtractor 생성

### TASK-908: lr_think_time() 변환 로직
- [ ] lr_think_time() → ConstantTimer

### TASK-909: 트랜잭션 변환 로직
- [ ] lr_start/end_transaction() → TransactionController

### TASK-910: 변환 로그 생성
- [ ] 변환 성공 항목 로깅
- [ ] 변환 실패 항목 로깅
- [ ] 경고 메시지 로깅

### TASK-911: End-to-End 변환 테스트
- [ ] 샘플 LoadRunner 스크립트 10개 준비
- [ ] 각 샘플에 대한 변환 테스트
- [ ] 변환 결과 검증

---

## Phase 10: LoadRunner → JMeter UI 통합

### TASK-1001: 탭 전환 로직 업데이트
- [ ] LoadRunner → JMeter 탭 클릭 시 처리
- [ ] 파일 업로드 필터 변경 (.c 파일)
- [ ] UI 레이블 업데이트

### TASK-1002: 변환 실행 연결
- [ ] Convert 버튼 클릭 시 LRToJMeterConverter 호출
- [ ] 변환 실행 및 결과 수신

### TASK-1003: 프리뷰 및 다운로드
- [ ] 원본 C 코드 표시
- [ ] 변환된 JMX 표시 (XML 포맷)
- [ ] 다운로드 파일명 설정 (.jmx)

### TASK-1004: 양방향 전환 테스트
- [ ] JMeter → LoadRunner → JMeter 변환 테스트
- [ ] LoadRunner → JMeter → LoadRunner 변환 테스트

---

## Phase 11: 고급 기능 및 최적화

### TASK-1101: 샘플 파일 제공
- [ ] 샘플 JMX 파일 5개 작성
- [ ] 샘플 LoadRunner 스크립트 5개 작성
- [ ] "Load Sample" 버튼 추가
- [ ] 샘플 파일 다운로드 기능

### TASK-1102: 변환 옵션 설정
- [ ] 설정 패널 추가 (Sidebar 활용)
- [ ] 코드 포매팅 옵션 (들여쓰기 크기)
- [ ] 주석 포함 여부 옵션
- [ ] 에러 처리 수준 옵션

### TASK-1103: 변환 히스토리
- [ ] 세션 내 변환 이력 저장
- [ ] 이력 목록 표시
- [ ] 이전 변환 결과 다시 보기

### TASK-1104: 비교 기능
- [ ] Diff 뷰 추가 (선택사항)
- [ ] 변환 전후 비교
- [ ] 변경 사항 하이라이트

### TASK-1105: 다크 모드 지원
- [ ] 다크 모드 테마 설정
- [ ] 색상 스키마 전환 버튼

### TASK-1106: 다국어 지원 (선택사항)
- [ ] 한국어/영어 전환 기능
- [ ] UI 텍스트 다국어 처리

### TASK-1107: 성능 최적화
- [ ] 대용량 파일 처리 개선
- [ ] 메모리 사용 최적화
- [ ] 변환 속도 개선

### TASK-1108: 에러 복구 기능
- [ ] 부분 변환 실패 시 계속 진행
- [ ] 변환 가능한 부분만 변환
- [ ] 상세 에러 리포트 생성

---

## Phase 12: 테스트 및 검증

### TASK-1201: 단위 테스트 작성
- [ ] JMXParser 단위 테스트
- [ ] LRParser 단위 테스트
- [ ] LRGenerator 단위 테스트
- [ ] JMXGenerator 단위 테스트
- [ ] Validators 단위 테스트
- [ ] Formatters 단위 테스트
- [ ] 가상환경에서 pytest 실행
  ```bash
  pytest tests/
  ```

### TASK-1202: 통합 테스트 작성
- [ ] JMeterToLRConverter 통합 테스트
- [ ] LRToJMeterConverter 통합 테스트
- [ ] End-to-End 변환 테스트

### TASK-1203: UI 테스트
- [ ] 파일 업로드 테스트
- [ ] 변환 실행 테스트
- [ ] 다운로드 테스트
- [ ] 에러 처리 테스트

### TASK-1204: 성능 테스트
- [ ] 1MB 파일 변환 시간 측정
- [ ] 5MB 파일 변환 시간 측정
- [ ] 10MB 파일 변환 시간 측정
- [ ] 동시 사용자 부하 테스트

### TASK-1205: 호환성 테스트
- [ ] Chrome 브라우저 테스트
- [ ] Firefox 브라우저 테스트
- [ ] Safari 브라우저 테스트
- [ ] Edge 브라우저 테스트

### TASK-1206: 실제 스크립트 검증
- [ ] 변환된 LoadRunner 스크립트를 LoadRunner에서 실행
- [ ] 변환된 JMeter 스크립트를 JMeter에서 실행
- [ ] 실행 결과 비교 및 검증

### TASK-1207: 회귀 테스트
- [ ] 기능 추가 후 기존 기능 테스트
- [ ] 버그 수정 후 전체 테스트 수행

### TASK-1208: 코드 커버리지 확인
- [ ] pytest-cov를 사용한 커버리지 측정
  ```bash
  pytest --cov=. --cov-report=html tests/
  ```
- [ ] 커버리지 80% 이상 목표

---

## Phase 13: 문서화

### TASK-1301: 사용자 가이드 작성
- [ ] README.md 작성
  - 프로젝트 소개
  - 가상환경 설정 방법
  - 의존성 설치 방법
  - 애플리케이션 실행 방법
  - 기본 사용법
- [ ] 스크린샷 추가
- [ ] GIF 데모 생성

### TASK-1302: 기술 문서 작성
- [ ] 아키텍처 문서
- [ ] API 문서 (각 클래스/함수)
- [ ] 변환 로직 상세 설명
- [ ] 매핑 테이블 문서

### TASK-1303: 개발자 가이드 작성
- [ ] 개발 환경 설정 가이드 (가상환경 포함)
- [ ] 코드 컨벤션
- [ ] 기여 가이드 (CONTRIBUTING.md)
- [ ] 테스트 작성 가이드

### TASK-1304: 릴리스 노트 작성
- [ ] CHANGELOG.md 생성
- [ ] 버전별 변경 사항 기록

### TASK-1305: FAQ 작성
- [ ] 자주 묻는 질문 정리
- [ ] 문제 해결 가이드
- [ ] 제한 사항 명시

### TASK-1306: 코드 주석 작성
- [ ] 모든 클래스에 docstring 추가
- [ ] 모든 함수에 docstring 추가
- [ ] 복잡한 로직에 인라인 주석 추가

---

## Phase 14: 배포 및 출시

### TASK-1401: 배포 환경 설정
- [ ] Streamlit Cloud 계정 생성
- [ ] 또는 Docker 이미지 생성
- [ ] 환경 변수 설정
- [ ] requirements.txt 최종 확인

### TASK-1402: CI/CD 파이프라인 구축
- [ ] GitHub Actions 설정
- [ ] 자동 테스트 실행 (가상환경 생성 포함)
- [ ] 자동 배포 설정

### TASK-1403: Docker 컨테이너화 (선택사항)
- [ ] Dockerfile 작성 (가상환경 설정 포함)
  ```dockerfile
  FROM python:3.9-slim
  WORKDIR /app
  COPY requirements.txt .
  RUN python -m venv .venv
  RUN .venv/bin/pip install --no-cache-dir -r requirements.txt
  COPY . .
  CMD [".venv/bin/streamlit", "run", "app.py"]
  ```
- [ ] docker-compose.yml 작성
- [ ] 이미지 빌드 및 테스트

### TASK-1404: 버전 관리
- [ ] 시맨틱 버저닝 적용
- [ ] Git 태그 생성
- [ ] 릴리스 브랜치 관리

### TASK-1405: 베타 테스트
- [ ] 베타 테스터 모집
- [ ] 피드백 수집
- [ ] 버그 수정 및 개선

### TASK-1406: 정식 출시
- [ ] 프로덕션 배포
- [ ] 출시 공지
- [ ] 사용자 지원 채널 오픈

---

## Phase 15: 유지보수 및 개선

### TASK-1501: 버그 트래킹
- [ ] GitHub Issues 설정
- [ ] 버그 리포트 템플릿 작성
- [ ] 버그 우선순위 분류

### TASK-1502: 사용자 피드백 수집
- [ ] 피드백 양식 작성
- [ ] 사용자 인터뷰 진행
- [ ] 개선 사항 도출

### TASK-1503: 기능 개선
- [ ] 변환 정확도 개선
- [ ] 성능 최적화
- [ ] UI/UX 개선

### TASK-1504: 신규 기능 추가
- [ ] 사용자 요청 기능 검토
- [ ] 우선순위 설정
- [ ] 개발 및 배포

### TASK-1505: 보안 업데이트
- [ ] 의존성 패키지 업데이트
  ```bash
  pip list --outdated
  pip install --upgrade <package_name>
  pip freeze > requirements.txt
  ```
- [ ] 보안 취약점 스캔
- [ ] 패치 적용

### TASK-1506: 문서 업데이트
- [ ] 신규 기능 문서화
- [ ] 변경 사항 반영
- [ ] FAQ 업데이트

### TASK-1507: 가상환경 관리
- [ ] 주기적인 패키지 업데이트
- [ ] requirements.txt 동기화
- [ ] 불필요한 패키지 제거

---

## 마일스톤

### Milestone 0: 환경 설정 완료 (3일)
- TASK-001 ~ TASK-007

### Milestone 1: 프로젝트 설정 완료 (1주)
- TASK-006 (프로젝트 구조)

### Milestone 2: 기본 UI 완성 (2주)
- TASK-101 ~ TASK-108

### Milestone 3: JMeter 파싱 완료 (3주)
- TASK-201 ~ TASK-204, TASK-301 ~ TASK-313

### Milestone 4: LoadRunner 생성기 완료 (3주)
- TASK-401 ~ TASK-419

### Milestone 5: JMeter → LoadRunner 변환 완성 (2주)
- TASK-501 ~ TASK-512, TASK-601 ~ TASK-608

### Milestone 6: LoadRunner → JMeter 변환 완성 (3주)
- TASK-701 ~ TASK-713, TASK-801 ~ TASK-811, TASK-901 ~ TASK-911, TASK-1001 ~ TASK-1004

### Milestone 7: 고급 기능 및 최적화 (2주)
- TASK-1101 ~ TASK-1108

### Milestone 8: 테스트 완료 (2주)
- TASK-1201 ~ TASK-1208

### Milestone 9: 문서화 완료 (1주)
- TASK-1301 ~ TASK-1306

### Milestone 10: 정식 출시 (1주)
- TASK-1401 ~ TASK-1406

---

## 우선순위 레이블

- **P0 (Critical)**: 핵심 기능, 반드시 구현 필요
- **P1 (High)**: 중요 기능, 1차 출시에 포함
- **P2 (Medium)**: 개선 기능, 2차 업데이트에 포함
- **P3 (Low)**: 부가 기능, 추후 개발 고려

### P0 Tasks
- **TASK-001 ~ TASK-007** (프로젝트 및 가상환경 설정) ⭐
- TASK-101 ~ TASK-108 (기본 UI)
- TASK-301 ~ TASK-313 (JMX 파싱)
- TASK-401 ~ TASK-419 (LoadRunner 생성)
- TASK-501 ~ TASK-512 (JMeter → LoadRunner 변환)
- TASK-601 ~ TASK-608 (UI 통합)

### P1 Tasks
- TASK-201 ~ TASK-204 (Utility)
- TASK-701 ~ TASK-713 (LoadRunner 파싱)
- TASK-801 ~ TASK-811 (JMX 생성)
- TASK-901 ~ TASK-911 (LoadRunner → JMeter 변환)
- TASK-1001 ~ TASK-1004 (양방향 UI)
- TASK-1201 ~ TASK-1208 (테스트)
- TASK-1301 ~ TASK-1306 (문서화)

### P2 Tasks
- TASK-1101 ~ TASK-1104 (고급 기능)
- TASK-1401 ~ TASK-1406 (배포)

### P3 Tasks
- TASK-1105 ~ TASK-1108 (최적화 및 부가 기능)
- TASK-1501 ~ TASK-1507 (유지보수)

---

## 가상환경 관련 주요 명령어 요약

```bash
# 가상환경 생성
python -m venv .venv

# 가상환경 활성화
# Windows
.venv\Scripts\activate
# Mac/Linux
source .venv/bin/activate

# 패키지 설치
pip install -r requirements.txt

# 패키지 업데이트
pip install --upgrade <package_name>

# 설치된 패키지 확인
pip list

# requirements.txt 생성
pip freeze > requirements.txt

# 가상환경 비활성화
deactivate

# Streamlit 앱 실행
streamlit run app.py

# 테스트 실행
pytest tests/

# 코드 커버리지 확인
pytest --cov=. --cov-report=html tests/
```

---

**문서 버전**: 1.1 (가상환경 추가)  
**작성일**: 2025-10-13  
**업데이트**: 2025-10-13  
**총 Task 수**: 155+  
**예상 개발 기간**: 16-20주
