from bs4 import BeautifulSoup
import logging

def parse_alojamientos(html: str) -> list:
    """
    Recibe el HTML crudo y extrae los datos clave usando BeautifulSoup.
    Retorna una lista de diccionarios limpios listos para la base de datos.
    """
    if not html:
        logging.warning("⚠️ [Parser] Se recibió un HTML vacío.")
        return []

    # Inicializamos el motor de análisis
    soup = BeautifulSoup(html, 'html.parser')
    datos_limpios = []
    
    # Buscamos todas las tarjetas usando el atributo de test (Igual que con locator)
    tarjetas = soup.find_all('div', attrs={"data-testid": "property-card"})
    logging.info(f"📊 [Parser] Analizando {len(tarjetas)} tarjetas de alojamiento...")

    for tarjeta in tarjetas:
        # Extraer Título
        titulo_elem = tarjeta.find(attrs={"data-testid": "title"})
        titulo = titulo_elem.get_text(strip=True) if titulo_elem else "Desconocido"
        
        # Extraer Precio
        precio_elem = tarjeta.find(attrs={"data-testid": "price-and-discounted-price"})
        # Limpiamos símbolos como "€" o "£" y espacios raros para poder guardarlo como Float en BD
        if precio_elem:
            precio_texto = precio_elem.get_text(strip=True)
            # Extraemos solo los números (ej. de "€ 1,234" a "1234")
            precio_limpio = ''.join(c for c in precio_texto if c.isdigit() or c == '.')
        else:
            precio_limpio = "0"
            
        # Añadimos a nuestro diccionario
        if titulo != "Desconocido":
            datos_limpios.append({
                "titulo": titulo,
                "precio": float(precio_limpio) if precio_limpio else 0.0
            })

    return datos_limpios