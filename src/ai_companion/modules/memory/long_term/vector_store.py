from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
from typing import List, Optional
import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer

from ai_companion.settings import settings


@dataclass
class Memory:
    """A memory entry returned from vector search."""

    text: str
    metadata: dict
    score: Optional[float] = None

    @property
    def id(self) -> Optional[str]:
        return self.metadata.get("id")

    @property
    def timestamp(self) -> Optional[datetime]:
        ts = self.metadata.get("timestamp")
        return datetime.fromisoformat(ts) if ts else None


class VectorStore:
    """Qdrant-backed store for long-term memory embeddings."""

    REQUIRED_ENV_VARS = ["QDRANT_URL", "QDRANT_API_KEY"]
    EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    COLLECTION_NAME = "ava_memories"
    SIMILARITY_THRESHOLD = 0.9

    def __init__(self) -> None:
        self._validate_env_vars()
        self.client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)
        self.model = SentenceTransformer(self.EMBEDDING_MODEL)
        self._ensure_collection()

    def _validate_env_vars(self) -> None:
        missing = [var for var in self.REQUIRED_ENV_VARS if not getattr(settings, var)]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

    def _ensure_collection(self) -> None:
        if self.client.collection_exists(self.COLLECTION_NAME):
            return

        vector_size = len(self.model.encode("sample text"))
        self.client.create_collection(
            collection_name=self.COLLECTION_NAME,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )

    def store_memory(self, text: str, metadata: Optional[dict] = None) -> None:
        if metadata is None:
            metadata = {}

        similar_memory = self.find_similar_memory(text)
        if similar_memory and similar_memory.id:
            metadata["id"] = similar_memory.id

        point_id = metadata.get("id", str(uuid.uuid4()))
        vector = self.model.encode(text).tolist()
        payload = {"text": text, **metadata}

        self.client.upsert(
            collection_name=self.COLLECTION_NAME,
            points=[PointStruct(id=point_id, vector=vector, payload=payload)],
        )

    def search_memories(self, query: str, k: int = 5) -> List[Memory]:
        if not self.client.collection_exists(self.COLLECTION_NAME):
            return []

        query_vector = self.model.encode(query).tolist()
        results = self.client.query_points(
            collection_name=self.COLLECTION_NAME,
            query=query_vector,
            limit=k,
        )

        return [
            Memory(
                text=hit.payload["text"],
                metadata={key: value for key, value in hit.payload.items() if key != "text"},
                score=hit.score,
            )
            for hit in results.points
        ]

    def find_similar_memory(self, text: str) -> Optional[Memory]:
        results = self.search_memories(text, k=1)
        if results and results[0].score is not None and results[0].score >= self.SIMILARITY_THRESHOLD:
            return results[0]
        return None


@lru_cache
def get_vector_store() -> VectorStore:
    return VectorStore()
