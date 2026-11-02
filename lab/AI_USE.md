# AI-Use Disclosure · E1 (과제 ② · 교육생 B · 2026-11-03)

사용 도구: Claude (claude.ai, Opus 5.5)

## 아이디어 · 구성

- 강의 흐름(비용 공식 → 추론 토큰 → 숨은 입력 → 캐시 → 온프레미스 → 결정 기준)과 확인 질문 2개는 Claude가 제안했고, M1 기준 슬라이드와 대조해 채택함.

## 글쓰기 · 슬라이드

- 슬라이드 10장과 발표 노트의 초안은 Claude가 작성함.
- 수치와 출처는 M1 기준 슬라이드(17, 18, 20–22, 24쪽)와 E1 예제 자료(3–5쪽)와 직접 대조함.
- 해석 3줄은 Claude 초안을 바탕으로 직접 수정함.

## 코드

- `lv0/backends.py`(Result, call_local, call_claude, call)와 `e1_two_models.py`의 초안은 Claude가 작성함.
- 직접 실행하며 응답 원본을 열어 아래 필드 위치를 확인하고 코드에 반영함.
  - local 추론 토큰: `usage.completion_tokens_details.reasoning_tokens`
  - claude 추론 토큰: `usage.output_tokens_details.thinking_tokens`
  - claude 입력 토큰: `input_tokens` + `cache_creation_input_tokens` + `cache_read_input_tokens`
- 환경 설정(uv 가상환경, VS Code 인터프리터 선택)은 Claude의 안내를 받아 직접 진행함.

## 실험 · 분석

- 모든 측정은 직접 실행함(2026-11-02, MacBook · Gemma 4 E4B 3회, Claude Haiku 5.5 4회).
- 1,000건 비용 · 지연 계산과 `total_cost_usd` 정가 검산은 Claude가 계산했고, 실측값과 직접 대조함.
- 직접 확인한 결과
  - 추론 토큰이 실행마다 크게 달라짐: Haiku 0–86, Gemma 380–676
  - Haiku는 SDK system prompt 631토큰을 1시간 캐시로 씀: 첫 호출 $0.000412 → 이후 $0.000246–0.000296
  - `total_cost_usd`(model_usage)에 `usage`에 없는 부가 호출 몫(입력 약 1,200 · 출력 30)이 매번 포함됨. 정체는 확인하지 못함.
  - Gemma 답 품질이 10/29 오답, 11/2 정답으로 달라짐

## 확인하지 못한 것

- 부가 호출의 정체
- 구독 로그인의 `total_cost_usd`(costBasis: list)가 실제 청구액과 같은지
- 병렬 처리 시 1,000건 지연(순차 처리 가정으로만 계산함)
