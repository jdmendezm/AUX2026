#!/bin/bash
# ════════════════════════════════════════════════════════════════════
# deploy.sh — Script de despliegue automatizado de FinTech Nova
# Sesión 13 - Laboratorio 3 | Ejercicio 6
# Uso: ./deploy.sh [versión]   Ej: ./deploy.sh 1.0
# ════════════════════════════════════════════════════════════════════

IMAGE_NAME="fintech-nova"
CONTAINER_NAME="fintech-api"
PORT=8000
VERSION=${1:-$(date +"%Y%m%d")}  # Usa el argumento o la fecha como versión
FULL_TAG="${IMAGE_NAME}:${VERSION}"

log() { echo "[$(date +"%H:%M:%S")] $1"; }

log "════════════════════════════════════════"
log " Despliegue FinTech Nova — v${VERSION}"
log "════════════════════════════════════════"

# ── 1. Verificar prerequisitos ──────────────────────────────────────
log "Verificando prerequisitos..."

if ! command -v docker &> /dev/null; then
    log "ERROR: Docker no está instalado. Instálalo primero."
    exit 1
fi

if [ ! -f "requirements.txt" ]; then
    log "ERROR: No se encontró requirements.txt — el build de Docker fallará"
    exit 1
fi

if [ ! -f "Dockerfile" ]; then
    log "ERROR: No se encontró Dockerfile"
    exit 1
fi

log "OK: Prerequisitos verificados"

# ── 2. Construir la nueva imagen ────────────────────────────────────
log "Construyendo imagen: $FULL_TAG ..."
docker build -t "$FULL_TAG" .

if [ $? -ne 0 ]; then
    log "ERROR: El build de Docker falló. Revisa el Dockerfile y requirements.txt"
    exit 1
fi
log "OK: Imagen construida exitosamente: $FULL_TAG"

# ── 3. Detener y eliminar el contenedor anterior ────────────────────
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    log "Deteniendo contenedor anterior: $CONTAINER_NAME ..."
    docker stop "$CONTAINER_NAME" > /dev/null 2>&1
    docker rm   "$CONTAINER_NAME" > /dev/null 2>&1
    log "OK: Contenedor anterior eliminado"
fi

# ── 4. Iniciar el nuevo contenedor ──────────────────────────────────
log "Iniciando nuevo contenedor: $CONTAINER_NAME ..."
docker run \
    -d \
    -p "${PORT}:${PORT}" \
    --name "$CONTAINER_NAME" \
    --restart unless-stopped \
    "$FULL_TAG"

if [ $? -ne 0 ]; then
    log "ERROR: No se pudo iniciar el contenedor"
    exit 1
fi
log "OK: Contenedor iniciado"

# ── 5. Esperar a que la API arranque ────────────────────────────────
log "Esperando 10 segundos para que la API inicie..."
sleep 10

# ── 6. Verificar el health check ────────────────────────────────────
log "Verificando health check..."
HEALTH_RESPONSE=$(curl -s "http://localhost:${PORT}/health" 2>/dev/null)

if [ -z "$HEALTH_RESPONSE" ]; then
    log "ERROR: El health check no respondió. Revisa los logs:"
    log "       docker logs $CONTAINER_NAME"
    exit 1
fi

HEALTH_STATUS=$(echo "$HEALTH_RESPONSE" | python3 -c "import sys,json; print(json.load(sys.stdin).get('status','unknown'))" 2>/dev/null)

if [ "$HEALTH_STATUS" = "healthy" ]; then
    log "✅  DESPLIEGUE EXITOSO — Health check: $HEALTH_STATUS"
    log "    API disponible en: http://localhost:${PORT}"
    log "    Docs en:           http://localhost:${PORT}/docs"
elif [ "$HEALTH_STATUS" = "degraded" ]; then
    log "⚠️   Despliegue completado con advertencias — Health check: $HEALTH_STATUS"
    log "    Revisa el estado completo: curl http://localhost:${PORT}/health"
else
    log "❌  ERROR: El despliegue tuvo problemas — Health check: $HEALTH_STATUS"
    log "    Logs del contenedor:"
    docker logs --tail 20 "$CONTAINER_NAME"
    exit 1
fi

log "════════════════════════════════════════"
