from __future__ import annotations

from pathlib import Path

import numpy as np

from app.application.services.semantic_category_service import SemanticCategoryService
from app.core.config import Settings


class StubModel:
    def encode(self, texts, **_kwargs):
        if any("社团" in text or "纳新" in text for text in texts):
            return np.array([[1.0, 0.0]], dtype=float)
        return np.array([[0.0, 1.0]], dtype=float)


def test_semantic_category_service_accepts_clear_campus_activity(tmp_path: Path):
    centroid_dir = tmp_path / "embeddings"
    centroid_dir.mkdir()
    np.save(centroid_dir / "campus_activity_centroid.npy", np.array([1.0, 0.0], dtype=float))
    settings = Settings(
        semantic_centroid_dir=centroid_dir.as_posix(),
        semantic_accept_threshold=0.68,
        semantic_strong_threshold=0.75,
        semantic_margin_threshold=0.06,
    )
    service = SemanticCategoryService(settings)
    service._model = StubModel()

    decision = service.classify(title="社团纳新报名", summary="", content="")

    assert decision.category == "campus_activity"
    assert decision.confidence == "high"
    assert decision.top_score == 1.0


def test_semantic_category_service_keeps_unclear_result_as_other(tmp_path: Path):
    centroid_dir = tmp_path / "embeddings"
    centroid_dir.mkdir()
    np.save(centroid_dir / "campus_activity_centroid.npy", np.array([1.0, 0.0], dtype=float))
    settings = Settings(
        semantic_centroid_dir=centroid_dir.as_posix(),
        semantic_accept_threshold=0.68,
        semantic_strong_threshold=0.75,
        semantic_margin_threshold=0.06,
    )
    service = SemanticCategoryService(settings)
    service._model = StubModel()

    decision = service.classify(title="期末考试安排", summary="", content="")

    assert decision.category == "other"
    assert decision.confidence == "low"


def test_semantic_category_service_requires_margin_for_high_confidence(tmp_path: Path):
    centroid_dir = tmp_path / "embeddings"
    centroid_dir.mkdir()
    np.save(centroid_dir / "campus_activity_centroid.npy", np.array([1.0, 0.0], dtype=float))
    np.save(centroid_dir / "lecture_centroid.npy", np.array([0.99, 0.01], dtype=float))
    settings = Settings(
        semantic_centroid_dir=centroid_dir.as_posix(),
        semantic_accept_threshold=0.68,
        semantic_strong_threshold=0.75,
        semantic_margin_threshold=0.06,
    )
    service = SemanticCategoryService(settings)
    service._model = StubModel()

    decision = service.classify(title="社团纳新报名", summary="", content="")

    assert decision.category == "other"
    assert decision.confidence == "low"
    assert decision.top_category == "campus_activity"
    assert decision.second_category == "lecture"


def test_semantic_category_service_loads_all_supported_centroids(tmp_path: Path):
    centroid_dir = tmp_path / "embeddings"
    centroid_dir.mkdir()
    for category in (
        "campus_activity",
        "competition",
        "volunteer",
        "graduate_study",
        "exam_certification",
        "recruitment",
        "lecture",
    ):
        np.save(centroid_dir / f"{category}_centroid.npy", np.array([1.0, 0.0], dtype=float))
    settings = Settings(semantic_centroid_dir=centroid_dir.as_posix())
    service = SemanticCategoryService(settings)

    centroids = service._load_centroids()

    assert set(centroids) == {
        "campus_activity",
        "competition",
        "volunteer",
        "graduate_study",
        "exam_certification",
        "recruitment",
        "lecture",
    }
