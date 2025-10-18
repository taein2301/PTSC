# Implementation Roadmap - 추가 구현 항목

**문서 버전**: 1.0
**작성일**: 2025-01-20
**최종 업데이트**: 2025-01-20

---

## 현재 구현 완료 상태 ✅

### Core Features (95% 완료)
- ✅ JMeter → LoadRunner 변환 (95%+ 정확도)
- ✅ LoadRunner → JMeter 변환 (기본 기능 완료)
- ✅ 파일 업로드 시 자동 변환
- ✅ 양방향 변환 UI (2개 탭)
- ✅ 코드 프리뷰 (구문 하이라이팅)
- ✅ 변환 로그 및 통계
- ✅ 파일 다운로드

### Advanced Features (80% 완료)
- ✅ 샘플 파일 제공 (10개 JMX, 5개 C)
- ✅ 변환 옵션 설정 UI (향후 로직 연동 필요)
- ✅ 변환 히스토리 (사이드바 표시, 필터링)
- ✅ 스크립트 비교 기능 (Side-by-side Diff)
- ✅ Show More/Less/Reset 코드 프리뷰

### Testing (82% 완료)
- ✅ Unit Tests: 28/34 테스트 통과
- ✅ Flake8 린팅 통과
- ✅ Mypy 타입 체킹 통과
- ⚠️ 6개 실패 테스트 (POST 파라미터, 헤더, 트랜잭션 등)

---

## 우선순위별 추가 구현 항목

## 🔴 Priority 0: Critical (핵심 버그 수정)

### BUG-001: POST 파라미터 변환 개선
**상태**: 🔴 Critical
**설명**: JMeter POST 요청의 파라미터가 LoadRunner ITEMDATA로 제대로 변환되지 않음
**영향**: POST 요청 변환 정확도 저하
**작업**:
- [ ] JMXParser의 POST 파라미터 추출 로직 수정
- [ ] LRGenerator의 ITEMDATA 생성 로직 개선
- [ ] 테스트 케이스 추가 및 검증

**예상 시간**: 2-3일

### BUG-002: Header Manager 변환 오류
**상태**: 🔴 Critical
**설명**: HeaderManager 구조 불일치로 헤더가 제대로 변환되지 않음
**영향**: HTTP 헤더 변환 실패
**작업**:
- [ ] HeaderManager 파싱 로직 수정
- [ ] web_add_header() 생성 로직 개선
- [ ] 다중 헤더 처리 검증

**예상 시간**: 2일

### BUG-003: Transaction Controller 변환 이슈
**상태**: 🔴 Critical
**설명**: TransactionController가 제대로 변환되지 않음
**영향**: 트랜잭션 경계가 올바르게 설정되지 않음
**작업**:
- [ ] _parse_hash_tree에서 TransactionController 처리 개선
- [ ] lr_start/end_transaction 생성 로직 검증
- [ ] 중첩 트랜잭션 처리

**예상 시간**: 2일

---

## 🟡 Priority 1: High (중요 기능 개선)

### FEAT-001: 변환 옵션 로직 연동
**상태**: 🟡 High
**설명**: 사이드바의 변환 옵션 UI가 실제 변환 로직과 연동되지 않음
**작업**:
- [ ] 들여쓰기 크기 옵션 적용 (2, 4, 8 spaces)
- [ ] 주석 포함 여부 옵션 적용
- [ ] 에러 처리 수준 옵션 적용 (Minimal, Standard, Verbose)
- [ ] CodeFormatter에 옵션 전달 로직 추가
- [ ] LRGenerator/JMXGenerator 옵션 반영

**예상 시간**: 3-4일

### FEAT-002: If Controller 변환 구현
**상태**: 🟡 High
**설명**: JMeter If Controller가 C 조건문으로 변환되지 않음
**작업**:
- [ ] IfController 파싱 로직 구현
- [ ] JMeter 조건식 → C 조건식 변환
- [ ] if 문 생성 로직 추가
- [ ] 중첩 조건문 처리

**예상 시간**: 3일

### FEAT-003: Response Assertion 변환
**상태**: 🟡 High
**설명**: ResponseAssertion이 lr_error_message로 변환되지 않음
**작업**:
- [ ] ResponseAssertion 파싱 로직 구현
- [ ] 조건문 + lr_error_message 생성
- [ ] 다양한 assertion 타입 지원 (응답 코드, 본문)

**예상 시간**: 2-3일

### FEAT-004: 대용량 파일 처리 개선
**상태**: 🟡 High
**설명**: 현재 10MB 제한, 더 큰 파일 처리 필요
**작업**:
- [ ] 스트리밍 방식 파싱 구현
- [ ] 메모리 사용 최적화
- [ ] 진행률 표시 (Progress bar)
- [ ] 파일 크기 제한 확대 (10MB → 50MB)

