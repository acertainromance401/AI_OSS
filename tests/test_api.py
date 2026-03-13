from pathlib import Path

from fastapi.testclient import TestClient

from api import main
from api import emotion_engine


client = TestClient(main.app)


def _write_test_datasets(base_dir: Path) -> tuple[Path, Path]:
    primary = base_dir / "color_emotion_labeled_updated.csv"
    warmth = base_dir / "colorassociations_warmth - colorwarmth.csv"

    primary.write_text(
        "\n".join(
            [
                "emotion,R,G,B,color_name,color_label",
                "energy,255,36,0,SCARLET,1",
                "calmness,135,206,235,SKY BLUE,2",
                "harmony,19,150,17,GREEN,3",
            ]
        ),
        encoding="utf-8",
    )

    warmth.write_text(
        "\n".join(
            [
                ",COLOR_ID,HEX_CODE,RGB_ID,CMYK_ID,HSV_ID,WARM,ASSOCIATION_1,ASSOCIATION_2,ASSOCIATION_3",
                ",SCARLET,#FF2400,\"255, 36, 0\",\"0%, 86%, 100%, 0%\",\"9°, 100%, 100%\",1,COURAGE,SIN,ENERGY",
                ",SKY BLUE,#87CEEB,\"135, 206, 235\",\"43%, 12%, 0%, 8%\",\"197°, 43%, 92%\",0,CALMNESS,FREEDOM,TRANQUILITY",
                ",GREEN,#139611,\"19, 150, 17\",\"87%, 0%, 89%, 41%\",\"119°, 89%, 59%\",0,HARMONY,FRESHNESS,IMMATURITY",
            ]
        ),
        encoding="utf-8",
    )
    return primary, warmth


def _patch_engine_dataset(monkeypatch, tmp_path: Path) -> None:
    primary, warmth = _write_test_datasets(tmp_path)
    monkeypatch.setattr(emotion_engine, "PRIMARY_DATASET", primary)
    monkeypatch.setattr(emotion_engine, "WARMTH_DATASET", warmth)
    monkeypatch.setattr(emotion_engine, "_DATASET_CACHE", None)
    monkeypatch.setattr(emotion_engine, "_ASSOCIATION_CACHE", None)
    monkeypatch.setattr(emotion_engine, "_EMOTIONS_CACHE", None)


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_endpoint_returns_prediction_and_scores(tmp_path: Path, monkeypatch) -> None:
    _patch_engine_dataset(monkeypatch, tmp_path)

    payload = {
        "palette": [
            {"r": 255, "g": 36, "b": 0},
            {"r": 135, "g": 206, "b": 235},
        ],
        "weights": [0.7, 0.3],
    }

    response = client.post("/analyze", json=payload)
    assert response.status_code == 200

    body = response.json()
    assert "predicted_emotion" in body
    assert "confidence_scores" in body
    assert isinstance(body["confidence_scores"], dict)
    assert body["predicted_emotion"] in body["confidence_scores"]

    score_sum = sum(body["confidence_scores"].values())
    assert 0.98 <= score_sum <= 1.02


def test_analyze_endpoint_rejects_negative_weight(tmp_path: Path, monkeypatch) -> None:
    _patch_engine_dataset(monkeypatch, tmp_path)

    payload = {
        "palette": [{"r": 255, "g": 36, "b": 0}],
        "weights": [-0.1],
    }

    response = client.post("/analyze", json=payload)
    assert response.status_code == 422


def test_feedback_endpoint_creates_csv(tmp_path: Path, monkeypatch) -> None:
    feedback_file = tmp_path / "feedback.csv"
    monkeypatch.setattr(main, "DATA_DIR", tmp_path)
    monkeypatch.setattr(main, "FEEDBACK_FILE", feedback_file)

    payload = {
        "predicted_emotion": "energy",
        "corrected_emotion": "calmness",
        "palette": [{"r": 255, "g": 140, "b": 0}],
        "note": "manual correction",
    }

    response = client.post("/feedback", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "saved"

    assert feedback_file.exists()
    text = feedback_file.read_text(encoding="utf-8")
    assert "predicted_emotion" in text
    assert "energy" in text
    assert "calmness" in text
