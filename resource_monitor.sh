#!/bin/bash
# ════════════════════════════════════════════════════════════════════
# resource_monitor.sh — Monitor de CPU, Memoria y Disco
# Sesión 13 - Laboratorio 3 | Ejercicio 1
# Uso: ./resource_monitor.sh
# ════════════════════════════════════════════════════════════════════

# ── Umbrales de alerta (puedes ajustarlos) ──────────────────────────
CPU_WARN=70     # % de CPU para advertencia
CPU_CRIT=90     # % de CPU para alerta crítica
MEM_WARN=75     # % de RAM para advertencia
MEM_CRIT=90     # % de RAM para alerta crítica
DISK_WARN=80    # % de disco para advertencia
DISK_CRIT=95    # % de disco para alerta crítica

log() { echo "[$(date +"%H:%M:%S")] $1"; }

log "=========================================="
log " Monitor de Recursos — FinTech Nova"
log "=========================================="

# ── 1. Uso de CPU ────────────────────────────────────────────────────
# top -bn1: corre top en modo batch (no interactivo) por 1 iteración
# grep "Cpu(s)": filtra la línea de CPU
# awk: extrae el porcentaje de CPU en uso
CPU_IDLE=$(top -bn1 | grep "Cpu(s)" | awk '{print $8}' | cut -d. -f1 2>/dev/null || echo "0")
CPU_USED=$((100 - CPU_IDLE))

log "CPU en uso: ${CPU_USED}%"
if [ "$CPU_USED" -ge "$CPU_CRIT" ]; then
    log "  🔴 CRÍTICO: CPU al ${CPU_USED}% (umbral: ${CPU_CRIT}%)"
elif [ "$CPU_USED" -ge "$CPU_WARN" ]; then
    log "  ⚠️  ADVERTENCIA: CPU al ${CPU_USED}% (umbral: ${CPU_WARN}%)"
else
    log "  ✅ CPU normal"
fi

# ── 2. Uso de Memoria RAM ───────────────────────────────────────────
# free: muestra uso de memoria
# grep Mem: filtra la línea de memoria RAM
# awk: calcula porcentaje = (usado / total) * 100
MEM_USED=$(free | grep Mem | awk '{print int($3/$2 * 100)}' 2>/dev/null || echo "0")
MEM_FREE_MB=$(free -m | grep Mem | awk '{print $4}')

log "Memoria RAM en uso: ${MEM_USED}% (libre: ${MEM_FREE_MB}MB)"
if [ "$MEM_USED" -ge "$MEM_CRIT" ]; then
    log "  🔴 CRÍTICO: RAM al ${MEM_USED}% (umbral: ${MEM_CRIT}%)"
elif [ "$MEM_USED" -ge "$MEM_WARN" ]; then
    log "  ⚠️  ADVERTENCIA: RAM al ${MEM_USED}% (umbral: ${MEM_WARN}%)"
else
    log "  ✅ Memoria normal"
fi

# ── 3. Espacio en disco ─────────────────────────────────────────────
# df -h .: muestra uso del disco del directorio actual
# tail -1: toma la última línea (la del directorio actual)
# awk '{print $5}': extrae el campo de porcentaje
# tr -d '%': elimina el símbolo de porcentaje para hacer comparaciones numéricas
DISK_USED=$(df -h . | tail -1 | awk '{print $5}' | tr -d '%' 2>/dev/null || echo "0")
DISK_FREE=$(df -h . | tail -1 | awk '{print $4}')

log "Disco en uso: ${DISK_USED}% (libre: ${DISK_FREE})"
if [ "$DISK_USED" -ge "$DISK_CRIT" ]; then
    log "  🔴 CRÍTICO: Disco al ${DISK_USED}% (umbral: ${DISK_CRIT}%)"
elif [ "$DISK_USED" -ge "$DISK_WARN" ]; then
    log "  ⚠️  ADVERTENCIA: Disco al ${DISK_USED}% (umbral: ${DISK_WARN}%)"
else
    log "  ✅ Disco normal"
fi

log "=========================================="
