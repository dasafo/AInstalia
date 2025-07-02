#!/usr/bin/env python3
"""
Script optimizado para cargar datos desde archivos CSV a la base de datos PostgreSQL.
Versión mejorada con logging, validaciones y orden correcto de carga.
"""
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Agregar el directorio padre al path para importar configuración
sys.path.append(str(Path(__file__).parent.parent))

try:
    from backend.core.config import settings
    from backend.core.logging import get_logger
except ImportError as e:
    print(f"❌ Error importando dependencias: {e}")
    print("💡 Asegúrate de ejecutar desde el directorio raíz del proyecto")
    sys.exit(1)

# Configurar logger
logger = get_logger("ainstalia.data_loader")

class DataLoader:
    """Cargador optimizado de datos CSV con validaciones y logging"""
    
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "data"
        self.engine = None
        
        # Mapeo correcto de archivos CSV a tablas (orden importante por foreign keys)
        self.csv_mapping = [
            # Tablas independientes primero
            ("clients.csv", "clients"),
            ("products.csv", "products"),
            ("technicians.csv", "technicians"),
            ("warehouses.csv", "warehouses"),
            
            # Tablas que dependen de las anteriores
            ("installed_equipment.csv", "installed_equipment"),  # Depende de clients, products
            ("stock.csv", "stock"),  # Depende de products, warehouses
            ("contracts.csv", "contracts"),  # Depende de clients
            ("orders.csv", "orders"),  # Depende de clients
            
            # Tablas que dependen de orders
            ("order_items.csv", "order_items"),  # Depende de orders, products
            
            # Tablas que dependen de equipment
            ("interventions.csv", "interventions"),  # Depende de technicians, clients, equipment
            
            # Tablas de chat (dependen de orders, clients)
            ("chat_sessions.csv", "chat_sessions"),
            ("chat_messages.csv", "chat_messages"),
            
            # Tabla independiente al final
            ("knowledge_feedback.csv", "knowledge_feedback")
        ]
        
        self.stats = {
            "loaded_files": 0,
            "total_records": 0,
            "errors": 0,
            "start_time": None,
            "end_time": None
        }
    
    def _validate_environment(self) -> bool:
        """Valida que el entorno esté correctamente configurado"""
        logger.info("🔍 Validando entorno...")
        
        # Verificar directorio de datos
        if not self.data_dir.exists():
            logger.error(f"❌ Directorio de datos no encontrado: {self.data_dir}")
            return False
        
        # Verificar configuración de BD
        if not hasattr(settings, 'DATABASE_URL') or not settings.DATABASE_URL:
            logger.error("❌ DATABASE_URL no configurada")
            return False
            
        # Verificar archivos CSV
        missing_files = []
        for csv_file, _ in self.csv_mapping:
            file_path = self.data_dir / csv_file
            if not file_path.exists():
                missing_files.append(csv_file)
        
        if missing_files:
            logger.warning(f"⚠️  Archivos CSV faltantes: {missing_files}")
        
        logger.info("✅ Validación de entorno completada")
        return True
    
    def _connect_database(self) -> bool:
        """Establece conexión con la base de datos"""
        try:
            logger.info("🔌 Conectando a la base de datos...")
            self.engine = create_engine(
                settings.DATABASE_URL,
                echo=False,
                pool_pre_ping=True,
                pool_recycle=3600
            )
            
            # Probar conexión
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT 1"))
                result.scalar()
            
            logger.info("✅ Conexión a base de datos establecida")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error conectando a la base de datos: {e}")
            return False
    
    def _load_single_csv(self, csv_file: str, table_name: str) -> Tuple[bool, int]:
        """Carga un archivo CSV individual"""
        file_path = self.data_dir / csv_file
        
        if not file_path.exists():
            logger.warning(f"⚠️  Archivo no encontrado: {csv_file}")
            return False, 0
        
        try:
            # Leer CSV con configuración optimizada y manejo de errores
            logger.info(f"📁 Cargando {csv_file} → tabla {table_name}")
            
            df = pd.read_csv(
                file_path,
                encoding='utf-8',
                na_values=['', 'NULL', 'null', 'None'],
                keep_default_na=True,
                on_bad_lines='skip',  # Saltar líneas malformadas
                dtype=str  # Leer todo como string para evitar problemas de tipo
            )
            
            record_count = len(df)
            logger.info(f"   📊 {record_count} registros encontrados")
            
            if record_count == 0:
                logger.warning(f"   ⚠️  Archivo {csv_file} está vacío")
                return True, 0
            
            # Verificar si la tabla ya tiene datos
            with self.engine.connect() as conn:
                existing_count = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
                if existing_count > 0:
                    logger.info(f"   📋 Tabla {table_name} ya tiene {existing_count} registros")
                    # Usar 'append' siempre, pero limpiar datos primero con TRUNCATE
                    logger.info(f"   🧹 Limpiando tabla {table_name} antes de recargar...")
                    conn.execute(text(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE"))
                    conn.commit()
                    if_exists_mode = 'append'
                else:
                    if_exists_mode = 'append'
            
            # Cargar datos con configuración optimizada
            df.to_sql(
                table_name,
                self.engine,
                if_exists=if_exists_mode,
                index=False,
                method='multi',
                chunksize=1000  # Procesar en lotes para mejorar rendimiento
            )
            
            logger.info(f"   ✅ {table_name} cargada exitosamente ({record_count} registros)")
            return True, record_count
            
        except pd.errors.EmptyDataError:
            logger.warning(f"   ⚠️  Archivo {csv_file} está vacío o malformado")
            return False, 0
            
        except pd.errors.ParserError as e:
            logger.error(f"   ❌ Error parseando CSV {csv_file}: {e}")
            logger.info(f"   💡 Intentando cargar con configuración menos estricta...")
            
            # Intentar carga con configuración más permisiva
            try:
                df = pd.read_csv(
                    file_path,
                    encoding='utf-8',
                    on_bad_lines='skip',
                    sep=',',
                    quotechar='"',
                    escapechar='\\',
                    dtype=str
                )
                
                record_count = len(df)
                if record_count > 0:
                    df.to_sql(table_name, self.engine, if_exists='append', index=False, method='multi')
                    logger.info(f"   ✅ {table_name} cargada con modo permisivo ({record_count} registros)")
                    return True, record_count
                else:
                    logger.warning(f"   ⚠️  No se pudieron recuperar datos de {csv_file}")
                    return False, 0
                    
            except Exception as e2:
                logger.error(f"   ❌ Error en carga permisiva de {csv_file}: {e2}")
                self.stats["errors"] += 1
                return False, 0
            
        except SQLAlchemyError as e:
            logger.error(f"   ❌ Error SQL cargando {csv_file}: {e}")
            self.stats["errors"] += 1
            return False, 0
            
        except Exception as e:
            logger.error(f"   ❌ Error inesperado cargando {csv_file}: {e}")
            self.stats["errors"] += 1
            return False, 0
    
    def _verify_data_integrity(self) -> None:
        """Verifica la integridad de los datos cargados"""
        logger.info("\n📊 Verificando integridad de datos cargados...")
        
        total_records = 0
        tables_summary = []
        
        with self.engine.connect() as conn:
            for csv_file, table_name in self.csv_mapping:
                try:
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    count = result.scalar()
                    total_records += count
                    tables_summary.append(f"   {table_name}: {count:,} registros")
                    
                except Exception as e:
                    logger.error(f"   ❌ Error verificando {table_name}: {e}")
                    tables_summary.append(f"   {table_name}: Error - {e}")
        
        # Mostrar resumen
        for summary in tables_summary:
            logger.info(summary)
        
        logger.info(f"\n📈 Total de registros en base de datos: {total_records:,}")
        self.stats["total_records"] = total_records
    
    def load_all_data(self) -> bool:
        """Método principal para cargar todos los datos"""
        self.stats["start_time"] = time.time()
        
        try:
            logger.info("🚀 Iniciando carga optimizada de datos CSV...")
            
            # Validaciones previas
            if not self._validate_environment():
                return False
            
            if not self._connect_database():
                return False
            
            # Cargar archivos en orden correcto
            loaded_count = 0
            total_records = 0
            
            for csv_file, table_name in self.csv_mapping:
                success, records = self._load_single_csv(csv_file, table_name)
                if success:
                    loaded_count += 1
                    total_records += records
            
            self.stats["loaded_files"] = loaded_count
            
            # Verificar integridad final
            self._verify_data_integrity()
            
            # Resumen final
            self.stats["end_time"] = time.time()
            duration = self.stats["end_time"] - self.stats["start_time"]
            
            logger.info(f"\n🎉 Proceso de carga completado!")
            logger.info(f"📊 Archivos procesados: {loaded_count}/{len(self.csv_mapping)}")
            logger.info(f"📈 Total registros cargados: {total_records:,}")
            logger.info(f"⏱️  Tiempo total: {duration:.2f} segundos")
            logger.info(f"❌ Errores: {self.stats['errors']}")
            
            return self.stats["errors"] == 0
            
        except Exception as e:
            logger.error(f"❌ Error crítico en carga de datos: {e}")
            return False
        
        finally:
            if self.engine:
                self.engine.dispose()
                logger.info("🔌 Conexión a base de datos cerrada")

def main():
    """Función principal del script"""
    loader = DataLoader()
    
    try:
        success = loader.load_all_data()
        
        if success:
            logger.info("🎯 Carga de datos completada exitosamente")
            return 0
        else:
            logger.error("💥 Carga de datos falló con errores")
            return 1
            
    except KeyboardInterrupt:
        logger.warning("⚠️  Proceso interrumpido por el usuario")
        return 1
    except Exception as e:
        logger.error(f"💥 Error crítico: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code) 