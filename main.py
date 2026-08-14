import os
import httpx
from fastapi import FastAPI, HTTPException, Query, Security
from fastapi.security import APIKeyQuery, APIKeyHeader
from fastapi.responses import JSONResponse

app = FastAPI(title="Multi Search API Wrapper")

# Credits Configuration
DEVELOPER_ID = "@wwnlf"
CHANNEL_NAME = "@ix_mrdeath"
CHANNEL_LINK = "https://t.me/ix_mrdeath"
CREDIT_SUPPORT = "@madara_x_support"

# API Key Protection
API_KEY = os.getenv("API_KEY", "baddie")
API_KEY_NAME = "api_key"

api_key_query = APIKeyQuery(name=API_KEY_NAME, auto_error=False)
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Source APIs Configuration
MOBILE_SOURCE_URL = "https://ankan-dey-number-search-api.hf.space/search"
MOBILE_SOURCE_KEY = "Only"

AADHAAR_SOURCE_URL = "https://vtrosint.dpdns.org/api/search/aadhaar"
AADHAAR_SOURCE_KEY = "ftgamer"

def verify_api_key(
    api_key_q: str = Security(api_key_query),
    api_key_h: str = Security(api_key_header)
):
    if api_key_q == API_KEY or api_key_h == API_KEY:
        return True
    raise HTTPException(
        status_code=401, 
        detail={
            "status": "error", 
            "message": "Invalid or Missing API Key.",
            "developer": DEVELOPER_ID,
            "credit": CREDIT_SUPPORT
        }
    )

def mask_id_number(id_str: str) -> str:
    """Masks sensitive ID digits for privacy protection."""
    clean_str = str(id_str).strip()
    if len(clean_str) >= 4:
        return "X" * (len(clean_str) - 4) + clean_str[-4:]
    return "[Redacted]"

@app.get("/")
def home():
    return {
        "status": "running", 
        "developer": DEVELOPER_ID, 
        "channel": CHANNEL_NAME,
        "support": CREDIT_SUPPORT
    }

# 1. Mobile Number Search Endpoint
@app.get("/search")
async def search_mobile(
    mobile: str = Query(..., description="Mobile number to search"),
    authenticated: bool = Security(verify_api_key)
):
    mobile_str = str(mobile).strip()
    
    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            response = await client.get(
                MOBILE_SOURCE_URL, 
                params={"api_key": MOBILE_SOURCE_KEY, "mobile": mobile_str}
            )
        
        if response.status_code == 200:
            res_json = response.json()
            source_data = res_json.get("data") or res_json.get("result")
            
            if source_data:
                records = source_data if isinstance(source_data, list) else [source_data]
                formatted_data = []
                
                for rec in records:
                    raw_id = rec.get("id") or rec.get("aadhar")
                    masked_id = mask_id_number(raw_id) if raw_id else "N/A"
                    
                    formatted_data.append({
                        "mobile": rec.get("mobile", mobile_str),
                        "name": rec.get("name", "N/A"),
                        "father_name": rec.get("fname", "N/A"),
                        "id": masked_id,
                        "address": rec.get("address", "N/A"),
                        "circle": rec.get("circle", "N/A"),
                        "email": rec.get("email", "N/A"),
                        "alt_mobile": rec.get("alt", "N/A")
                    })
                
                return {
                    "status": "success",
                    "system_credits": {
                        "developer": DEVELOPER_ID,
                        "credit": CREDIT_SUPPORT,
                        "channel_link": CHANNEL_LINK
                    },
                    "data": formatted_data
                }
                
        return JSONResponse(
            status_code=404, 
            content={
                "status": "not_found", 
                "message": "Mobile number not found",
                "developer": DEVELOPER_ID
            }
        )
        
    except Exception:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Source server unavailable. Try again later.",
                "developer": DEVELOPER_ID
            }
        )

# 2. Aadhaar Search Endpoint (Cleans Emoji Keys & Formats Data)
@app.get("/search/aadhaar")
async def search_aadhaar(
    id: str = Query(..., description="Target ID to search"),
    authenticated: bool = Security(verify_api_key)
):
    clean_id = str(id).strip()
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                AADHAAR_SOURCE_URL, 
                params={"id": clean_id, "key": AADHAAR_SOURCE_KEY}
            )
        
        if response.status_code == 200:
            res_json = response.json()
            raw_records = res_json.get("data", [])
            
            formatted_records = []
            for item in raw_records:
                # Extract values from keys containing emojis
                mobile_val = item.get("mobile 📱") or item.get("mobile") or "N/A"
                name_val = item.get("name 🫵") or item.get("name") or "N/A"
                fname_val = item.get("father_name 👨‍👦") or item.get("father_name") or "N/A"
                address_val = item.get("address 🏠") or item.get("address") or "N/A"
                alt_val = item.get("alt_mobile 📞") or item.get("alt_mobile") or "N/A"
                circle_val = item.get("circle 🌐") or item.get("circle") or "N/A"
                raw_id_val = item.get("id 🆔") or item.get("id") or clean_id

                formatted_records.append({
                    "mobile": mobile_val,
                    "name": name_val,
                    "father_name": fname_val,
                    "address": address_val,
                    "alt_mobile": alt_val,
                    "circle": circle_val,
                    "id": mask_id_number(raw_id_val)
                })
            
            return {
                "status": "success",
                "system_credits": {
                    "developer": DEVELOPER_ID,
                    "credit": CREDIT_SUPPORT,
                    "channel_link": CHANNEL_LINK
                },
                "total_records": len(formatted_records),
                "data": formatted_records
            }
                
        return JSONResponse(
            status_code=response.status_code, 
            content={
                "status": "not_found", 
                "message": "Record not found or source API error.",
                "developer": DEVELOPER_ID
            }
        )
        
    except Exception:
        return JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "message": "Source server unavailable. Try again later.",
                "developer": DEVELOPER_ID
            }
        )
