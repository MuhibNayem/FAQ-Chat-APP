from typing import List
import numpy as np
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
from src.core.config import settings

class ClassificationService:
    def __init__(self):
        self.model = AutoModelForSequenceClassification.from_pretrained(
            "typeform/distilbert-base-uncased-mnli"
        )
        self.tokenizer = AutoTokenizer.from_pretrained(
            "typeform/distilbert-base-uncased-mnli"
        )
        self.pipe = pipeline(
            "zero-shot-classification",
            model=self.model,
            tokenizer=self.tokenizer,
            device=0,
            framework="pt"
        )

    async def batch_classify(self, texts: List[str]) -> List[bool]:
        results = self.pipe(
            texts,
            candidate_labels=["company related", "off topic"],
            multi_label=False,
            batch_size=settings.MODEL_BATCH_SIZE
        )
        return [r['labels'][0] == 'company related' and r['scores'][0] > 0.85 for r in results]