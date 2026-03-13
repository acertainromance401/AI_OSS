from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, field_validator

from .emotion_engine import RGB, aggregate_palette

app = FastAPI(
    title="SentiVision API",
    description="Color-based emotion analysis API",
    version="0.1.0",
)

DATA_DIR = Path("data")
FEEDBACK_FILE = DATA_DIR / "feedback.csv"


class RGBColor(BaseModel):
    r: int = Field(ge=0, le=255)
    g: int = Field(ge=0, le=255)
    b: int = Field(ge=0, le=255)


class AnalyzeRequest(BaseModel):
    palette: list[RGBColor] = Field(min_length=1, max_length=16)
    weights: list[float] | None = None

    @field_validator("weights")
    @classmethod
    def validate_weights(cls, value: list[float] | None) -> list[float] | None:
        if value is None:
            return value
        for weight in value:
            if weight < 0:
                raise ValueError("weights must be >= 0")
        return value


class AnalyzeResponse(BaseModel):
    predicted_emotion: str
    confidence_scores: dict[str, float]


class FeedbackRequest(BaseModel):
    predicted_emotion: str = Field(min_length=1)
    corrected_emotion: str = Field(min_length=1)
    palette: list[RGBColor] = Field(min_length=1, max_length=16)
    note: str | None = Field(default=None, max_length=300)


def _ensure_feedback_file() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if FEEDBACK_FILE.exists():
        return

    with FEEDBACK_FILE.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "timestamp",
                "predicted_emotion",
                "corrected_emotion",
                "palette",
                "note",
            ],
        )
        writer.writeheader()


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "SentiVision API is running"}


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze(payload: AnalyzeRequest) -> AnalyzeResponse:
    try:
        colors = [RGB(r=c.r, g=c.g, b=c.b) for c in payload.palette]
        best_emotion, scores = aggregate_palette(colors, payload.weights)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error

    return AnalyzeResponse(
        predicted_emotion=best_emotion,
        confidence_scores=scores,
    )


@app.post("/feedback")
def save_feedback(payload: FeedbackRequest) -> dict[str, str]:
    _ensure_feedback_file()

    palette_as_text = ";".join(
        [f"{color.r},{color.g},{color.b}" for color in payload.palette]
    )

    with FEEDBACK_FILE.open("a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "timestamp",
                "predicted_emotion",
                "corrected_emotion",
                "palette",
                "note",
            ],
        )
        writer.writerow(
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "predicted_emotion": payload.predicted_emotion.strip().lower(),
                "corrected_emotion": payload.corrected_emotion.strip().lower(),
                "palette": palette_as_text,
                "note": (payload.note or "").strip(),
            }
        )

    return {"status": "saved"}