**예상 시간**: 4-5일

### FEAT-005: 에러 메시지 개선
**상태**: 🟡 High
**설명**: 사용자 친화적인 에러 메시지 필요
**작업**:
- [ ] 에러 타입별 메시지 템플릿 작성
- [ ] 해결 방법 가이드 추가
- [ ] 에러 위치 정보 제공 (라인 번호)
- [ ] 다국어 에러 메시지 (한/영)

**예상 시간**: 2-3일

---

## 🟢 Priority 2: Medium (편의성 개선)

### FEAT-006: 배치 변환 기능
**상태**: 🟢 Medium
**설명**: 여러 파일을 한 번에 변환
**작업**:
- [ ] 다중 파일 업로드 UI 추가
- [ ] 배치 변환 로직 구현
- [ ] ZIP 파일로 일괄 다운로드
- [ ] 변환 진행률 표시

**예상 시간**: 5-6일

### FEAT-007: 변환 프리셋 저장
**상태**: 🟢 Medium
**설명**: 자주 사용하는 변환 옵션을 프리셋으로 저장
**작업**:
- [ ] 프리셋 저장 UI 추가
- [ ] 프리셋 불러오기 기능
- [ ] 프리셋 관리 (생성, 수정, 삭제)
- [ ] LocalStorage에 프리셋 저장

**예상 시간**: 3-4일

### FEAT-008: 변환 미리보기 강화
**상태**: 🟢 Medium
**설명**: 변환 전에 어떻게 변환될지 미리 확인
**작업**:
- [ ] 실시간 미리보기 (파일 업로드 즉시)
- [ ] 변환될 요소 하이라이트
- [ ] 변환 불가 요소 경고 표시
- [ ] 변환 정확도 예측

**예상 시간**: 4-5일

### FEAT-009: 검색 및 필터링
**상태**: 🟢 Medium
**설명**: 코드 프리뷰에서 특정 텍스트 검색
**작업**:
- [ ] 검색 입력 UI 추가
- [ ] 검색 결과 하이라이트
- [ ] 다음/이전 결과 이동
- [ ] 정규표현식 검색 지원

**예상 시간**: 2-3일

### FEAT-010: 스크립트 편집 기능
**상태**: 🟢 Medium
**설명**: 변환 후 간단한 수정 가능
**작업**:
- [ ] 코드 에디터 위젯 추가
- [ ] 구문 하이라이팅 유지
- [ ] 저장/되돌리기 기능
- [ ] 수정 사항 다운로드

**예상 시간**: 5-6일

---

## 🔵 Priority 3: Low (부가 기능)

### FEAT-011: 다크 모드
**상태**: 🔵 Low
**설명**: 다크/라이트 테마 지원
**작업**:
- [ ] 테마 토글 버튼 추가
- [ ] 다크 테마 색상 스키마 정의
- [ ] 코드 프리뷰 테마 적용
- [ ] 사용자 선택 저장 (LocalStorage)

**예상 시간**: 2-3일

### FEAT-012: 다국어 지원
**상태**: 🔵 Low
**설명**: 한국어/영어 UI 지원
**작업**:
- [ ] 언어 선택 UI 추가
- [ ] 다국어 문자열 파일 작성 (i18n)
- [ ] UI 라벨 다국어화
- [ ] 에러 메시지 다국어화

**예상 시간**: 4-5일

### FEAT-013: 사용 통계 대시보드
**상태**: 🔵 Low
**설명**: 변환 통계 시각화
**작업**:
- [ ] 변환 횟수 추적
- [ ] 성공률 차트
- [ ] 인기 샘플 파일 통계
- [ ] 주간/월간 리포트

**예상 시간**: 3-4일

### FEAT-014: API 엔드포인트
**상태**: 🔵 Low
**설명**: REST API로 변환 기능 제공
**작업**:
- [ ] FastAPI 백엔드 추가
- [ ] /api/convert/jmx-to-lr 엔드포인트
- [ ] /api/convert/lr-to-jmx 엔드포인트
- [ ] API 문서 (Swagger)
- [ ] 인증 및 Rate Limiting

**예상 시간**: 7-10일

### FEAT-015: 플러그인 시스템
**상태**: 🔵 Low
**설명**: 커스텀 변환 로직 추가 가능
**작업**:
- [ ] 플러그인 아키텍처 설계
- [ ] 플러그인 로더 구현
- [ ] 플러그인 API 문서
- [ ] 샘플 플러그인 작성

**예상 시간**: 10-15일

---

## 🧪 Testing & Quality

