#!/usr/bin/env python3
"""
health_monitor.py — Monitor autónomo del endpoint /health de FinTech Nova
Sesión 13 - Laboratorio 3 | Bloque 2

Este script corre en segundo plano, consulta /health periódicamente
y registra el historial de salud del sistema.

Uso: python3 health_monitor.py
     python3 health_monitor.py --url http://localhost:8000 --interval 60
"""

import requests
import time
import json
import argparse
from datetime import datetime

# ── Configuración por defecto ────────────────────────────────────────────────
DEFAULT_URL      = "http://localhost:8000/health"
DEFAULT_INTERVAL = 60    # segundos entre cada verificación
DEFAULT_TIMEOUT  = 10    # segundos máximo para esperar respuesta
LOG_FILE         = "health_monitor.log"


# ── Consultar el health check ─────────────────────────────────────────────────

def check_health(url: str, timeout: int) -> dict:
    """
    Consulta el endpoint /health y retorna el resultado estructurado.
    Maneja los dos tipos de fallo posibles:
      - ConnectionError: el servidor no está disponible
      - Timeout: el servidor existe pero tarda demasiado en responder
    """
    start = time.time()

    try:
        response    = requests.get(url, timeout=timeout)
        elapsed_ms  = (time.time() - start) * 1000

        return {
            "reachable":   True,
            "http_status": response.status_code,
            "app_status":  response.json().get("status", "unknown"),
            "response_ms": round(elapsed_ms, 1),
            "details":     response.json(),
            "timestamp":   datetime.utcnow().isoformat() + "Z",
        }

    except requests.exceptions.ConnectionError:
        return {
            "reachable":  False,
            "error":      "Servidor no alcanzable (ConnectionError)",
            "timestamp":  datetime.utcnow().isoformat() + "Z",
        }
    except requests.exceptions.Timeout:
        return {
            "reachable":  False,
            "error":      f"Timeout — el servidor no respondió en {timeout}s",
            "timestamp":  datetime.utcnow().isoformat() + "Z",
        }
    except Exception as e:
        return {
            "reachable":  False,
            "error":      f"Error inesperado: {e}",
            "timestamp":  datetime.utcnow().isoformat() + "Z",
        }


# ── Guardar resultado en el log ───────────────────────────────────────────────

def save_to_log(result: dict):
    """Guarda el resultado como línea JSON en el archivo de log."""
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(result, ensure_ascii=False) + "\n")


# ── Imprimir estado en la consola ─────────────────────────────────────────────

def print_status(result: dict):
    """Muestra el estado en la consola con formato legible."""
    ts = result.get("timestamp", "?")[:19]  # Solo fecha y hora, sin microsegundos

    if not result.get("reachable"):
        print(f"[{ts}] [ERROR] NO ALCANZABLE - {result.get('error', 'Error desconocido')}")
    elif result.get("app_status") == "healthy":
        print(f"[{ts}] [OK] SALUDABLE - {result['response_ms']}ms")
    elif result.get("app_status") == "degraded":
        print(f"[{ts}] [WARN] DEGRADADO - {result['response_ms']}ms")
        # Mostrar qué componente está fallando
        checks = result.get("details", {}).get("checks", {})
        for name, info in checks.items():
            if info.get("status") != "ok":
                print(f"          {name}: {info.get('message', '')}")
    else:
        print(f"[{ts}] [CRIT] UNHEALTHY - {result.get('response_ms', '?')}ms")
        checks = result.get("details", {}).get("checks", {})
        for name, info in checks.items():
            if info.get("status") == "error":
                print(f"          ERROR en {name}: {info.get('message', '')}")


# ── Loop principal de monitoreo ───────────────────────────────────────────────

def run_monitor(url: str, interval: int, timeout: int):
    """Corre el monitor en bucle infinito hasta ser interrumpido con Ctrl+C."""
    print(f"Monitor iniciado.")
    print(f"  URL:      {url}")
    print(f"  Intervalo: {interval}s | Timeout: {timeout}s")
    print(f"  Log:      {LOG_FILE}")
    print(f"  Presiona Ctrl+C para detener\n")

    while True:
        result = check_health(url, timeout)
        print_status(result)
        save_to_log(result)
        time.sleep(interval)  # Esperar antes de la siguiente verificación


# ── Punto de entrada ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Monitor de salud para FinTech Nova")
    parser.add_argument("--url",      default=DEFAULT_URL,      help="URL del endpoint /health")
    parser.add_argument("--interval", default=DEFAULT_INTERVAL, type=int, help="Segundos entre checks")
    parser.add_argument("--timeout",  default=DEFAULT_TIMEOUT,  type=int, help="Timeout en segundos")
    args = parser.parse_args()

    try:
        run_monitor(args.url, args.interval, args.timeout)
    except KeyboardInterrupt:
        print("\n\nMonitor detenido por el usuario.")
