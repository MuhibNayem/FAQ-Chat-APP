from typing import List
from sentence_transformers import SentenceTransformer
from src.core.config import settings

class EmbeddingService:
    def __init__(self):
        self.model = SentenceTransformer(
            'sentence-transformers/all-MiniLM-L6-v2',
            device='cuda' if settings.USE_GPU else 'cpu'
        )
        self.model.max_seq_length = 256

    async def batch_embed(self, texts: List[str]) -> List[List[float]]:
        embeddings = self.model.encode(
            texts,
            batch_size=settings.MODEL_BATCH_SIZE,
            convert_to_numpy=True,
            normalize_embeddings=True
        )
        return embeddings.tolist()