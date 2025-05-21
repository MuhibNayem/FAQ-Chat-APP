from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from src.core.security import validate_api_key
from src.schemas.chat import ChatRequest, ChatResponse
from src.services.classifier import ClassificationService
from src.services.embedding import EmbeddingService
from src.models.vector_db import VectorDB
from src.services.llm import BedrockClient
from src.core.config import settings
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)
classifier = ClassificationService()
embedder = EmbeddingService()
llm = BedrockClient()

@router.post("/chat", response_model=ChatResponse)
@limiter.limit(settings.RATE_LIMIT)
async def chat_endpoint(request: ChatRequest, api_key: str = Depends(validate_api_key)):
    try:
        try:
            is_relevant = (await classifier.batch_classify([request.query]))[0]
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Classification service error: {str(e)}"
            ) from e

        if not is_relevant:
            return ChatResponse(
                status="success",
                reply="I specialize in CompanyName questions. How can I help?",
                timestamp=datetime.now()
            )

        try:
            embedding = (await embedder.batch_embed([request.query]))[0]
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Embedding generation failed: {str(e)}"
            ) from e

        try:
            results = await VectorDB.search(embedding)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"VectorDB search failed: {str(e)}"
            ) from e

        if not results:
            return ChatResponse(
                status="success",
                reply="I don't have information on that topic.",
                timestamp=datetime.now()
            )

        context = "\n".join([r['content'] for r in results])
        try:
            response = await llm.generate(context, request.query)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Response generation failed: {str(e)}"
            ) from e

        return ChatResponse(
            status="success",
            reply=response,
            timestamp=datetime.now()
        )

    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Unexpected server error: {str(e)}"
        ) from e