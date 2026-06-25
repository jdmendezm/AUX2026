# -*- coding: utf-8 -*-
"""
resource_monitor.py — Monitor de CPU, Memoria y Disco.
Versión Python para compatibilidad multiplataforma (Windows y Linux).
Uso: python resource_monitor.py
"""

import os
import sys
import time
from datetime import datetime
import psutil

# ── Umbrales de alerta ────────────────────────────────────────────────────────
CPU_WARN = 70     # % de CPU para advertencia
CPU_CRIT = 90     # % de CPU para alerta crítica
MEM_WARN = 75     # % de RAM para advertencia
MEM_CRIT = 90     # % de RAM para alerta crítica
DISK_WARN = 80    # % de disco para advertencia
DISK_CRIT = 95    # % de disco para alerta crítica

def log(message):
    current_time = datetime.now().strftime("%H:%M:%S")
    print(f"[{current_time}] {message}")

def run_monitor():
    log("==========================================")
    log(" Monitor de Recursos - FinTech Nova")
    log("==========================================")

    # ── 1. Uso de CPU ────────────────────────────────────────────────────
    cpu_used = psutil.cpu_percent(interval=1)
    
    log(f"CPU en uso: {cpu_used}%")
    if cpu_used >= CPU_CRIT:
        log(f"  [CRITICAL] CPU al {cpu_used}% (umbral: {CPU_CRIT}%)")
    elif cpu_used >= CPU_WARN:
        log(f"  [WARNING] CPU al {cpu_used}% (umbral: {CPU_WARN}%)")
    else:
        log("  [OK] CPU normal")

    # ── 2. Uso de Memoria RAM ───────────────────────────────────────────
    mem = psutil.virtual_memory()
    mem_used = mem.percent
    mem_free_mb = mem.available / (1024 * 1024)

    log(f"Memoria RAM en uso: {mem_used}% (libre: {mem_free_mb:.1f} MB)")
    if mem_used >= MEM_CRIT:
        log(f"  [CRITICAL] RAM al {mem_used}% (umbral: {MEM_CRIT}%)")
    elif mem_used >= MEM_WARN:
        log(f"  [WARNING] RAM al {mem_used}% (umbral: {MEM_WARN}%)")
    else:
        log("  [OK] Memoria normal")

    # ── 3. Espacio en disco ─────────────────────────────────────────────
    try:
        disk = psutil.disk_usage(os.getcwd())
        disk_used = disk.percent
        disk_free_gb = disk.free / (1024 * 1024 * 1024)

        log(f"Disco en uso: {disk_used}% (libre: {disk_free_gb:.1f} GB)")
        if disk_used >= DISK_CRIT:
            log(f"  [CRITICAL] Disco al {disk_used}% (umbral: {DISK_CRIT}%)")
        elif disk_used >= DISK_WARN:
            log(f"  [WARNING] Disco al {disk_used}% (umbral: {DISK_WARN}%)")
        else:
            log("  [OK] Disco normal")
    except Exception as e:
        log(f"  [ERROR] Error al verificar disco: {e}")

    log("==========================================")

if __name__ == "__main__":
    run_monitor()
