import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
from typing import List, Dict, Optional

# Constantes
URL = 'https://www.marketingdive.com/news/'
HEADERS = { 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36' }
OUTPUT_PATH = './output/marketing_dive_news_beautifulsoup.csv'
TIMEOUT = 10

# Obtiene y parsea el contenido HTML de la URL especificada.
def fetch_html_content(url: str, headers: dict, timeout: int) -> Optional[BeautifulSoup]:
    try:
        print("📡 Haciendo petición a Marketing Dive...")
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'html.parser')
    except requests.exceptions.RequestException as e:
        print(f"❌ Error en la petición HTTP: {e}")
        return None

# Extrae y filtra los artículos de noticias del HTML.
def extract_news_articles(soup: BeautifulSoup) -> List[BeautifulSoup]:
    # Contenedor con la sección "Últimas noticias"
    feed_container = soup.find('ul', class_='feed layout-stack-xxl')
    
    if not feed_container:
        raise ValueError("No se encontró el contenedor principal de noticias")
    
    # Identificar todos los elementos 'li' de la sección    
    articles = feed_container.find_all('li', class_='row feed__item')
    
    # Filtrar anuncios (excluir elementos con clase 'feed-item-ad')
    news_articles = [
        article for article in articles 
        if 'feed-item-ad' not in article.get('class', [])
    ]
    
    print(f"✅ Se encontraron {len(news_articles)} artículos de noticias")
    return news_articles

# Extrae y procesa los datos de un artículo individual.
def parse_article_data(article: BeautifulSoup) -> Optional[Dict]:
    try:
        # Extraer título
        title_element = article.find('h3', class_='feed__title')
        if not title_element:
            return None
        
        title = title_element.get_text(strip=True)
        
        # Extraer enlace
        link_element = title_element.find('a')
        if not link_element or not link_element.get('href'):
            return None
        
        link = link_element['href']
        if not link.startswith('http'):
            link = f'https://www.marketingdive.com{link}'
        
        # Extraer descripción
        description_element = article.find('p', class_='feed__description')
        description = description_element.get_text(strip=True) if description_element else ''
        
        # Extraer categoría
        topic_element = article.find('a', class_='topic-tag')
        category = topic_element.get_text(strip=True) if topic_element else ''
        
        return {
            'headline': title,
            'link': link,
            'description': description,
            'category': category
        }
        
    except Exception as e:
        print(f"⚠️ Error procesando artículo: {e}")
        return None

# Guarda los datos en un archivo CSV.
def save_to_csv(data: List[Dict], output_path: str) -> bool:
    try:
        df = pd.DataFrame(data)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"💾 Datos guardados en: {output_path}")
        return True
    except Exception as e:
        print(f"❌ Error guardando CSV: {e}")
        return False

# Muestra un preview de los resultados.
def display_results(df: pd.DataFrame, num_results: int = 5):
    print(f"\n📊 Total de noticias extraídas: {len(df)}")
    print("\n📋 Primeras noticias:")
    print(df[['headline', 'category']].head(num_results).to_string(index=False))

# Función principal del script.
def main():
    try:
        # Obtener contenido HTML
        soup = fetch_html_content(URL, HEADERS, TIMEOUT)
        if not soup:
            return
        
        # Extraer artículos
        articles = extract_news_articles(soup)
        
        # Procesar cada artículo
        news_data = []
        for article in articles:
            article_data = parse_article_data(article)
            if article_data:
                news_data.append(article_data)
        
        # Guardar resultados
        if news_data:
            success = save_to_csv(news_data, OUTPUT_PATH)
            if success:
                df = pd.DataFrame(news_data)
                display_results(df)
        else:
            print("❌ No se pudieron extraer artículos válidos")
            
    except ValueError as e:
        print(f"❌ Error de datos: {e}")
    except Exception as e:
        print(f"💥 Error inesperado: {e}")

if __name__ == "__main__":
    main()