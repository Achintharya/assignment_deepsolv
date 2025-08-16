from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, HttpUrl
from app.services.fetcher import ShopifyFetcher
from fastapi.responses import JSONResponse

app = FastAPI(title="Shopify Store Insights-Fetcher")

class InsightsRequest(BaseModel):
    website_url: HttpUrl

@app.post("/fetch-insights")
def fetch_insights(request: InsightsRequest):
    try:
        fetcher = ShopifyFetcher(request.website_url)
        data = fetcher.get_all_insights()
        if not data:
            raise HTTPException(status_code=401, detail="Website not found or not a Shopify store.")
        return JSONResponse(content=data)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
