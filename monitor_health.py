#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
monitor_health.py — Script de monitoreo para el endpoint /status de FinTech Nova
Sesión 13 - Laboratorio 3 | Fase 3

Este script consulta periódicamente el endpoint /status de la API,
verifica que responda correctamente y registra su estado de salud en un log local.

Uso:
    python monitor_health.py
    python monitor_health.py --url http://127.0.0.1:8000/status --interval 30
"""

import requests
import time
import json
import argparse
from datetime import datetime
import os

# ── Configuración por defecto ────────────────────────────────────────────────
DEFAULT_URL      = "http://127.0.0.1:8000/status"
DEFAULT_INTERVAL = 10    # Segundos entre verificaciones
DEFAULT_TIMEOUT  = 5     # Timeout de respuesta HTTP
LOG_FILE         = "health_monitor.log"

def check_status(url: str, timeout: int) -> dict:
    """
    Realiza una petición HTTP GET al endpoint /status y retorna
    un diccionario con el resultado de la comprobación.
    """
    start_time = time.time()
    try:
        response = requests.get(url, timeout=timeout)
        elapsed_ms = (time.time() - start_time) * 1000
        
        if response.status_code == 200:
            data = response.json()
            estado = data.get("estado", "desconocido")
            
            if estado == "Operacional":
                return {
                    "timestamp": datetime.now().isoformat(),
                    "status": "OK",
                    "url": url,
                    "response_time_ms": round(elapsed_ms, 2),
                    "message": f"Servicio Operacional (Servidor: {data.get('servidor', 'desconocido')})"
                }
            else:
                return {
                    "timestamp": datetime.now().isoformat(),
                    "status": "WARN",
                    "url": url,
                    "response_time_ms": round(elapsed_ms, 2),
                    "message": f"Servicio en estado no operativo: {estado}"
                }
        else:
            return {
                "timestamp": datetime.now().isoformat(),
                "status": "FAIL",
                "url": url,
                "response_time_ms": round(elapsed_ms, 2),
                "message": f"HTTP status code incorrecto: {response.status_code}"
            }
            
    except requests.exceptions.ConnectionError:
        return {
            "timestamp": datetime.now().isoformat(),
            "status": "FAIL",
            "url": url,
            "message": "Error de conexión: No se pudo establecer enlace con el servidor."
        }
    except requests.exceptions.Timeout:
        return {
            "timestamp": datetime.now().isoformat(),
            "status": "FAIL",
            "url": url,
            "message": f"Error de Timeout: El servidor tardó más de {timeout}s en responder."
        }
    except Exception as e:
        return {
            "timestamp": datetime.now().isoformat(),
            "status": "FAIL",
            "url": url,
            "message": f"Error inesperado: {str(e)}"
        }

def log_result(result: dict):
    """Escribe el resultado estructurado de la verificación en el log local."""
    line = f"[{result['timestamp']}] [{result['status']}] URL: {result['url']} - Msg: {result['message']}"
    if "response_time_ms" in result:
        line += f" ({result['response_time_ms']} ms)"
    
    # Imprimir por consola
    print(line)
    
    # Guardar en archivo
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

def run_loop(url: str, interval: int, timeout: int):
    """Ejecuta el ciclo continuo de monitoreo."""
    print("=====================================================================")
    print(f"Iniciando monitoreo de /status para FinTech Nova")
    print(f"URL objetivo : {url}")
    print(f"Intervalo    : {interval}s")
    print(f"Log de salida: {os.path.abspath(LOG_FILE)}")
    print("Presiona Ctrl+C para detener el proceso.")
    print("=====================================================================")
    
    # Asegurar que el directorio de salida existe
    log_dir = os.path.dirname(os.path.abspath(LOG_FILE))
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    try:
        while True:
            result = check_status(url, timeout)
            log_result(result)
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\nMonitoreo finalizado por el usuario.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitoreo autónomo del endpoint /status")
    parser.add_argument("--url", default=DEFAULT_URL, help="URL de la API a consultar")
    parser.add_argument("--interval", type=int, default=DEFAULT_INTERVAL, help="Segundos entre peticiones")
    parser.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT, help="Timeout de respuesta en segundos")
    args = parser.parse_args()
    
    run_loop(args.url, args.interval, args.timeout)
