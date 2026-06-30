from bs4 import BeautifulSoup

def parse_books(html_content: str) -> list[dict]:
    """Extrae la información de los libros del HTML."""
    print("[Parser] Extrayendo datos del HTML...")
    soup = BeautifulSoup(html_content, 'html.parser')
    books_data = []
    
    articles = soup.find_all('article', class_='product_pod')
    for article in articles:
        title = article.h3.a['title']
        price = article.find('p', class_='price_color').text
        stock = article.find('p', class_='instock availability').text.strip()
        
        books_data.append({
            'title': title,
            'price': price,
            'stock': stock
        })
        
    return books_data