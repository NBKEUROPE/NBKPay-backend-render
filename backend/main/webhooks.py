from fastapi import APIRouter, Request, HTTPException
import logging

router = APIRouter()

@router.post("/payment-callback")
async def payment_callback(request: Request):
    data = await request.json()
    # Validate source/IP/signature as needed
    # Process callback, update transaction status
    logging.info(f"Received payment callback: {data}")
    # Example: data = {"reference":"...", "status":"Paid", ...}
    # Find transaction and update status if needed
    return {"msg": "Callback received"}
