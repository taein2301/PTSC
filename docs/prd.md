# PRD: Performance Test Script Converter

## 1. 프로젝트 개요

### 1.1 프로젝트명
**Performance Test Script Converter** (성능테스트 스크립트 변환기)

### 1.2 목적
JMeter JMX 파일과 LoadRunner C 스크립트 간의 양방향 변환을 지원하는 GUI 기반 변환 도구 개발

### 1.3 배경
- 성능 테스트 도구 전환 시 기존 스크립트 재사용 필요성
- 수동 변환 작업의 시간 소모 및 오류 가능성
- 도구 간 스크립트 호환성 부재로 인한 생산성 저하

### 1.4 목표
- JMeter JMX → LoadRunner C 스크립트 변환 (1차 우선순위)
- LoadRunner C 스크립트 → JMeter JMX 변환 (2차 우선순위)
- 직관적인 웹 기반 GUI 제공
- 변환 정확도 95% 이상 달성

---

## 2. 기술 스택

### 2.1 Core Technology
- **언어**: Python 3.9+
- **GUI 프레임워크**: Streamlit
- **XML 파싱**: xml.etree.ElementTree, lxml
- **파일 처리**: pathlib, io

### 2.2 주요 라이브러리
```python
- streamlit >= 1.28.0
- lxml >= 4.9.0
- xml.etree.ElementTree (표준 라이브러리)
- re (정규표현식)
```

---

## 3. 기능 요구사항

### 3.1 1차 우선순위: JMeter → LoadRunner 변환

#### 3.1.1 지원 기능
| JMeter 요소 | LoadRunner 변환 대상 |
|-------------|---------------------|
| HTTP Request Sampler | web_url(), web_submit_data() |
| Thread Group | vuser_init(), Action(), vuser_end() |
| HTTP Header Manager | web_add_header() |
| Cookie Manager | web_set_cookie() |
| Assertions | lr_error_message(), lr_abort() |
| Timers | lr_think_time() |
| Regular Expression Extractor | web_reg_save_param() |
| JSON Extractor | web_reg_save_param_json() |
| Variables | lr_save_string() |
| Loop Controller | 반복문 (for/while) |
| If Controller | 조건문 (if) |

#### 3.1.2 변환 로직
```
1. JMX 파일 구조 분석
   - TestPlan → 스크립트 헤더
   - ThreadGroup → vuser_init/Action/vuser_end 구조
   - HTTPSamplerProxy → HTTP 함수 변환

2. 요청 메소드별 변환
   - GET → web_url()
   - POST → web_submit_data()
   - PUT/DELETE → web_custom_request()

3. 파라미터 처리
   - Query Parameters → URL 인코딩
   - Body Parameters → ITEMDATA 배열
   - Headers → web_add_header()

4. 동적 데이터 처리
   - ${variable} → lr_eval_string("{variable}")
   - Correlation → web_reg_save_param()
```

### 3.2 2차 우선순위: LoadRunner → JMeter 변환

#### 3.2.1 지원 기능
| LoadRunner 함수 | JMeter 변환 대상 |
|-----------------|------------------|
| web_url() | HTTP Request (GET) |
| web_submit_data() | HTTP Request (POST) |
| web_add_header() | HTTP Header Manager |
| web_reg_save_param() | Regular Expression Extractor |
| lr_think_time() | Constant Timer |
| vuser_init/end | setUp/tearDown Thread Group |
| Action() | Main Thread Group |

### 3.3 공통 기능

#### 3.3.1 파일 입출력
- **입력**: 파일 업로드 (Drag & Drop 지원)
  - JMX: `.jmx` 확장자
  - LoadRunner: `.c` 확장자
- **출력**: 변환된 파일 다운로드
  - 파일명 자동 생성 (원본명_converted.확장자)

#### 3.3.2 검증 기능
- 입력 파일 형식 검증
- 구문 오류 감지 및 보고
- 변환 불가능한 요소 경고

