import asyncio
from playwright.async_api import async_playwright

async def fetch_html(url: str) -> str:
    """
    Se conecta a una URL usando un navegador Chromium invisible (headless),
    espera a que el JavaScript se ejecute y devuelve el HTML completo.
    """
    print(f"Iniciando conexión asíncrona con: {url}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        page = await browser.new_page()
        
        # Navegamos a la URL y esperamos a que el DOM básico esté cargado
        await page.goto(url, wait_until="domcontentloaded")
        
        # Pausa táctica de 1 segundo para simular comportamiento humano y evitar baneos
        await asyncio.sleep(1)
        
        # Extraemos todo el código HTML ya renderizado por la página
        html_content = await page.content()
        
        # Cerramos el navegador para liberar memoria RAM en tu CachyOS
        await browser.close()
        
        print(f"[Motor] HTML obtenido con éxito ({len(html_content)} bytes)")
        return html_content