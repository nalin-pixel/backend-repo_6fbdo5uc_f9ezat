import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from database import db, create_document
from schemas import Lead

app = FastAPI(title="Weight Loss Course API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Weight Loss API running"}

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }
    try:
        if db is not None:
            response["database"] = "✅ Connected & Working"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"
    return response

class LeadIn(BaseModel):
    name: str
    email: str
    product_tier: str
    message: str | None = None

VALID_TIERS = {"pdf", "course", "course_coach"}

@app.post("/leads")
def create_lead(lead: LeadIn):
    if lead.product_tier not in VALID_TIERS:
        raise HTTPException(status_code=400, detail="Invalid product tier")
    lead_doc = Lead(**lead.model_dump())
    lead_id = create_document("lead", lead_doc)
    return {"id": lead_id, "status": "ok"}