#### 3.3.3 프리뷰 기능
- 원본 코드 표시 (좌측)
- 변환된 코드 표시 (우측)
- 구문 하이라이팅 (Syntax Highlighting)

---

## 4. UI/UX 디자인

### 4.1 레이아웃 구조
```
참고: https://jsonformatter.org/json-to-xml

┌─────────────────────────────────────────────────┐
│  Performance Test Script Converter              │
│  [로고]                                         │
├─────────────────────────────────────────────────┤
│                                                 │
│  [ JMeter → LoadRunner ]  [ LoadRunner → JMeter ]│
│                                                 │
├─────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐   │
│  │   Input File    │    │  Converted File │   │
│  │                 │ →  │                 │   │
│  │  [Upload Area]  │    │  [Preview Area] │   │
│  │                 │    │                 │   │
│  └─────────────────┘    └─────────────────┘   │
│                                                 │
│         [Convert] [Download] [Clear]           │
│                                                 │
├─────────────────────────────────────────────────┤
│  Conversion Log:                                │
│  ✓ Successfully converted 15 HTTP requests     │
│  ⚠ Warning: 2 unsupported elements skipped    │
└─────────────────────────────────────────────────┘
```

### 4.2 UI 컴포넌트

#### 4.2.1 헤더
- 제목: "Performance Test Script Converter"
- 부제목: "JMeter ↔ LoadRunner Script Converter"

#### 4.2.2 변환 방향 선택
- 탭 또는 라디오 버튼
- 옵션:
  - "JMeter → LoadRunner" (기본 선택)
  - "LoadRunner → JMeter"

#### 4.2.3 입력 영역
- 파일 업로드 위젯
- 지원 형식 표시
- Drag & Drop 영역
- 파일명 표시

#### 4.2.4 출력 영역
- 코드 프리뷰 (읽기 전용)
- 라인 번호 표시
- 구문 하이라이팅

#### 4.2.5 액션 버튼
- **Convert**: 변환 실행
- **Download**: 변환 파일 다운로드
- **Clear**: 입력/출력 초기화

#### 4.2.6 로그 영역
- 변환 상태 메시지
- 경고 및 오류 표시
- 통계 정보 (변환 항목 수)

### 4.3 색상 스키마
```python
primary_color = "#1E88E5"      # 파란색 (액션 버튼)
secondary_color = "#43A047"    # 초록색 (성공 메시지)
warning_color = "#FB8C00"      # 주황색 (경고)
error_color = "#E53935"        # 빨간색 (오류)
background_color = "#FAFAFA"   # 연한 회색
text_color = "#212121"         # 진한 회색
```

---

## 5. 아키텍처 설계

### 5.1 디렉토리 구조
```
performance-script-converter/
├── app.py                      # Streamlit 메인 앱
├── requirements.txt            # 의존성 패키지
├── README.md                   # 프로젝트 문서
├── converters/
│   ├── __init__.py
│   ├── jmeter_to_lr.py        # JMeter → LoadRunner 변환기
│   ├── lr_to_jmeter.py        # LoadRunner → JMeter 변환기
│   └── base_converter.py      # 공통 변환 로직
├── parsers/
│   ├── __init__.py
│   ├── jmx_parser.py          # JMX 파일 파싱
│   └── lr_parser.py           # LoadRunner C 파싱
├── generators/
│   ├── __init__.py
│   ├── lr_generator.py        # LoadRunner 코드 생성
│   └── jmx_generator.py       # JMX 파일 생성
├── utils/
│   ├── __init__.py
│   ├── validators.py          # 파일 검증
│   └── formatters.py          # 코드 포매팅
└── tests/
    ├── __init__.py
    ├── test_jmeter_to_lr.py
    └── test_lr_to_jmeter.py
```

