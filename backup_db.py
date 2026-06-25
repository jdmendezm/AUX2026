# -*- coding: utf-8 -*-
"""
backup_db.py — Respalda database.db con timestamp y gestiona retención.
Versión Python para compatibilidad multiplataforma (Windows y Linux).
Uso: python backup_db.py
"""

import os
import sys
import tarfile
import time
from datetime import datetime, timedelta

# ── Configuración ────────────────────────────────────────────────────────────
DB_FILE = "database.db"         # Archivo a respaldar
BACKUP_DIR = "backups"          # Directorio donde guardar los backups
RETENTION_DAYS = 7              # Días de backups a conservar

def log(message):
    current_time = datetime.now().strftime("%H:%M:%S")
    print(f"[{current_time}] {message}")

def run_backup():
    log("Iniciando backup de FinTech Nova (Versión Python)...")

    # Verificar si el archivo de la BD existe
    if not os.path.exists(DB_FILE):
        log(f"ERROR: No se encontró el archivo '{DB_FILE}'")
        log("ERROR: Ejecuta el script desde el directorio raíz del proyecto")
        sys.exit(1)

    # Tamaño del archivo
    db_size = os.path.getsize(DB_FILE)
    db_size_kb = db_size / 1024
    log(f"Archivo encontrado: {DB_FILE} ({db_size_kb:.2f} KB)")

    # Crear directorio de backups si no existe
    if not os.path.exists(BACKUP_DIR):
        log(f"Creando directorio de backups: {BACKUP_DIR}")
        os.makedirs(BACKUP_DIR, exist_ok=True)

    # Crear el nombre del archivo de backup
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_file_name = f"backup_{timestamp}.tar.gz"
    backup_path = os.path.join(BACKUP_DIR, backup_file_name)

    log(f"Creando backup: {backup_path}")

    # Crear el backup comprimido (.tar.gz)
    try:
        with tarfile.open(backup_path, "w:gz") as tar:
            tar.add(DB_FILE, arcname=os.path.basename(DB_FILE))
        
        backup_size = os.path.getsize(backup_path)
        backup_size_kb = backup_size / 1024
        log(f"OK: Backup creado exitosamente ({backup_size_kb:.2f} KB)")
    except Exception as e:
        log(f"ERROR: Falló la creación del backup. Detalle: {e}")
        sys.exit(1)

    # Contar backups existentes
    all_backups = [f for f in os.listdir(BACKUP_DIR) if f.endswith(".tar.gz")]
    log(f"Backups en directorio: {len(all_backups)} (reteniendo últimos {RETENTION_DAYS} días)")

    # Eliminar backups más antiguos que RETENTION_DAYS
    now = time.time()
    cutoff = now - (RETENTION_DAYS * 86400) # 86400 segundos en un día
    deleted_count = 0

    for f in all_backups:
        file_path = os.path.join(BACKUP_DIR, f)
        file_mtime = os.path.getmtime(file_path)
        if file_mtime < cutoff:
            try:
                os.remove(file_path)
                log(f"Eliminado backup antiguo: {f}")
                deleted_count += 1
            except Exception as e:
                log(f"No se pudo eliminar {f}: {e}")

    if deleted_count > 0:
        log(f"Limpieza de backups antiguos completada. {deleted_count} archivos eliminados.")
    else:
        log("No se encontraron backups antiguos para limpiar.")

    # Conteo final
    final_backups = [f for f in os.listdir(BACKUP_DIR) if f.endswith(".tar.gz")]
    log(f"Backups actuales en directorio: {len(final_backups)}")
    log("Proceso de backup finalizado correctamente.")

if __name__ == "__main__":
    run_backup()
