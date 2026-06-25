#!/usr/bin/env python3
"""
log_analyzer.py — Detecta intentos de SQL Injection en logs de FinTech Nova
Sesión 13 - Laboratorio 3 | Bloque 1

Uso: python3 log_analyzer.py [archivo_log]
     python3 log_analyzer.py server.log
"""

import re
import sys
import json
from datetime import datetime
from collections import defaultdict


# ── Patrones de detección de SQL Injection ───────────────────────────────────
# Cada elemento es una tupla: (patrón_regex, descripción_legible)
# re.IGNORECASE hace la búsqueda sin importar mayúsculas/minúsculas

SQL_PATTERNS = [
    (r"'\s*OR\s*'?1'?\s*=\s*'?1",    "Bypass de login clásico (OR 1=1)"),
    (r"'\s*--",                        "Comentario SQL para ignorar password"),
    (r"UNION\s+SELECT",               "Exfiltración con UNION SELECT"),
    (r"DROP\s+TABLE",                 "Destrucción de tabla DROP TABLE"),
    (r"INSERT\s+INTO.*SELECT",        "Inyección de datos INSERT-SELECT"),
    (r"EXEC\s*\(",                    "Ejecución de comandos del sistema EXEC"),
    (r";\s*DROP",                     "Encadenamiento de comandos con DROP"),
    (r"xp_cmdshell",                  "Ejecución de comandos OS (MSSQL)"),
]


# ── Función principal de análisis ────────────────────────────────────────────

def analyze_log(log_path: str) -> dict:
    """
    Analiza un archivo de logs en busca de patrones de SQL Injection.

    Retorna un diccionario con:
      - total_lines: total de líneas analizadas
      - clean:       líneas sin incidentes
      - incidents:   lista de incidentes detectados
      - by_ip:       conteo de ataques por dirección IP
      - by_type:     conteo de ataques por tipo
    """
    incidents  = []
    by_ip      = defaultdict(int)   # defaultdict(int) empieza todos los contadores en 0
    by_type    = defaultdict(int)
    total_lines = 0

    try:
        # 'with open()' garantiza que el archivo se cierre aunque haya errores
        with open(log_path, "r", encoding="utf-8") as f:
            # enumerate() da el número de línea junto con su contenido
            for line_num, line in enumerate(f, start=1):
                total_lines += 1
                line = line.strip()     # Elimina espacios y saltos de línea

                if not line:            # Ignorar líneas vacías
                    continue

                # Verificar cada patrón de SQL Injection contra la línea actual
                for pattern, description in SQL_PATTERNS:
                    if re.search(pattern, line, re.IGNORECASE):
                        # Extraer la dirección IP de la línea del log
                        ip_match = re.search(r"IP[:\s]+(\S+)", line, re.IGNORECASE)
                        ip = ip_match.group(1) if ip_match else "desconocida"

                        incidents.append({
                            "line":    line_num,
                            "type":    description,
                            "ip":      ip,
                            "content": line[:120],  # Máximo 120 caracteres para el reporte
                        })

                        by_ip[ip]          += 1
                        by_type[description] += 1

                        # Un incidente por línea es suficiente — break evita duplicados
                        break

    except FileNotFoundError:
        print(f"ERROR: Archivo no encontrado: '{log_path}'")
        sys.exit(1)
    except PermissionError:
        print(f"ERROR: Sin permiso para leer: '{log_path}'")
        sys.exit(1)
    except UnicodeDecodeError:
        print(f"ERROR: El archivo '{log_path}' tiene caracteres no reconocidos. Prueba con --encoding latin-1")
        sys.exit(1)

    return {
        "total_lines": total_lines,
        "clean":       total_lines - len(incidents),
        "incidents":   incidents,
        "by_ip":       dict(by_ip),
        "by_type":     dict(by_type),
    }


# ── Función de presentación del reporte ─────────────────────────────────────

def print_report(results: dict, log_path: str):
    """Imprime un reporte legible con los resultados del análisis."""
    sep  = "=" * 62
    sep2 = "-" * 62
    ts   = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"\n{sep}")
    print(f"  REPORTE DE SEGURIDAD - FinTech Nova")
    print(f"  Archivo analizado : {log_path}")
    print(f"  Fecha del analisis: {ts}")
    print(f"{sep}")
    print(f"  Total de lineas   : {results['total_lines']}")
    print(f"  Lineas limpias    : {results['clean']}")
    print(f"  Incidentes        : {len(results['incidents'])}")
    print(f"{sep}\n")

    if results["incidents"]:
        print("  INCIDENTES DETECTADOS:")
        print(f"  {sep2}")
        for i, inc in enumerate(results["incidents"], 1):
            print(f"  [{i:02d}] Linea {inc['line']:4d} | Tipo: {inc['type']}")
            print(f"        IP: {inc['ip']}")
            print(f"        -> {inc['content'][:80]}...")
            print()

        if results["by_ip"]:
            print(f"  {sep2}")
            print("  IPs mas activas (ordenadas por frecuencia):")
            sorted_ips = sorted(results["by_ip"].items(), key=lambda x: -x[1])
            for ip, count in sorted_ips:
                bar = "#" * min(count, 20)
                print(f"    {ip:<20} {bar} ({count} ataque{'s' if count > 1 else ''})")
            print()

        print(f"  {sep2}")
        print("  Tipos de ataque detectados:")
        sorted_types = sorted(results["by_type"].items(), key=lambda x: -x[1])
        for atype, count in sorted_types:
            print(f"    {count:3d}x - {atype}")
    else:
        print("  Sin incidentes detectados. Logs limpios.")

    print(f"\n{sep}\n")


# ── Punto de entrada ─────────────────────────────────────────────────────────
if __name__ == "__main__":
    log_file = sys.argv[1] if len(sys.argv) > 1 else "server.log"

    print(f"Analizando archivo: {log_file}")
    results = analyze_log(log_file)
    print_report(results, log_file)
