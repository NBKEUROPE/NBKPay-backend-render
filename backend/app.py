from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from main.auth import router as auth_router
from main.terminals import router as terminals_router
from main.payouts import router as payouts_router
from main.iso8583 import router as iso8583_router
from main.receipts import router as receipts_router
from main.history import router as history_router
from main.limits import router as limits_router

app = FastAPI(
    title="NBK Pay API",
    version="1.0.0",
    description="NBK Pay: Card Payment, Crypto Payout, Admin & Terminal Management"
)

# CORS setup for frontend/mobile
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Set to your frontend domain in production!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers for each main module
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])
app.include_router(terminals_router, prefix="/terminals", tags=["Terminals"])
app.include_router(payouts_router, prefix="/payouts", tags=["Payouts"])
app.include_router(iso8583_router, prefix="/iso8583", tags=["Card Logic"])
app.include_router(receipts_router, prefix="/receipts", tags=["Receipts"])
app.include_router(history_router, prefix="/history", tags=["History"])
app.include_router(limits_router, prefix="/limits", tags=["Limits"])

@app.get("/")
def root():
    return {"msg": "NBK Pay backend is running."}