### TEST-001: 테스트 커버리지 향상
**상태**: 🟡 High
**현재 상태**: 28/34 테스트 통과 (82%)
**목표**: 95% 이상
**작업**:
- [ ] 실패한 6개 테스트 수정
- [ ] 누락된 테스트 케이스 추가
- [ ] Edge case 테스트 추가
- [ ] 통합 테스트 강화

**예상 시간**: 5-7일

### TEST-002: E2E 테스트
**상태**: 🟡 High
**작업**:
- [ ] Selenium/Playwright 설정
- [ ] UI 테스트 시나리오 작성
- [ ] 자동화 테스트 구현
- [ ] CI/CD 파이프라인 연동

**예상 시간**: 5-6일

### TEST-003: 성능 테스트
**상태**: 🟢 Medium
**작업**:
- [ ] 변환 속도 벤치마크
- [ ] 메모리 사용량 측정
- [ ] 병목 지점 분석
- [ ] 성능 최적화

**예상 시간**: 3-4일

---

## 📚 Documentation

### DOC-001: 사용자 가이드
**상태**: 🟡 High
**작업**:
- [ ] README.md 업데이트
- [ ] 단계별 사용 가이드 작성
- [ ] 스크린샷 및 GIF 추가
- [ ] 자주 묻는 질문 (FAQ)
- [ ] 문제 해결 가이드

**예상 시간**: 3-4일

### DOC-002: API 문서
**상태**: 🟢 Medium
**작업**:
- [ ] 각 클래스/메서드 docstring 작성
- [ ] Sphinx 문서 생성
- [ ] 코드 예제 추가
- [ ] 변환 매핑 테이블 업데이트

**예상 시간**: 5-6일

### DOC-003: 개발자 가이드
**상태**: 🟢 Medium
**작업**:
- [ ] 아키텍처 다이어그램 작성
- [ ] 코드 컨벤션 정의
- [ ] 기여 가이드 (CONTRIBUTING.md)
- [ ] 개발 환경 설정 가이드

**예상 시간**: 3-4일

---

## 🚀 Deployment

### DEPLOY-001: Docker 컨테이너화
**상태**: 🟡 High
**작업**:
- [ ] Dockerfile 작성
- [ ] docker-compose.yml 작성
- [ ] 멀티 스테이지 빌드
- [ ] Docker Hub 배포

**예상 시간**: 2-3일

### DEPLOY-002: 클라우드 배포
**상태**: 🟢 Medium
**작업**:
- [ ] Streamlit Cloud 배포
- [ ] 또는 Heroku 배포
- [ ] 또는 AWS/GCP 배포
- [ ] 도메인 연결

**예상 시간**: 2-3일

### DEPLOY-003: CI/CD 파이프라인
**상태**: 🟢 Medium
**작업**:
- [ ] GitHub Actions 설정
- [ ] 자동 테스트 실행
- [ ] 자동 배포 설정
- [ ] 배포 알림 설정

**예상 시간**: 3-4일

---

## 📊 Timeline Estimation

### Sprint 1 (2주) - Critical Bugs
- BUG-001: POST 파라미터 변환
- BUG-002: Header Manager 변환
- BUG-003: Transaction Controller 변환

### Sprint 2 (2주) - High Priority Features
- FEAT-001: 변환 옵션 로직 연동
- FEAT-002: If Controller 변환
- FEAT-003: Response Assertion 변환

### Sprint 3 (2주) - Testing & Quality
- TEST-001: 테스트 커버리지 향상
- TEST-002: E2E 테스트
- DOC-001: 사용자 가이드

### Sprint 4 (2주) - Deployment
- DEPLOY-001: Docker 컨테이너화
- DEPLOY-002: 클라우드 배포
- DEPLOY-003: CI/CD 파이프라인

### Sprint 5+ (4주+) - Enhancement
- FEAT-004: 대용량 파일 처리
- FEAT-006: 배치 변환
- FEAT-008: 변환 미리보기 강화
- Medium/Low priority features

---

## 📈 Success Metrics

### 품질 목표
- [ ] 변환 정확도: 95% → 98%+
- [ ] 테스트 통과율: 82% → 95%+
- [ ] 코드 커버리지: N/A → 85%+
- [ ] 평균 변환 시간: 10초 이내 (1MB 기준)

### 사용성 목표
- [ ] 사용자 만족도: 4.0/5.0 이상
- [ ] 에러율: 5% 미만
- [ ] 문서 완성도: 모든 기능 가이드 제공

---

**총 예상 개발 기간**: 12-16주 (3-4개월)
**우선순위별 시간 배분**:
- Priority 0 (Critical): 2주
- Priority 1 (High): 4-5주
- Priority 2 (Medium): 4-5주
- Priority 3 (Low): 2-3주
