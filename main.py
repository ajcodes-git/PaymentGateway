from fastapi import FastAPI, HTTPException
from app.schemas.payment import PaymentRequest
from app.utils.config import settings
from app.db.session import check_db_connection
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.app_client_api import router as app_client_router
from app.api.v1.transaction_api import router as transaction_router


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    #allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(app_client_router, prefix=f"{settings.API_V1_STR}/app_client", tags=["App Client"])
app.include_router(transaction_router, prefix=f"{settings.API_V1_STR}/payment", tags=["Payment"])


@app.on_event("startup")
async def startup_event():
    check_db_connection()

@app.get("/")
def root():
    return {
        "message": "Welcome to Doos Logistics API",
        "version": settings.VERSION,
        "docs_url": f"/docs"
    } 