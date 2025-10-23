# AI Prompt Templates

This file contains prompt templates used by the Gemini AI Helper.

## Conversion Analysis Prompt

```
당신은 성능 테스트 스크립트 변환 전문가입니다.

다음 변환 결과를 분석하고 한글로 요약해주세요:

**변환 정보:**
- 변환 방향: {source_type} → {target_type}
- 총 항목 수: {total}
- 변환 성공: {converted}
- 변환 스킵: {skipped}
- 변환 정확도: {accuracy:.1f}%

**경고 메시지 ({warning_count}개):**
{warnings}

**오류 메시지 ({error_count}개):**
{errors}

**변환된 스크립트 미리보기:**
```
{content_preview}
```

다음 항목을 포함하여 200자 이내로 간결하게 요약해주세요:
1. 변환 품질 평가 (우수/양호/주의 필요)
2. 주요 변환 항목 (예: HTTP 요청, 트랜잭션, 상관관계 등)
3. 주의사항 또는 권장사항 (있는 경우)

답변은 반드시 200자 이내로 간결하게 작성하고, 마크다운 형식을 사용하지 마세요.
```

## Conversion Tips Prompt

```
당신은 성능 테스트 전문가입니다.

{source_type}에서 {target_type}로 스크립트를 변환할 때 주의할 점 3가지를 150자 이내로 간결하게 알려주세요.

답변 형식:
1. [첫 번째 주의사항]
2. [두 번째 주의사항]
3. [세 번째 주의사항]

마크다운을 사용하지 말고 일반 텍스트로만 작성하세요.
```

## Variables Reference

### For Conversion Analysis:
- `{source_type}`: Source format (e.g., 'JMeter', 'LoadRunner')
- `{target_type}`: Target format (e.g., 'LoadRunner', 'JMeter')
- `{total}`: Total number of items
- `{converted}`: Number of successfully converted items
- `{skipped}`: Number of skipped items
- `{accuracy}`: Conversion accuracy percentage
- `{warning_count}`: Number of warnings
- `{warnings}`: Warning messages (up to 5)
- `{error_count}`: Number of errors
- `{errors}`: Error messages (up to 5)
- `{content_preview}`: Preview of converted script (first 500 chars)

### For Conversion Tips:
- `{source_type}`: Source format
- `{target_type}`: Target format
