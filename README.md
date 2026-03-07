# AI_OSS

OSS class practice repository

## About
AI학과 재학 중인 대학생, Python 기반 ML/딥러닝 실험과 데이터 파이프라인 구현에 집중합니다.

## Project
자세한 프로젝트 내용은 [Project_Proposal.txt](Project_Proposal.txt)를 참고하세요.

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
