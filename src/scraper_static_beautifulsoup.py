import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import os  # Importar os para manejar rutas

# URL objetivo
url = 'https://www.marketingdive.com/news/'

# Headers para simular un navegador web y evitar bloqueos
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

try:
    # Hacer la petición HTTP
    print("Haciendo petición a Marketing Dive...")
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Lanza un error para códigos HTTP 4xx/5xx

    # Parsear el HTML con BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # Encontrar el contenedor principal de noticias
    feed_container = soup.find('ul', class_='feed layout-stack-xxl')

    if not feed_container:
        raise Exception("No se encontró el contenedor de noticias")

    # Encontrar todos los elementos de noticias (ignorar anuncios con class 'feed-item-ad')
    articles = feed_container.find_all('li', class_='row feed__item')

    # Filtrar para excluir anuncios (algunos pueden tener clases adicionales)
    news_articles = [article for article in articles if 'feed-item-ad' not in article.get('class', [])]

    print(f"Se encontraron {len(news_articles)} artículos de noticias")

    data = []
    for article in news_articles:
        try:
            # Extraer el título - está en un h3 con clase 'feed__title'
            title_element = article.find('h3', class_='feed__title')
            if not title_element:
                continue

            title = title_element.get_text(strip=True)

            # Extraer el enlace
            link_element = title_element.find('a')
            if not link_element or not link_element.get('href'):
                continue

            link = link_element['href']

            # Asegurar que el enlace sea absoluto
            if link and not link.startswith('http'):
                link = 'https://www.marketingdive.com' + link

            # Extraer la descripción (si existe)
            description_element = article.find('p', class_='feed__description')
            description = description_element.get_text(strip=True) if description_element else ''

            # Extraer categoría/topic (si existe)
            topic_element = article.find('a', class_='topic-tag')
            topic = topic_element.get_text(strip=True) if topic_element else ''

            data.append({
                'headline': title,
                'link': link,
                'description': description,
                'category': topic
            })

        except Exception as e:
            print(f"Error procesando un artículo: {e}")
            continue

    # Crear un DataFrame y guardar en CSV en la carpeta output
    if data:
        df = pd.DataFrame(data)
        
        # Definir la ruta completa del archivo en la carpeta output
        output_path = '../output/marketing_dive_news_beautifulsoup.csv'
        
        # Guardar en la carpeta output
        df.to_csv(output_path, index=False)
        print(f"¡Éxito! Se extrajeron {len(data)} artículos y se guardaron en '{output_path}'")
        print("\nPrimeras 5 noticias:")
        print(df[['headline', 'category']].head().to_string(index=False))
    else:
        print("No se pudieron extraer artículos. Puede que la estructura del sitio haya cambiado.")

except requests.exceptions.RequestException as e:
    print(f"Error en la petición HTTP: {e}")
except Exception as e:
    print(f"Error inesperado: {e}")
