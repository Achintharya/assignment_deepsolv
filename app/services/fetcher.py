import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from crawl4ai import Crawler
from app.models import BrandContext, Product, Policy, FAQ, SocialHandle, ContactInfo

class ShopifyFetcher:
    def __init__(self, website_url: str):
        self.website_url = website_url.rstrip('/')
        self.session = requests.Session()
        self.crawler = Crawler()

    def get_all_insights(self) -> dict:
        context = BrandContext()
        context.brand_name = self._get_brand_name()
        context.product_catalog = self._get_product_catalog()
        context.hero_products = self._get_hero_products()
        context.policies = self._get_policies()
        context.faqs = self._get_faqs()
        context.social_handles = self._get_social_handles()
        context.contact_info = self._get_contact_info()
        context.about = self._get_about()
        context.important_links = self._get_important_links()
        return context.dict()

    def _get_brand_name(self):
        try:
            resp = self.session.get(self.website_url, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            if soup.title:
                return soup.title.text.strip()
        except Exception:
            pass
        return None

    def _get_product_catalog(self):
        try:
            url = urljoin(self.website_url, '/products.json')
            resp = self.session.get(url, timeout=10)
            if resp.status_code == 200:
                products = resp.json().get('products', [])
                return [Product(id=str(p.get('id')), title=p.get('title'), url=urljoin(self.website_url, f"/products/{p.get('handle')}") if p.get('handle') else None, image=p.get('images')[0]['src'] if p.get('images') else None, price=str(p.get('variants')[0]['price']) if p.get('variants') else None) for p in products]
        except Exception:
            pass
        return []

    def _get_hero_products(self):
        try:
            resp = self.session.get(self.website_url, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            hero_products = []
            for a in soup.select('a[href*="/products/"]'):
                title = a.get('title') or a.text.strip()
                href = a.get('href')
                if href and title:
                    url = urljoin(self.website_url, href)
                    hero_products.append(Product(id=title, title=title, url=url))
            return hero_products[:10]  # Limit to 10 hero products
        except Exception:
            pass
        return []

    def _get_policies(self):
        policies = []
        policy_types = ['privacy', 'refund', 'return']
        for ptype in policy_types:
            try:
                url = urljoin(self.website_url, f'/{ptype}-policy')
                resp = self.session.get(url, timeout=10)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    content = soup.get_text(separator=' ', strip=True)
                    policies.append(Policy(type=ptype, url=url, content=content))
            except Exception:
                continue
        return policies

    def _get_faqs(self):
        faqs = []
        try:
            # Try common FAQ URLs
            for path in ['/pages/faq', '/pages/faqs', '/faq', '/faqs']:
                url = urljoin(self.website_url, path)
                resp = self.session.get(url, timeout=10)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    for q in soup.find_all(['h2', 'h3', 'strong']):
                        question = q.text.strip()
                        answer = ''
                        next_sib = q.find_next_sibling()
                        if next_sib:
                            answer = next_sib.text.strip()
                        if question and answer:
                            faqs.append(FAQ(question=question, answer=answer))
                    if faqs:
                        break
        except Exception:
            pass
        return faqs

    def _get_social_handles(self):
        handles = []
        try:
            resp = self.session.get(self.website_url, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            for a in soup.find_all('a', href=True):
                href = a['href']
                for platform in ['instagram', 'facebook', 'tiktok', 'twitter', 'youtube', 'linkedin']:
                    if platform in href:
                        handles.append(SocialHandle(platform=platform, url=href))
        except Exception:
            pass
        return handles

    def _get_contact_info(self):
        info = ContactInfo()
        try:
            resp = self.session.get(self.website_url, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            text = soup.get_text(separator=' ', strip=True)
            import re
            emails = re.findall(r'[\w\.-]+@[\w\.-]+', text)
            phones = re.findall(r'\+?\d[\d\s\-]{7,}\d', text)
            info.emails = list(set(emails))
            info.phones = list(set(phones))
        except Exception:
            pass
        return info

    def _get_about(self):
        try:
            for path in ['/pages/about', '/about', '/about-us']:
                url = urljoin(self.website_url, path)
                resp = self.session.get(url, timeout=10)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    return soup.get_text(separator=' ', strip=True)
        except Exception:
            pass
        return None

    def _get_important_links(self):
        links = {}
        try:
            resp = self.session.get(self.website_url, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            for a in soup.find_all('a', href=True):
                text = a.text.strip().lower()
                href = a['href']
                if any(key in text for key in ['order', 'track', 'contact', 'blog']):
                    links[text] = urljoin(self.website_url, href)
        except Exception:
            pass
        return links
