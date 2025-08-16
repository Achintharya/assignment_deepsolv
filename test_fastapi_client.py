from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_fetch_insights():
    url = "https://memy.co.in"  # Example Shopify store
    response = client.post("/fetch-insights", json={"website_url": url})
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())

if __name__ == "__main__":
    test_fetch_insights()
