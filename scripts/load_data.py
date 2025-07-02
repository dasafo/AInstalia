#!/usr/bin/env python3
"""
Script para cargar datos desde archivos CSV a la base de datos PostgreSQL.
"""
import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text
from pathlib import Path

# Agregar el directorio padre al path para importar configuración
sys.path.append(str(Path(__file__).parent.parent))

from backend.core.config import settings

def load_csv_data():
    """Carga todos los archivos CSV a la base de datos."""
    
    # Crear engine de base de datos
    engine = create_engine(settings.DATABASE_URL)
    
    # Directorio donde están los archivos CSV
    data_dir = Path(__file__).parent.parent / "data"
    
    # Mapeo de archivos CSV a nombres de tabla
    csv_files = {
        "clients.csv": "clients",
        "products.csv": "products", 
        "technicians.csv": "technicians",
        "warehouses.csv": "warehouses",  # Nota: el archivo se llama wharehouses.csv (typo)
        "orders.csv": "orders",
        "orders_items.csv": "order_items",  # Nota: el archivo se llama orders_items.csv
        "installed_equipment.csv": "installed_equipment",
        "interventions.csv": "interventions",
        "contracts.csv": "contracts",
        "stock.csv": "stock",
        "chat_sessions.csv": "chat_sessions",
        "chat_messages.csv": "chat_messages",
        "knowledge_feedback.csv": "knowledge_feedback"
    }
    
    print("🔄 Iniciando carga de datos...")
    
    # Verificar que los archivos CSV existen
    for csv_file, table_name in csv_files.items():
        file_path = data_dir / csv_file
        
        # Manejar nombres de archivo con errores tipográficos
        if not file_path.exists():
            if csv_file == "warehouses.csv":
                file_path = data_dir / "wharehouses.csv"  # Archivo real
            elif csv_file == "orders_items.csv":
                file_path = data_dir / "orders_items.csv"  # Archivo real
                
        if file_path.exists():
            print(f"📁 Cargando {csv_file} → tabla {table_name}")
            
            try:
                # Leer CSV
                df = pd.read_csv(file_path)
                print(f"   📊 {len(df)} registros encontrados")
                
                # Cargar a base de datos
                df.to_sql(
                    table_name, 
                    engine, 
                    if_exists='append',  # Agregar datos (las tablas ya existen)
                    index=False,
                    method='multi'
                )
                print(f"   ✅ {table_name} cargada exitosamente")
                
            except Exception as e:
                print(f"   ❌ Error cargando {csv_file}: {e}")
        else:
            print(f"   ⚠️  Archivo no encontrado: {csv_file}")
    
    print("\n🎉 Proceso de carga completado!")
    
    # Verificar conteo de registros
    print("\n📊 Verificando datos cargados:")
    with engine.connect() as conn:
        for csv_file, table_name in csv_files.items():
            try:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                count = result.scalar()
                print(f"   {table_name}: {count} registros")
            except Exception as e:
                print(f"   {table_name}: Error - {e}")

if __name__ == "__main__":
    load_csv_data() 