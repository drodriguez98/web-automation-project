import time
import os
import pandas as pd
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException, WebDriverException

# Constantes,
URL = "https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnpHZ0pGVXlnQVAB?hl=es&gl=ES&ceid=ES%3Aes"
OUTPUT_PATH = "./output/google_news.csv"
WAIT_TIME = 5
USER_AGENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Configura y devuelve una instancia de Chrome WebDriver.
def setup_driver() -> Optional[webdriver.Chrome]:
    try:
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument(f"--user-agent={USER_AGENT}")
        options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        options.add_experimental_option("useAutomationExtension", False)
        return webdriver.Chrome(options=options)
    except WebDriverException as e:
        print(f"❌ Error configurando WebDriver: {e}")
        return None

# Intenta aceptar cookies si aparece el banner.
def accept_cookies(driver: webdriver.Chrome):
    try:
        button = driver.find_element(By.XPATH, "//button[contains(., 'Aceptar')]")
        button.click()
        print("✅ Cookies aceptadas")
        time.sleep(2)
    except NoSuchElementException:
        pass

# Extrae artículos de Google News usando Selenium.
def scrape_articles(driver: webdriver.Chrome) -> List[Dict]:
    articles = []
    news_links = driver.find_elements(By.CSS_SELECTOR, "a.gPFEn")
    print(f"✅ Encontrados {len(news_links)} enlaces potenciales")

    for i, link in enumerate(news_links, 1):
        try:
            # Saltar si está dentro de div.f9uzM (contenido no deseado)
            try:
                link.find_element(By.XPATH, "./ancestor::div[contains(@class, 'f9uzM')]")
                continue
            except NoSuchElementException:
                pass

            title = link.text.strip()
            href = link.get_attribute("href")
            if not title or not href:
                continue

            if href.startswith("./"):
                href = f"https://news.google.com{href[1:]}"

            articles.append({"title": title, "link": href})
            # print(f"📰 {i}. {title[:80]}...")

        except Exception as e:
            print(f"⚠️ Error procesando enlace {i}: {e}")

    return articles

# Guarda artículos en CSV.
def save_to_csv(data: List[Dict], path: str):
    if not data:
        print("😞 No hay datos para guardar")
        return

    df = pd.DataFrame(data)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False, encoding="utf-8")
    print(f"💾 Datos guardados en: {path}")

# Función principal.
def main():
    driver = setup_driver()
    if not driver:
        return

    try:
        print("🌐 Abriendo Google News...")
        driver.get(URL)
        time.sleep(WAIT_TIME)

        accept_cookies(driver)
        articles = scrape_articles(driver)
        save_to_csv(articles, OUTPUT_PATH)

    except Exception as e:
        print(f"💥 Error en la ejecución: {e}")

    finally:
        driver.quit()
        print("🔚 Navegador cerrado")


if __name__ == "__main__":
    main()