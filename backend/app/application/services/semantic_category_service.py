from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path

from app.application.classification import CONTENT_CLASSIFICATION_MAX_CHARS, normalize_whitespace
from app.core.config import Settings

_logger = logging.getLogger(__name__)

SEMANTIC_CATEGORIES = (
    "campus_activity",
    "competition",
    "volunteer",
    "graduate_study",
    "exam_certification",
    "recruitment",
    "lecture",
)


@dataclass(slots=True)
class SemanticCategoryDecision:
    category: str
    confidence: str
    top_category: str
    top_score: float
    second_category: str
    second_score: float
    margin: float
    scores: dict[str, float]
    reason: str = ""

    @property
    def is_high_confidence(self) -> bool:
        return self.confidence == "high"


def _split_text(text: str, *, max_chars: int = 240) -> list[str]:
    normalized = normalize_whitespace(text)
    if not normalized:
        return []
    pieces = [
        piece.strip()
        for piece in re.split(r"(?<=[。！？!?；;])\s*|\n+", normalized)
        if piece.strip()
    ]
    chunks: list[str] = []
    current = ""
    for piece in pieces:
        if not current:
            current = piece
            continue
        if len(current) + len(piece) + 1 <= max_chars:
            current = f"{current} {piece}"
        else:
            chunks.append(current)
            current = piece
    if current:
        chunks.append(current)
    return chunks


class SemanticCategoryService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._model = None
        self._centroids = None
        self._disabled_reason = ""

    def classify(self, *, title: str, summary: str = "", content: str = "") -> SemanticCategoryDecision:
        text = normalize_whitespace(f"{title} {summary} {(content or '')[:CONTENT_CLASSIFICATION_MAX_CHARS]}")
        if not text:
            return self._empty_decision("empty_text")
        if not self.settings.semantic_enabled:
            return self._empty_decision("semantic_disabled")

        centroids = self._load_centroids()
        if not centroids:
            return self._empty_decision(self._disabled_reason or "no_centroids")

        model = self._load_model()
        if model is None:
            return self._empty_decision(self._disabled_reason or "model_unavailable")

        chunks = _split_text(text)
        if not chunks:
            return self._empty_decision("empty_chunks")

        try:
            import numpy as np

            embeddings = model.encode(
                chunks,
                batch_size=8,
                normalize_embeddings=True,
                convert_to_numpy=True,
                show_progress_bar=False,
            )
            article_vector = embeddings.mean(axis=0)
            article_vector = article_vector / np.clip(np.linalg.norm(article_vector), 1e-12, None)
            scores = {
                category: float(article_vector @ centroid)
                for category, centroid in centroids.items()
            }
        except Exception as exc:  # noqa: BLE001
            _logger.warning("semantic classification failed: %s", exc)
            return self._empty_decision("semantic_failed")

        ranked = sorted(scores, key=lambda category: (-scores[category], category))
        top_category = ranked[0]
        second_category = ranked[1] if len(ranked) > 1 else "other"
        top_score = scores[top_category]
        second_score = scores.get(second_category, 0.0)
        margin = top_score - second_score
        is_high_confidence = (
            top_score >= self.settings.semantic_accept_threshold
            and margin >= self.settings.semantic_margin_threshold
        )
        return SemanticCategoryDecision(
            category=top_category if is_high_confidence else "other",
            confidence="high" if is_high_confidence else "low",
            top_category=top_category,
            top_score=top_score,
            second_category=second_category,
            second_score=second_score,
            margin=margin,
            scores=scores,
            reason="semantic_confident" if is_high_confidence else "semantic_unclear",
        )

    def _load_model(self):
        if self._model is not None:
            return self._model
        try:
            os.environ.setdefault("HF_HUB_OFFLINE", "1")
            os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
            from sentence_transformers import SentenceTransformer

            model_name = self.settings.semantic_model
            local_model_path = self._resolve_local_model_path(model_name)
            self._model = SentenceTransformer(local_model_path or model_name, device="cpu")
        except Exception as exc:  # noqa: BLE001
            self._disabled_reason = "model_unavailable"
            _logger.warning("semantic model unavailable: %s", exc)
            return None
        return self._model

    def _resolve_local_model_path(self, model_name: str) -> str:
        if "/" not in model_name:
            return ""
        cache_root = Path.home() / ".cache" / "huggingface" / "hub"
        model_dir = cache_root / f"models--{model_name.replace('/', '--')}"
        refs_main = model_dir / "refs" / "main"
        if not refs_main.exists():
            return ""
        revision = refs_main.read_text(encoding="utf-8").strip()
        snapshot = model_dir / "snapshots" / revision
        return snapshot.as_posix() if snapshot.exists() else ""

    def _load_centroids(self):
        if self._centroids is not None:
            return self._centroids
        try:
            import numpy as np
        except Exception as exc:  # noqa: BLE001
            self._disabled_reason = "numpy_unavailable"
            _logger.warning("semantic numpy unavailable: %s", exc)
            self._centroids = {}
            return self._centroids

        centroid_dir = Path(self.settings.semantic_centroid_dir or ".run/embeddings")
        centroids = {}
        for category in SEMANTIC_CATEGORIES:
            path = centroid_dir / f"{category}_centroid.npy"
            if not path.exists():
                continue
            vector = np.load(path)
            vector = vector / np.clip(np.linalg.norm(vector), 1e-12, None)
            centroids[category] = vector
        if not centroids:
            self._disabled_reason = "no_centroids"
        self._centroids = centroids
        return self._centroids

    def _empty_decision(self, reason: str) -> SemanticCategoryDecision:
        return SemanticCategoryDecision(
            category="other",
            confidence="low",
            top_category="other",
            top_score=0.0,
            second_category="other",
            second_score=0.0,
            margin=0.0,
            scores={},
            reason=reason,
        )
