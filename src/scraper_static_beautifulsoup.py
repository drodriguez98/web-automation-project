import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

# Constantes
URL = 'https://www.marketingdive.com/news/'
HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'}
OUTPUT_PATH = './output/marketing_dive_news.csv'

# Descarga la página y devuelve una lista de noticias parseadas.
def fetch_articles():
    print("🌐 Intentando descargar enlaces desde Marketing Dive...")
    try:
        response = requests.get(URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        container = soup.find('ul', class_='feed layout-stack-xxl')
        if not container:
            return []

        articles = container.find_all('li', class_='row feed__item')
        results = []

        for art in articles:
            if 'feed-item-ad' in art.get('class', []):  # Filtrar anuncios
                continue

            title_element = art.find('h3', class_='feed__title')
            link_element = title_element.find('a') if title_element else None
            if not title_element or not link_element or not link_element.get('href'):
                continue

            link = link_element['href']
            if not link.startswith('http'):
                link = f'https://www.marketingdive.com{link}'

            results.append({
                'title': title_element.get_text(strip=True),
                'link': link,
                'description': art.find('p', class_='feed__description').get_text(strip=True)
                if art.find('p', class_='feed__description') else '',
                'category': art.find('a', class_='topic-tag').get_text(strip=True)
                if art.find('a', class_='topic-tag') else ''
            })
        
        print(f"Encontrados {len(results)} enlaces")

        return results

    except requests.RequestException as e:
        print(f" ❌ Error de conexión: {e}")
        return []

# Guarda los datos en un archivo CSV.
def save_to_csv(data, path):
    if not data:
        print("❌ No hay datos para guardar.")
        return

    df = pd.DataFrame(data)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
    print(f"💾 Datos guardados en: {path}")

# Función principal.
def main():
    news_data = fetch_articles()
    save_to_csv(news_data, OUTPUT_PATH)


if __name__ == "__main__":
    main()