### 5.2 클래스 다이어그램
```python
# 핵심 클래스 구조

class BaseConverter:
    - validate_input()
    - convert()
    - generate_output()

class JMeterToLRConverter(BaseConverter):
    - parse_jmx()
    - convert_http_sampler()
    - convert_thread_group()
    - generate_lr_script()

class LRToJMeterConverter(BaseConverter):
    - parse_lr_script()
    - convert_web_url()
    - convert_web_submit_data()
    - generate_jmx()

class JMXParser:
    - load_file()
    - extract_test_plan()
    - extract_thread_groups()
    - extract_samplers()

class LRParser:
    - load_file()
    - extract_functions()
    - parse_parameters()
    - identify_sections()
```

---

## 6. 변환 매핑 상세

### 6.1 JMeter → LoadRunner 매핑표

#### 6.1.1 HTTP Request 변환
```xml
<!-- JMeter JMX -->
<HTTPSamplerProxy>
  <stringProp name="HTTPSampler.domain">example.com</stringProp>
  <stringProp name="HTTPSampler.path">/api/users</stringProp>
  <stringProp name="HTTPSampler.method">GET</stringProp>
</HTTPSamplerProxy>
```

```c
/* LoadRunner C */
web_url("api_users",
    "URL=http://example.com/api/users",
    "Resource=0",
    "RecContentType=application/json",
    "Referer=",
    "Snapshot=t1.inf",
    "Mode=HTML",
    LAST);
```

#### 6.1.2 Thread Group 변환
```xml
<!-- JMeter -->
<ThreadGroup>
  <stringProp name="ThreadGroup.num_threads">10</stringProp>
  <stringProp name="ThreadGroup.ramp_time">5</stringProp>
</ThreadGroup>
```

```c
/* LoadRunner - Runtime Settings로 설정 */
// 주석으로 설정 정보 표시
/*
 * Runtime Settings:
 * Virtual Users: 10
 * Ramp-up Time: 5 seconds
 */
```

#### 6.1.3 Correlation 변환
```xml
<!-- JMeter -->
<RegexExtractor>
  <stringProp name="RegexExtractor.refname">token</stringProp>
  <stringProp name="RegexExtractor.regex">token":"([^"]+)</stringProp>
</RegexExtractor>
```

```c
/* LoadRunner */
web_reg_save_param("token",
    "LB=token\":\"",
    "RB=\"",
    "Ord=1",
    LAST);
```

### 6.2 LoadRunner → JMeter 매핑표

#### 6.2.1 web_url() 변환
```c
/* LoadRunner */
web_url("homepage",
    "URL=http://example.com/",
    "Resource=0",
    LAST);
```

```xml
<!-- JMeter -->
<HTTPSamplerProxy>
  <stringProp name="HTTPSampler.domain">example.com</stringProp>
  <stringProp name="HTTPSampler.path">/</stringProp>
  <stringProp name="HTTPSampler.method">GET</stringProp>
  <stringProp name="HTTPSampler.protocol">http</stringProp>
</HTTPSamplerProxy>
```

---

## 7. 비기능 요구사항

### 7.1 성능
- 파일 크기: 최대 10MB 지원
- 변환 시간: 1MB당 5초 이내
- 동시 사용자: 10명 이상 지원

### 7.2 보안
- 업로드 파일 검증 (확장자, MIME 타입)
- 악성 코드 패턴 필터링
- 세션 격리 (Streamlit 기본 제공)

### 7.3 호환성
- Python 3.9 이상
- 최신 브라우저 지원 (Chrome, Firefox, Safari, Edge)

### 7.4 사용성
- 직관적인 UI (3클릭 이내 변환 완료)
- 명확한 오류 메시지
- 단계별 가이드 제공

---

## 8. 개발 계획

### 8.1 Phase 1: 기본 구조 (1-2주)
- [ ] Streamlit 앱 기본 구조 구현
- [ ] UI 레이아웃 설계
- [ ] 파일 업로드/다운로드 기능

