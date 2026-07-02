import asyncio
import argparse
from playwright.async_api import async_playwright

async def extraer_alojamientos(destino: str, entrada: str, salida: str):
    """
    Motor de extracción con inyección de URL dinámica y evasión de defensas.
    """
    # Construimos la URL Maestra (El atajo del hacker)
    # Booking usa 'ss' para destino, y 'checkin'/'checkout' para las fechas
    url = f"https://www.booking.com/searchresults.html?ss={destino}&checkin={entrada}&checkout={salida}"
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = await context.new_page()

        # Inyección JS para eludir detección de bot
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            window.navigator.chrome = { runtime: {} };
        """)

        print(f"🕵️ Infiltrando mediante URL maestra: {url}")
        response = await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        print(f"Estado HTTP: {response.status}")

        print("⏳ Esperando renderizado de tarjetas de alojamiento...")
        await page.wait_for_load_state("networkidle")
        
        # Damos margen al motor JS de Booking para que pinte los precios
        await page.wait_for_timeout(3000)
        
        print(f"🔍 Analizando disponibilidad en {destino} del {entrada} al {salida}...\n")
        
        tarjetas_hoteles = page.locator('div[data-testid="property-card"]')
        cantidad_hoteles = await tarjetas_hoteles.count()
        
        if cantidad_hoteles == 0:
            print("⚠️ No se encontraron alojamientos. ¿Fechas pasadas o bloqueo anti-bot?")
            await page.screenshot(path="error_extraccion.png")
        else:
            print(f"📊 Se detectaron {cantidad_hoteles} alojamientos. Extrayendo el Top 5:\n")
            limite = min(5, cantidad_hoteles)
            
            for i in range(limite):
                tarjeta = tarjetas_hoteles.nth(i)
                
                try:
                    titulo = await tarjeta.locator('[data-testid="title"]').inner_text(timeout=2000)
                except:
                    titulo = "Título desconocido"
                    
                try:
                    # En la vista de resultados con fechas, Booking muestra el precio total
                    precio = await tarjeta.locator('[data-testid="price-and-discounted-price"]').inner_text(timeout=2000)
                    precio = precio.replace('\n', ' ').strip()
                except:
                    precio = "Agotado / Precio oculto"
                    
                print(f"🏨 Alojamiento {i+1}: {titulo}")
                print(f"💰 Precio Total Estancia: {precio}")
                print("-" * 50)
        
        await browser.close()

if __name__ == "__main__":
    # La Magia de Argparse (Interfaz de cliente)
    parser = argparse.ArgumentParser(description="Scraper táctico de alojamientos en Booking")
    
    # Definimos las "banderas" que el cliente puede usar en la terminal
    parser.add_argument("-d", "--destino", type=str, required=True, help="Ciudad objetivo (ej: Praga)")
    parser.add_argument("-e", "--entrada", type=str, required=True, help="Fecha de check-in (Formato: YYYY-MM-DD)")
    parser.add_argument("-s", "--salida", type=str, required=True, help="Fecha de check-out (Formato: YYYY-MM-DD)")
    
    # Python lee lo que escribes en la terminal y lo convierte en un objeto
    args = parser.parse_args()
    
    print(f"🚀 INICIANDO MISIÓN: Objetivo {args.destino}")
    asyncio.run(extraer_alojamientos(args.destino, args.entrada, args.salida))