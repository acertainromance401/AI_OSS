# AI_OSS

OSS class practice repository

## About
AI학과 재학 중인 대학생, Python 기반 ML/딥러닝 실험과 데이터 파이프라인 구현에 집중합니다.

## Project
자세한 프로젝트 내용은 [Project_Proposal.txt](Project_Proposal.txt)를 참고하세요.

## Swift Canvas Prototype

- 위치: `ios/CanvasDrawingPrototype.playground`
- Xcode 또는 Swift Playgrounds에서 playground를 열면 캔버스 드로잉 UI를 바로 확인할 수 있습니다.
- 포함 기능: 자유 드로잉, 색상 선택, 브러시 두께 조절, Undo, Clear

## Backend API (FastAPI)

### 1. 설치

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. 실행

```bash
# first time only
cp .env.example .env

uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 주요 엔드포인트

- `GET /health`: 서버 상태 확인
- `POST /analyze`: 색상 팔레트 기반 감정 분석
- `POST /feedback`: 사용자 피드백 저장 (`data/feedback.csv`)

### 3-1. 분석 데이터셋 파일

- `data/color_emotion_labeled_updated.csv`
- `data/colorassociations_warmth - colorwarmth.csv`

`POST /analyze`는 위 두 CSV를 로드해 최근접 색상 기반으로 감정 점수를 계산합니다.

주의: 위 CSV는 라이선스/재배포 확인 전까지 저장소에 커밋하지 않도록 설정되어 있습니다.
로컬 테스트 시에는 본인 데이터 파일을 `data/` 폴더에 직접 배치하세요.

### 4. 분석 요청 예시

```json
{
	"palette": [
		{ "r": 255, "g": 120, "b": 80 },
		{ "r": 40, "g": 80, "b": 190 }
	],
	"weights": [0.7, 0.3]
}
```

Swagger 문서: `http://localhost:8000/docs`

## Security and Compliance Notes

- Docker/Grafana admin password is read from environment variables (`.env.example` 참고).
- Dataset redistribution/license details are tracked in `data/DATA_LICENSE.txt`.

## DORA Metrics 수집 자동화 구현 방법(간단)

1. `.github/workflows/metrics.yml`에서 DORA 파이프라인을 구성했습니다.
2. `scripts/collect_dora_metrics.py`에서 GitHub API를 호출해 4개 지표(Lead Time, Deployment Frequency, MTTR, Change Failure Rate)를 계산합니다.
3. 계산 결과를 `metrics/dora_metrics.json`으로 저장하고 Actions Artifact(`dora-metrics`)로 업로드합니다.
4. 주간 스케줄 실행 시 요약 리포트를 생성해 GitHub Issue로 자동 등록합니다.

## DORA Metrics 자동 수집 파이프라인

- 워크플로우 파일: `.github/workflows/metrics.yml`
- 수집 스크립트: `scripts/collect_dora_metrics.py`
- 실행 트리거:
	- PR 병합 시 (`pull_request: closed`)
	- 배포 상태 변경 시 (`deployment_status`)
	- 주간 실행 (`schedule`, 매주 일요일 자정)
	- 수동 실행 (`workflow_dispatch`)

### 수집 지표

- Lead Time for Changes (평균 시간)
- Deployment Frequency (주간 성공 배포 횟수)
- MTTR (평균 복구 시간)
- Change Failure Rate (실패 배포 비율)

### 결과 저장 및 리포팅

- 계산 결과는 `metrics/dora_metrics.json`으로 생성
- GitHub Actions Artifact(`dora-metrics`)로 업로드
- 주간 스케줄 실행 시 요약 보고서를 GitHub Issue로 자동 생성

(본 레퍼지토리의 모든 내용은 AI로 작성하였음)
