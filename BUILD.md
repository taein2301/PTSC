# PTSC 빌드 가이드

Performance Test Script Converter를 독립 실행 가능한 .exe 파일로 빌드하는 방법입니다.

## 사전 요구사항

- Python 3.9 이상
- Windows 10/11
- 가상 환경 설정 완료

## 빌드 방법

### 1. 가상 환경 활성화

```bash
.venv\Scripts\activate
```

### 2. 의존성 설치

```bash
pip install -r requirements.txt
```

### 3. 빌드 실행

#### 자동 빌드 (권장)

```bash
build_exe.bat
```

이 스크립트는 자동으로:
- 가상 환경 활성화
- PyInstaller 설치 확인
- 이전 빌드 정리
- 새로운 빌드 생성
- 필요한 파일 복사

#### 수동 빌드

```bash
pyinstaller --clean PTSC.spec
```

## 빌드 결과

빌드가 성공하면 다음 경로에 실행 파일이 생성됩니다:

```
dist/PTSC/
├── PTSC.exe          # 메인 실행 파일
├── app.py            # Streamlit 앱
├── converters/       # 변환기 모듈
├── parsers/          # 파서 모듈
├── generators/       # 생성기 모듈
├── utils/            # 유틸리티 모듈
├── samples/          # 샘플 파일
├── .streamlit/       # Streamlit 설정
└── README.txt        # 사용자 가이드
```

## 실행 방법

### 빌드된 실행 파일 실행

1. `dist\PTSC` 폴더로 이동
2. `PTSC.exe` 더블 클릭
3. 자동으로 브라우저가 열리고 애플리케이션이 실행됩니다
4. 브라우저가 자동으로 열리지 않으면 `http://localhost:8501` 접속

### 배포

`dist\PTSC` 폴더 전체를 압축하여 배포할 수 있습니다:

```bash
# 폴더 이름 예시
PTSC_v1.0.0_windows_x64.zip
```

## 문제 해결

### PyInstaller가 설치되지 않는 경우

```bash
pip install pyinstaller
```

### 빌드 중 모듈을 찾을 수 없다는 오류

`PTSC.spec` 파일의 `hiddenimports` 섹션에 누락된 모듈을 추가하세요:

```python
hiddenimports=[
    'streamlit',
    'your_missing_module',
    # ...
],
```

### 실행 시 Streamlit이 시작되지 않는 경우

1. 콘솔 창에서 에러 메시지 확인
2. 방화벽에서 `PTSC.exe` 허용
3. 포트 8501이 다른 프로그램에서 사용 중인지 확인

### 빌드 파일이 너무 큰 경우

PyInstaller는 모든 의존성을 포함하므로 크기가 클 수 있습니다 (약 100-300MB).
- UPX 압축이 자동으로 적용됩니다
- 배포 시 ZIP 파일로 압축하면 크기가 줄어듭니다

## 개발 모드 실행

빌드하지 않고 개발 모드로 실행:

```bash
streamlit run app.py
```

## 참고사항

- 첫 실행은 초기화 시간이 소요될 수 있습니다 (5-10초)
- 인터넷 연결이 필요하지 않습니다 (독립 실행)
- Windows Defender가 실행 파일을 검사할 수 있습니다

## 빌드 환경

- Python: 3.9+
- PyInstaller: 6.0+
- Streamlit: 1.28+
- OS: Windows 10/11

## 라이선스

MIT License - 자세한 내용은 LICENSE 파일 참조
