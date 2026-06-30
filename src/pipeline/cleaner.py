import pandas as pd
import os

def clean_and_export(raw_data: list[dict], output_path: str):
    """
    Recibe la lista de diccionarios, limpia los precios y textos, 
    y exporta el resultado a un archivo CSV.
    """
    print("[Pipeline] Iniciando limpieza de datos con Pandas...")
    
    # Convertimos los datos crudos en una tabla (DataFrame)
    df = pd.DataFrame(raw_data)
    
    if df.empty:
        print("⚠️ [Pipeline] No hay datos para limpiar.")
        return

    # 1. Limpieza matemática: Quitamos el símbolo de la libra (£) y convertimos el texto a número decimal
    df['price'] = df['price'].str.replace('£', '', regex=False).astype(float)
    
    # 2. Limpieza de texto: Estandarizamos el stock
    df['stock_status'] = df['stock'].apply(lambda x: "In Stock" if "In stock" in x else "Out of Stock")
    
    # 3. Borramos la columna vieja y sucia de stock
    df.drop(columns=['stock'], inplace=True)
    
    # Exportamos a CSV sin guardar el índice numérico
    df.to_csv(output_path, index=False)
    print(f"[Pipeline] ✅ Éxito! {len(df)} registros limpios guardados en: {output_path}")