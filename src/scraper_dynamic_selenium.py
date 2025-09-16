from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, WebDriverException
import pandas as pd
import time
import os
from typing import List, Dict, Optional

# Constantes
URL = 'https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnpHZ0pGVXlnQVAB?hl=es&gl=ES&ceid=ES%3Aes'
OUTPUT_PATH = './output/google_news_with_selenium.csv'
WAIT_TIME = 5
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# Configura y retorna una instancia del WebDriver de Chrome (previamente instalado en el sistema).
def setup_driver() -> Optional[webdriver.Chrome]:
    try:
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-dev-tools')
        options.add_argument('--no-zygote')
        options.add_argument('--remote-debugging-port=0')
        options.add_argument(f'--user-agent={USER_AGENT}')
        
        options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        options.add_experimental_option('useAutomationExtension', False)
        
        return webdriver.Chrome(options=options)
    except WebDriverException as e:
        print(f"❌ Error configurando el WebDriver: {e}")
        return None

# Intenta aceptar las cookies si aparece el banner.
def accept_cookies(driver: webdriver.Chrome) -> bool:
    try:
        accept_buttons = driver.find_elements(
            By.XPATH, 
            "//button[contains(., 'Aceptar') or contains(., 'Aceptar todo') or contains(., 'Aceptar todas')]"
        )
        
        if accept_buttons:
            accept_buttons[0].click()
            print("✅ Cookies aceptadas")
            time.sleep(2)
            return True
        return False
    except (NoSuchElementException, WebDriverException):
        print("ℹ️ No hay cookies que aceptar")
        return False

# Determina si el elemento debe ser omitido según su contexto.
def should_skip_element(link_element) -> bool:
    try:
        parent_div = link_element.find_element(
            By.XPATH, 
            "./ancestor::div[contains(@class, 'f9uzM')]"
        )
        return parent_div is not None
    except NoSuchElementException:
        return False

# Extrae los datos del artículo desde el elemento del enlace.
def extract_article_data(link_element) -> Optional[Dict]:
    try:
        title = link_element.text.strip()
        if not title or len(title) < 10:
            return None
        
        link = link_element.get_attribute('href')
        if not link:
            return None
        
        # Convertir enlace relativo a absoluto
        if link.startswith('./'):
            link = f'https://news.google.com{link[1:]}'
        
        return {
            'titulo': title,
            'enlace': link
        }
        
    except Exception as e:
        print(f"⚠️ Error extrayendo datos del artículo: {e}")
        return None

# Realiza el scraping de los artículos de noticias.
def scrape_news_articles(driver: webdriver.Chrome) -> List[Dict]:
    print("🔍 Buscando enlaces con clase 'gPFEn'...")
    news_links = driver.find_elements(By.CSS_SELECTOR, "a.gPFEn")
    print(f"✅ Encontrados {len(news_links)} enlaces potenciales")
    
    articles_data = []
    
    for i, link_element in enumerate(news_links, 1):
        try:
            # Saltar elementos no deseados
            if should_skip_element(link_element):
                print(f"⏩ Saltando enlace {i} - Filtrado por div.f9uzM")
                continue
            
            # Extraer datos del artículo
            article_data = extract_article_data(link_element)
            if article_data:
                articles_data.append(article_data)
                print(f"📰 {i}. {article_data['titulo'][:80]}...")
                
        except Exception as e:
            print(f"⚠️ Error procesando enlace {i}: {e}")
            continue
    
    return articles_data

# Guarda los artículos en un archivo CSV.
def save_articles_to_csv(articles_data: List[Dict], output_path: str) -> bool:
    try:
        df = pd.DataFrame(articles_data)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"💾 Datos guardados en: {output_path}")
        return True
    except Exception as e:
        print(f"❌ Error guardando CSV: {e}")
        return False

# Muestra un preview de los resultados.
def display_results(articles_data: List[Dict], num_results: int = 5):
    if not articles_data:
        print("😞 No se encontraron noticias con los filtros aplicados")
        return
    
    print(f"\n🎉 ¡Éxito! Se encontraron {len(articles_data)} noticias")
    print("\n📋 Primeras noticias:")
    
    for i, article in enumerate(articles_data[:num_results], 1):
        print(f"{i}. {article['titulo']}")
        print(f"   🔗 {article['enlace']}")
        print()

# Función principal del script.
def main():
    driver = setup_driver()
    if not driver:
        return
    
    try:
        # Navegar a la URL
        print("🌐 Navegando a Google News...")
        driver.get(URL)
        
        # Esperar carga inicial
        print(f"⏳ Esperando {WAIT_TIME} segundos...")
        time.sleep(WAIT_TIME)
        
        # Manejar cookies
        accept_cookies(driver)
        
        # Scraping de artículos
        articles_data = scrape_news_articles(driver)
        
        # Guardar resultados
        if articles_data:
            success = save_articles_to_csv(articles_data, OUTPUT_PATH)
            if success:
                display_results(articles_data)
        else:
            print("❌ No se encontraron artículos válidos")
            
    except Exception as e:
        print(f"💥 Error durante la ejecución: {e}")
    
    finally:
        # Cerrar driver
        driver.quit()
        print("🔚 Navegador cerrado")

if __name__ == "__main__":
    main()