### 8.2 Phase 2: JMeter → LoadRunner 변환 (3-4주)
- [ ] JMX 파싱 엔진 개발
- [ ] HTTP Request 변환 로직
- [ ] Thread Group 변환
- [ ] Correlation 변환
- [ ] LoadRunner 코드 생성기

### 8.3 Phase 3: LoadRunner → JMeter 변환 (3-4주)
- [ ] LoadRunner C 파싱 엔진
- [ ] 함수별 변환 로직
- [ ] JMX 생성기
- [ ] 양방향 테스트

### 8.4 Phase 4: 고도화 (2주)
- [ ] 에러 핸들링 강화
- [ ] 프리뷰 기능 개선
- [ ] 사용자 피드백 반영
- [ ] 문서화

---

## 9. 테스트 계획

### 9.1 단위 테스트
- 각 변환 함수별 테스트 케이스
- 파싱 정확도 검증
- 예외 상황 처리

### 9.2 통합 테스트
- End-to-End 변환 테스트
- 실제 스크립트 변환 검증
- 성능 테스트

### 9.3 사용자 테스트
- 성능 테스트 엔지니어 대상 베타 테스트
- 피드백 수집 및 개선

---

## 10. 성공 지표

### 10.1 정량적 지표
- 변환 정확도: 95% 이상
- 평균 변환 시간: 10초 이내 (1MB 기준)
- 오류율: 5% 미만

### 10.2 정성적 지표
- 사용자 만족도: 4.0/5.0 이상
- UI 직관성: 3회 이하 클릭으로 변환 완료
- 문서 완성도: 모든 기능 가이드 제공

---

## 11. 제약사항 및 가정

### 11.1 제약사항
- 복잡한 커스텀 함수는 수동 수정 필요
- LoadRunner의 GUI 기반 설정은 주석으로 안내
- JMeter 플러그인 기능은 미지원

### 11.2 가정
- 입력 파일이 유효한 형식이라고 가정
- 표준 HTTP 프로토콜만 지원
- 사용자가 기본적인 성능 테스트 지식 보유

---

## 12. 참고 자료

### 12.1 기술 문서
- JMeter User Manual: https://jmeter.apache.org/usermanual/
- LoadRunner C Language Reference: HP/Micro Focus 공식 문서
- Streamlit Documentation: https://docs.streamlit.io/

### 12.2 UI 참고
- JSON Formatter: https://jsonformatter.org/json-to-xml
- Online Code Converter 사이트들

---

## 부록: 샘플 변환 예제

### A. 단순 GET 요청
**입력 (JMeter JMX):**
```xml
<HTTPSamplerProxy>
  <stringProp name="HTTPSampler.domain">api.example.com</stringProp>
  <stringProp name="HTTPSampler.path">/v1/users</stringProp>
  <stringProp name="HTTPSampler.method">GET</stringProp>
</HTTPSamplerProxy>
```

**출력 (LoadRunner C):**
```c
web_url("GetUsers",
    "URL=http://api.example.com/v1/users",
    "Resource=0",
    "RecContentType=application/json",
    "Snapshot=t1.inf",
    "Mode=HTML",
    LAST);
```

### B. POST 요청 (JSON Body)
**입력 (JMeter JMX):**
```xml
<HTTPSamplerProxy>
  <stringProp name="HTTPSampler.method">POST</stringProp>
  <stringProp name="HTTPSampler.path">/api/login</stringProp>
  <boolProp name="HTTPSampler.postBodyRaw">true</boolProp>
  <stringProp name="Argument.value">{"username":"test","password":"123"}</stringProp>
</HTTPSamplerProxy>
```

**출력 (LoadRunner C):**
```c
web_custom_request("Login",
    "URL=http://example.com/api/login",
    "Method=POST",
    "Resource=0",
    "RecContentType=application/json",
    "Body={\"username\":\"test\",\"password\":\"123\"}",
    LAST);
```

---

**문서 버전**: 1.0  
**작성일**: 2025-10-13  
**작성자**: Performance Test Team
