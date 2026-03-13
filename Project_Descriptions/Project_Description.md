# SentiVision Project Description

작성일: 2026-03-13  
통합 문서 버전: v1.0

## 문서 바로가기
- PRD 원본: [PRD_SentiVision.md](PRD_SentiVision.md)
- WBS 원본: [WBS_SentiVision.md](WBS_SentiVision.md)
- WireFrame 원본: [Wireframe_SentiVision.md](Wireframe_SentiVision.md)
- User Journey 원본: [User_Journey_Scenario_SentiVision.md](User_Journey_Scenario_SentiVision.md)

---

## 1. 프로젝트 한눈에 보기
SentiVision은 사용자의 드로잉 색상 팔레트를 분석해 감정 상태를 예측하고, 사용자 피드백을 통해 점진적으로 정확도를 높이는 감성 컴퓨팅 프로젝트다.

핵심 가치
- 빠른 감정 인사이트 제공
- 결과의 시각화 및 이해 용이성
- 피드백 기반 지속 개선 루프

---

## 2. PRD 통합 요약

### 2-1. 목표
- 색상 기반 감정 예측 제공
- 분석 결과 시각화 제공
- 사용자 피드백 수집 및 모델 개선

### 2-2. 비목표
- 의료/임상 진단 제공
- 실시간 멀티유저 협업 드로잉
- 텍스트/음성 멀티모달 분석(초기 버전)

### 2-3. 핵심 기능 요구사항
- FR-1: 드로잉 및 분석 요청
- FR-2: 감정 분석 API (POST /analyze)
- FR-3: 피드백 API (POST /feedback)
- FR-4: 결과 시각화
- FR-5: 데이터 기반 감정 매핑

### 2-4. 비기능 요구사항
- 성능: 평균 응답 2초 이내 목표
- 안정성: GET /health 제공
- 보안: 민감값 하드코딩 금지, 환경변수 사용
- 컴플라이언스: 데이터 라이선스 확인 전 공개 커밋 금지

### 2-5. KPI
- 모델 정확도: 80%+ (목표 85%+)
- 피드백 제출률
- API health 성공률 99%+

---

## 3. WBS 통합 요약

### 3-1. 단계별 작업 구조
1. 프로젝트 관리
2. 요구사항/기획
3. 아키텍처/설계
4. 백엔드 API 개발
5. 감정 분석 엔진
6. 테스트/품질
7. 보안/컴플라이언스
8. iOS 연동 준비
9. 배포/운영 준비

### 3-2. 주차별 권장 계획
- 1~2주: 기획/설계
- 3~6주: API/분석엔진 구현
- 7~9주: 테스트/연동
- 10~12주: 보안 점검/운영 준비

### 3-3. 완료 기준 규칙
- 각 항목은 산출물 + 완료 기준 둘 다 충족 시 Done
- 상태 관리: Not Started / In Progress / Done

---

## 4. WireFrame 통합 요약

### 4-1. 화면 플로우
Home -> Canvas -> Result -> Feedback -> History

### 4-2. 핵심 화면
- Home: 새 그림 시작, 최근 분석 요약
- Canvas: 드로잉, 팔레트 미리보기, 분석 요청
- Result: 예측 감정, 점수 분포, 대표 색상
- Feedback: 예측 정정 및 메모 제출
- History: 과거 분석 이력 조회

### 4-3. 예외 상태 화면
- 분석 로딩 상태
- 분석 실패 상태(재시도 제공)
- 피드백 제출 완료 상태

### 4-4. API 연결 포인트
- 분석하기 -> POST /analyze
- 피드백 제출 -> POST /feedback
- 상태 확인 -> GET /health

---

## 5. User Journey 통합 요약

### 5-1. 페르소나
- 감정 확인을 가볍게 하고 싶은 사용자
- 색상 표현에 익숙한 사용자

### 5-2. 핵심 여정
1. 앱 진입
2. 그림 작성
3. 분석 요청
4. 결과 확인
5. 피드백 제출
6. 기록 확인 및 재방문

### 5-3. 대표 시나리오
- 사용자가 그림 작성 후 분석 요청
- 2초 내 예측 결과 확인
- 필요 시 피드백 제출
- 결과 저장 후 종료 또는 기록 확인

### 5-4. 예외 시나리오
- 네트워크 오류
- 데이터셋 로드 실패
- 예측 불일치 반복

### 5-5. 여정 KPI
- 홈 -> 캔버스 전환율
- 분석 완료율/응답시간
- 피드백 제출률
- 재방문율

---

## 6. 시스템 구성 및 실행 정보

### 6-1. Backend API
- FastAPI 기반
- 주요 엔드포인트: /health, /analyze, /feedback

### 6-2. 테스트
- pytest 기반 API 테스트
- GitHub Actions 테스트 워크플로우 구성

### 6-3. 보안 및 데이터 정책
- 환경변수 기반 보안 설정 사용
- 데이터 라이선스 검증 전 CSV 공개 커밋 금지
- 관련 문서:
  - [data/DATA_LICENSE.txt](data/DATA_LICENSE.txt)
  - [Data_License_Checklist.txt](Data_License_Checklist.txt)

---

## 7. 최종 수용 기준
- PRD, WBS, WireFrame, User Journey 문서가 서로 일관된 범위/용어를 가진다.
- API 핵심 플로우(분석/피드백/헬스체크)가 문서와 구현에서 일치한다.
- 테스트 및 보안/라이선스 정책이 공개 저장소 기준으로 명시된다.

---

## 8. 원본 문서 링크 모음
- [Project_Proposal.txt](Project_Proposal.txt)
- [PRD_SentiVision.md](PRD_SentiVision.md)
- [WBS_SentiVision.md](WBS_SentiVision.md)
- [Wireframe_SentiVision.md](Wireframe_SentiVision.md)
- [User_Journey_Scenario_SentiVision.md](User_Journey_Scenario_SentiVision.md)
- [README.md](README.md)
