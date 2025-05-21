from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from src.routes.chat import router as chat_router
from src.models.vector_db import VectorDB

app = FastAPI()

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router, prefix="/api/v1")


@app.on_event("startup")
async def startup():
    await VectorDB.get_pool()

@app.on_event("shutdown")
async def shutdown():
    await VectorDB.close_pool()
    
@app.get("/healthcheck")
async def healthcheck():
    return Response(status_code=200)
    
@app.get("/")
async def applicant_service():
    return {
        "service": "FAQ chat Service",
        "version": "1.0.0",
    }