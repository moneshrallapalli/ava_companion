from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from ai_companion.settings import settings
from qdrant_client.models import VectorParams, PointStruct
import uuid

class VectorStore:
    COLLECTION_NAME="ava_memories"
    SIMILARITY_THRESHOLD = 0.9
    def _ensure_collection(self):
        if not self.client.collection_exists(self.COLLECTION_NAME):
            vector_size = len(self.model.encode("test"))
            self.client.create_collection(
                collection_name=self.COLLECTION_NAME,
                vectors_config = VectorParams(size= vector_size, distance = "Cosine")
            )
    
    def store_memory(self, text, metadata=None):
        if metadata is None:
            metadata = {}
        vector = self.model.encode(text).tolist()
        payload = {"text": text, **metadata}
        self.client.upsert(collection_name= self.COLLECTION_NAME, points= [PointStruct(id=str(uuid.uuid4()), vector=vector, payload=payload  )])

    def search_memories(self, query, limit = 5):
        query_vector = self.model.encode(query).tolist()
        results = self.client.query_points(
            collection_name =  self.COLLECTION_NAME,
            query = query_vector,
            limit = limit,
        )
        return [
            {
                "text": hit.payload["text"],
                "score": hit.score,
                "metadata": hit.payload,
            }
            for hit in results.points
        ]
    def find_similar_memory(self,text):
        results = self.search_memories(text,limit = 1)
        if results and results[0]["score"] >= self.SIMILARITY_THRESHOLD:
            return results[0]
        return None

    def __init__(self):
        self.client = QdrantClient(url=settings.QDRANT_URL, api_key = settings.QDRANT_API_KEY)
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self._ensure_collection()

