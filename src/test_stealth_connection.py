import asyncio
from playwright.async_api import async_playwright

async def test_stealth_connection(url: str):
    """
    Testea la conexión e interactúa con la SPA esquivando defensas anti-bot.
    Arquitectura de grado de producción sin dependencias rotas.
    """
    async with async_playwright() as p:
        # 1. EVASIÓN A NIVEL DE CHROMIUM (Desactiva la bandera de bot)
        browser = await p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = await context.new_page()

        # 2. INYECCIÓN JS MANUAL (Camuflaje profundo)
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
            window.navigator.chrome = { runtime: {} };
        """)

        print(f"🕵️ Navegando a {url}...")
        
        # Usamos domcontentloaded para soltar el hilo en cuanto llegue el esqueleto
        response = await page.goto(url, wait_until="domcontentloaded", timeout=60000)
        print(f"Estado HTTP: {response.status}")

        print("⏳ Esperando estabilización de la red (Network Idle)...")
        await page.wait_for_load_state("networkidle")
        
        # 3. INTERACCIÓN (Búsqueda autónoma de alojamiento)
        print("✅ Interfaz base detectada. Iniciando interacción humana...")
        
        try:
            # Localizamos el input por su atributo semántico inmutable
            buscador = page.locator('input[name="ss"]')
            
            # Escribimos el objetivo
            print("📍 Introduciendo destino: Praga...")
            await buscador.fill("Praga")
            
            # Pausa humana antes de confirmar (imprescindible para eludir el bot-scoring)
            await page.wait_for_timeout(1500)
            
            # Simulamos pulsar Enter con el hardware virtual
            print("⌨️ Tecla Enter pulsada. Esperando resultados del servidor...")
            await buscador.press("Enter")
            
            # Esperamos a que la nueva página de resultados cargue
            await page.wait_for_load_state("networkidle")
            
            # Damos 2 segundos extra para que el motor gráfico pinte las fotos de los hoteles
            await page.wait_for_timeout(2000)
            
            # Auditoría visual del éxito
            await page.screenshot(path="resultados_extraccion.png")
            print("📸 ÉXITO: Captura de resultados guardada como 'resultados_extraccion.png'.")
            
        except Exception as e:
            print(f"⚠️ Error crítico durante la interacción: {e}")
            # Si el script falla, hacemos una foto para ver qué nos ha bloqueado
            await page.screenshot(path="error_interaccion.png")
            print("📸 Captura de depuración guardada como 'error_interaccion.png'.")

        # Tiempo para auditar visualmente la ventana en tu monitor antes de destruir el proceso
        await asyncio.sleep(5)
        await browser.close()

if __name__ == "__main__":
    # Nuestro objetivo de grado militar
    target = "https://www.booking.com/"
    print("🚀 INICIANDO PIPELINE DE EVASIÓN E INTERACCIÓN...")
    asyncio.run(test_stealth_connection(target))