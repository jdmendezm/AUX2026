"""
health_check.py — Verificación de salud del sistema FinTech Nova
Sesión 13 - Laboratorio 3 | Bloque 2

Uso independiente:  python3 health_check.py
Uso desde FastAPI:  from health_check import run_all_checks
"""

import sqlite3
import shutil
import os
import time
from datetime import datetime
from typing import Tuple


# ── Verificación 1: Base de datos ────────────────────────────────────────────

def check_database(db_path: str = "database.db") -> Tuple[str, str]:
    """
    Verifica que la base de datos esté accesible y responda consultas.

    Retorna una tupla (estado, mensaje):
      - estado: 'ok' | 'warning' | 'error'
      - mensaje: descripción legible del resultado
    """
    if not os.path.exists(db_path):
        return "error", f"Archivo de BD no encontrado: {db_path}"

    try:
        start = time.time()

        conn = sqlite3.connect(db_path, timeout=5)
        # SELECT 1 es la consulta más liviana posible — solo verifica que la BD responde
        conn.execute("SELECT 1")
        conn.close()

        elapsed_ms = (time.time() - start) * 1000

        if elapsed_ms > 500:
            return "warning", f"BD lenta: {elapsed_ms:.1f}ms (umbral: 500ms)"

        return "ok", f"BD accesible - respuesta en {elapsed_ms:.1f}ms"

    except sqlite3.OperationalError as e:
        return "error", f"Error operacional de BD: {e}"
    except Exception as e:
        return "error", f"Error inesperado al conectar BD: {e}"


# ── Verificación 2: Espacio en disco ─────────────────────────────────────────

def check_disk(path: str = "/", warn_pct: int = 80, crit_pct: int = 95) -> Tuple[str, str]:
    """
    Verifica el espacio en disco disponible.

    path:     ruta del sistema de archivos a verificar
    warn_pct: porcentaje de uso que activa la advertencia (default: 80%)
    crit_pct: porcentaje de uso que activa el estado crítico (default: 95%)
    """
    try:
        usage = shutil.disk_usage(path)

        used_pct = (usage.used / usage.total) * 100
        free_gb  = usage.free  / (1024 ** 3)  # Convertir bytes a GB
        total_gb = usage.total / (1024 ** 3)

        detail = f"{used_pct:.1f}% usado — {free_gb:.1f}GB libre de {total_gb:.1f}GB"

        if used_pct >= crit_pct:
            return "error", f"Disco crítico: {detail}"
        if used_pct >= warn_pct:
            return "warning", f"Disco alto: {detail}"

        return "ok", f"Disco saludable: {detail}"

    except FileNotFoundError:
        return "error", f"Ruta no encontrada: {path}"
    except Exception as e:
        return "error", f"Error al verificar disco: {e}"


# ── Verificación 3: Backup reciente ──────────────────────────────────────────

def check_backup(backup_dir: str = "backups", max_age_hours: int = 25) -> Tuple[str, str]:
    """
    Verifica que exista un backup reciente generado por backup_db.sh.

    backup_dir:    directorio donde backup_db.sh guarda los backups
    max_age_hours: máximo de horas aceptable desde el último backup
    """
    if not os.path.isdir(backup_dir):
        return "warning", f"Directorio de backups no existe: '{backup_dir}' - ejecuta backup_db.sh"

    # Buscar todos los archivos .tar.gz en el directorio
    backups = sorted([
        f for f in os.listdir(backup_dir)
        if f.endswith(".tar.gz")
    ])

    if not backups:
        return "error", f"No hay backups en '{backup_dir}' - ejecuta backup_db.sh"

    latest      = backups[-1]                              # El más reciente (orden alfabético = cronológico)
    latest_path = os.path.join(backup_dir, latest)
    age_seconds = time.time() - os.path.getmtime(latest_path)
    age_hours   = age_seconds / 3600

    if age_hours > max_age_hours:
        return (
            "warning",
            f"Backup desactualizado: '{latest}' tiene {age_hours:.1f}h (máximo: {max_age_hours}h)"
        )

    return "ok", f"Backup reciente: '{latest}' - hace {age_hours:.1f}h"


# ── Función consolidada ───────────────────────────────────────────────────────

def run_all_checks() -> dict:
    """
    Ejecuta todas las verificaciones y retorna el estado consolidado del sistema.
    Esta función es llamada directamente por el endpoint /health de FastAPI.

    Estado general:
      - 'healthy':   todos los checks son 'ok'
      - 'degraded':  al menos un check es 'warning', ninguno es 'error'
      - 'unhealthy': al menos un check es 'error'
    """
    db_status,   db_msg   = check_database()
    disk_status, disk_msg = check_disk()
    bkp_status,  bkp_msg  = check_backup()

    checks = {
        "database": {"status": db_status,   "message": db_msg},
        "disk":     {"status": disk_status, "message": disk_msg},
        "backup":   {"status": bkp_status,  "message": bkp_msg},
    }

    # El estado general es el peor de todos los checks individuales
    all_statuses = [v["status"] for v in checks.values()]

    if "error" in all_statuses:
        overall = "unhealthy"
    elif "warning" in all_statuses:
        overall = "degraded"
    else:
        overall = "healthy"

    return {
        "status":    overall,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version":   "1.0.0",
        "checks":    checks,
    }


# ── Ejecución directa para pruebas ───────────────────────────────────────────
if __name__ == "__main__":
    import json
    print("\nEjecutando health checks de FinTech Nova...\n")
    result = run_all_checks()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    print()
