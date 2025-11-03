import trafilatura

def get_website_text_content(url: str) -> str:
    """
    This function takes a url and returns the main text content of the website.
    The text content is extracted using trafilatura and easier to understand.
    The results is not directly readable, better to be summarized by LLM before consume
    by the user.
    
    Reference: web_scraper blueprint integration
    
    Some common website to crawl information from:
    - Financial news sites
    - Company earnings reports
    - Industry analysis pages
    """
    downloaded = trafilatura.fetch_url(url)
    text = trafilatura.extract(downloaded)
    return text if text else ""
