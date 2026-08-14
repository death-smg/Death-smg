import os
import httpx
from fastapi import FastAPI, HTTPException, Query, Security
from fastapi.security import APIKeyQuery, APIKeyHeader
from fastapi.responses import JSONResponse

app = FastAPI(title="Aadhaar Search API Wrapper")

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

# Source API Config
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

@app.get("/")
def home():
    return {
        "status": "running", 
        "service": "Aadhaar Lookup API",
        "developer": DEVELOPER_ID, 
        "channel": CHANNEL_NAME,
        "support": CREDIT_SUPPORT
    }

@app.get("/search")
async def search_aadhaar(
    id: str = Query(..., description="Target ID to search"),
    authenticated: bool = Security(verify_api_key)
):
    clean_id = str(id).strip()
    
    try:
        # Timeout 25 seconds for slow response handling
        async with httpx.AsyncClient(timeout=25.0) as client:
            response = await client.get(
                AADHAAR_SOURCE_URL, 
                params={"id": clean_id, "key": AADHAAR_SOURCE_KEY}
            )
        
        if response.status_code == 200:
            res_json = response.json()
            raw_records = res_json.get("data", [])
            
            if not raw_records:
                return JSONResponse(
                    status_code=404, 
                    content={
                        "status": "not_found", 
                        "message": "No record found in source database for this ID.",
                        "developer": DEVELOPER_ID
                    }
                )

            formatted_records = []
            for item in raw_records:
                mobile_val = item.get("mobile 📱") or item.get("mobile") or "N/A"
                name_val = item.get("name 🫵") or item.get("name") or "N/A"
                fname_val = item.get("father_name 👨‍👦") or item.get("father_name") or "N/A"
                address_val = item.get("address 🏠") or item.get("address") or "N/A"
                alt_val = item.get("alt_mobile 📞") or item.get("alt_mobile") or "N/A"
                circle_val = item.get("circle 🌐") or item.get("circle") or "N/A"

                formatted_records.append({
                    "mobile": mobile_val,
                    "name": name_val,
                    "father_name": fname_val,
                    "address": address_val,
                    "alt_mobile": alt_val,
                    "circle": circle_val,
                    "id": "[Redacted for Privacy]"
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
                "message": "Source server unavailable or timed out.",
                "developer": DEVELOPER_ID
            }
        )
