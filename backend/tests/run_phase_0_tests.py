#!/usr/bin/env python3
"""
Script para ejecutar tests de Fase 0 - Capa de Datos
"""
import sys
import subprocess
import time
from pathlib import Path

from backend.core.logging import get_logger

logger = get_logger("ainstalia.tests.runner")

def run_phase_0_tests():
    """Ejecuta todos los tests de Fase 0"""
    logger.info("🚀 Iniciando ejecución de tests - Fase 0")
    start_time = time.time()
    
    # Directorio de tests de Fase 0
    test_dir = Path(__file__).parent / "phase_0"
    
    # Comando pytest con configuraciones específicas
    pytest_cmd = [
        "python", "-m", "pytest",
        str(test_dir),
        "-v",                    # Verbose output
        "--tb=short",           # Traceback corto
        "--durations=10",       # Mostrar los 10 tests más lentos
        "--color=yes",          # Colores en output
        "-s",                   # No capturar stdout (para ver logs)
        "--disable-warnings",   # Deshabilitar warnings de dependencias
    ]
    
    try:
        logger.info(f"Ejecutando comando: {' '.join(pytest_cmd)}")
        result = subprocess.run(
            pytest_cmd,
            cwd=Path(__file__).parent.parent.parent,  # Desde raíz del proyecto
            capture_output=False,  # Mostrar output en tiempo real
            text=True
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        if result.returncode == 0:
            logger.info(f"✅ Tests de Fase 0 completados exitosamente en {duration:.2f}s")
            print("\n" + "="*60)
            print("🎉 FASE 0 - TESTS EXITOSOS")
            print("="*60)
            print(f"⏱️  Duración: {duration:.2f} segundos")
            print("📊 Cobertura: Modelos SQLAlchemy, Esquemas Pydantic, CRUD")
            print("="*60)
            return True
        else:
            logger.error(f"❌ Tests de Fase 0 fallaron con código {result.returncode}")
            print("\n" + "="*60)
            print("💥 FASE 0 - TESTS FALLIDOS")
            print("="*60)
            print(f"🔍 Código de salida: {result.returncode}")
            print(f"⏱️  Duración: {duration:.2f} segundos")
            print("="*60)
            return False
            
    except FileNotFoundError:
        logger.error("❌ pytest no encontrado. Instalar con: pip install pytest")
        return False
    except Exception as e:
        logger.error(f"❌ Error ejecutando tests: {e}")
        return False

def run_individual_test_files():
    """Ejecuta archivos de test individuales para debugging"""
    logger.info("🔍 Ejecutando tests individuales para debugging")
    
    test_dir = Path(__file__).parent / "phase_0"
    test_files = [
        "test_models.py",
        "test_schemas.py", 
        "test_crud.py"
    ]
    
    results = {}
    
    for test_file in test_files:
        logger.info(f"▶️  Ejecutando {test_file}")
        
        pytest_cmd = [
            "python", "-m", "pytest",
            str(test_dir / test_file),
            "-v", "--tb=short", "-s"
        ]
        
        try:
            result = subprocess.run(
                pytest_cmd,
                cwd=Path(__file__).parent.parent.parent,
                capture_output=True,
                text=True
            )
            
            results[test_file] = {
                "success": result.returncode == 0,
                "output": result.stdout + result.stderr
            }
            
            if result.returncode == 0:
                logger.info(f"✅ {test_file} - EXITOSO")
            else:
                logger.error(f"❌ {test_file} - FALLIDO")
                
        except Exception as e:
            logger.error(f"❌ Error ejecutando {test_file}: {e}")
            results[test_file] = {"success": False, "output": str(e)}
    
    # Reporte de resultados individuales
    print("\n" + "="*60)
    print("📋 REPORTE INDIVIDUAL DE TESTS")
    print("="*60)
    
    for test_file, result in results.items():
        status = "✅ EXITOSO" if result["success"] else "❌ FALLIDO"
        print(f"{test_file:20} - {status}")
    
    print("="*60)
    
    return results

def check_test_dependencies():
    """Verifica que las dependencias de test estén instaladas"""
    logger.info("🔍 Verificando dependencias de test")
    
    required_modules = ["pytest", "sqlalchemy", "pydantic"]
    missing_modules = []
    
    for module in required_modules:
        try:
            __import__(module)
            logger.info(f"✅ {module} - OK")
        except ImportError:
            logger.error(f"❌ {module} - FALTANTE")
            missing_modules.append(module)
    
    if missing_modules:
        logger.error(f"❌ Módulos faltantes: {', '.join(missing_modules)}")
        logger.info("💡 Instalar con: pip install pytest sqlalchemy pydantic")
        return False
    
    logger.info("✅ Todas las dependencias están instaladas")
    return True

def main():
    """Función principal"""
    print("🧪 AInstalia - Test Runner Fase 0")
    print("="*60)
    
    # Verificar dependencias
    if not check_test_dependencies():
        sys.exit(1)
    
    # Ejecutar tests
    success = run_phase_0_tests()
    
    if not success:
        print("\n🔍 Ejecutando tests individuales para debugging...")
        run_individual_test_files()
        sys.exit(1)
    
    print("\n🎯 Fase 0 completada exitosamente!")
    print("📝 Próximos pasos: Implementar APIs y endpoints (Fase 1)")

if __name__ == "__main__":
    main() 