from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time

# Configuración MÍNIMA de Chrome - sin conexiones externas
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-dev-tools')
options.add_argument('--no-zygote')
options.add_argument('--remote-debugging-port=0')
options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

# Evitar que intente descargar nada de internet
options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
options.add_experimental_option('useAutomationExtension', False)

# Inicializar driver SIN conexiones externas
driver = webdriver.Chrome(options=options)

try:
    print("🌐 Navegando a Google News...")
    driver.get('https://news.google.com/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGx1YlY4U0FtVnpHZ0pGVXlnQVAB?hl=es&gl=ES&ceid=ES%3Aes')
    
    print("⏳ Esperando 5 segundos...")
    time.sleep(5)
    
    # ACEPTAR COOKIES si aparece
    try:
        accept_buttons = driver.find_elements(By.XPATH, "//button[contains(., 'Aceptar') or contains(., 'Aceptar todo')]")
        if accept_buttons:
            accept_buttons[0].click()
            print("✅ Cookies aceptadas")
            time.sleep(2)
    except:
        print("ℹ️ No hay cookies que aceptar")
    
    # BUSCAR ELEMENTOS CON CLASE 'gPFEn' pero EXCLUIR los que están dentro de 'f9uzM'
    print("🔍 Buscando ENLACES con clase 'gPFEn' (excluyendo div.f9uzM)...")
    news_links = driver.find_elements(By.CSS_SELECTOR, "a.gPFEn")
    print(f"✅ Encontrados {len(news_links)} enlaces de noticias")
    
    data = []
    
    for i, link_element in enumerate(news_links):
        try:
            # VERIFICAR que NO esté dentro de un div con clase 'f9uzM'
            parent_div = link_element.find_element(By.XPATH, "./ancestor::div[contains(@class, 'f9uzM')]")
            if parent_div:
                print(f"⏩ Saltando enlace {i+1} - Está dentro de div.f9uzM")
                continue
                
        except:
            # Si no encuentra un div padre con clase 'f9uzM', procesar el enlace
            title = link_element.text.strip()
            link = link_element.get_attribute('href')
            
            # Convertir enlace relativo a absoluto
            if link and link.startswith('./'):
                link = 'https://news.google.com' + link[1:]
            
            if title and len(title) > 10:  # Filtrar títulos muy cortos
                data.append({
                    'titulo': title,
                    'enlace': link
                })
                print(f"📰 {i+1}. {title[:80]}...")
                continue
    
    # Guardar resultados
    if data:
        df = pd.DataFrame(data)
        df.to_csv('google_news_with_selenium.csv', index=False, encoding='utf-8')
        print(f"\n🎉 ¡Éxito! Guardadas {len(data)} noticias en google_news_with_selenium.csv")
        
        # Mostrar primeras 5
        print("\n📋 Primeras noticias:")
        for i, row in df.head().iterrows():
            print(f"{i+1}. {row['titulo']}")
            print(f"   🔗 {row['enlace']}")
            print()
    else:
        print("😞 No se encontraron noticias con los filtros aplicados")

except Exception as e:
    print(f"💥 Error: {str(e)}")

finally:
    driver.quit()
    print("🔚 Navegador cerrado")
