import logging
from playwright.async_api import async_playwright

async def fetch_html_booking(url: str) -> str:
    """
    Navega a la URL objetivo esquivando defensas anti-bot y devuelve el HTML crudo.
    Se cierra automáticamente para liberar recursos del servidor.
    """
    logging.info(f"🕸️ [Engine] Desplegando navegador stealth hacia: {url}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True, # En producción (Ubuntu) SIEMPRE va en True
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = await context.new_page()

        # Inyección manual JS
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            window.navigator.chrome = { runtime: {} };
        """)

        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(3000) # Cortesía para el renderizado
            
            # CRÍTICO: Extraemos todo el código HTML de la web como un simple string de texto
            html_crudo = await page.content()
            logging.info("✅ [Engine] HTML extraído con éxito. Cerrando navegador.")
            
            return html_crudo
            
        except Exception as e:
            logging.error(f"❌ [Engine] Fallo en la navegación: {e}")
            return ""