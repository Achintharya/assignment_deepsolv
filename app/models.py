from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict

class Product(BaseModel):
    id: str
    title: str
    url: Optional[str]
    image: Optional[str]
    price: Optional[str]
    # Add more fields as needed

class Policy(BaseModel):
    type: str
    url: Optional[str]
    content: Optional[str]

class FAQ(BaseModel):
    question: str
    answer: str

class SocialHandle(BaseModel):
    platform: str
    url: str

class ContactInfo(BaseModel):
    emails: List[str] = []
    phones: List[str] = []

class BrandContext(BaseModel):
    brand_name: Optional[str]
    about: Optional[str]
    product_catalog: List[Product] = []
    hero_products: List[Product] = []
    policies: List[Policy] = []
    faqs: List[FAQ] = []
    social_handles: List[SocialHandle] = []
    contact_info: ContactInfo = ContactInfo()
    important_links: Dict[str, str] = {}
