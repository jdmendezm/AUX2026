#!/bin/bash
# ════════════════════════════════════════════════════════════════════
# Script: backup_db.sh
# Descripción: Respalda database.db con timestamp y gestiona retención
# Uso:  ./backup_db.sh
# Cron: 0 2 * * * /ruta/completa/al/proyecto/backup_db.sh
# Sesión 13 - Laboratorio 3 | Bloque 1
# ════════════════════════════════════════════════════════════════════

# ── SECCIÓN 1: Variables de configuración ───────────────────────────
DB_FILE="database.db"         # Archivo a respaldar
BACKUP_DIR="backups"          # Directorio donde guardar los backups
RETENTION_DAYS=7              # Días de backups a conservar

# $(comando) ejecuta el comando y captura su salida como valor
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_FILE="backup_${TIMESTAMP}.tar.gz"

# ── SECCIÓN 2: Función de logging con timestamp ─────────────────────
log() {
    echo "[$(date +"%H:%M:%S")] $1"
}

# ── SECCIÓN 3: Verificaciones previas ──────────────────────────────
log "Iniciando backup de FinTech Nova..."

# [ ! -f "$DB_FILE" ] = si el archivo NO existe
if [ ! -f "$DB_FILE" ]; then
    log "ERROR: No se encontró el archivo '$DB_FILE'"
    log "ERROR: Ejecuta el script desde el directorio raíz del proyecto"
    exit 1  # exit 1 = terminar con código de error
fi

DB_SIZE=$(du -sh "$DB_FILE" | cut -f1)
log "Archivo encontrado: $DB_FILE ($DB_SIZE)"

# ── SECCIÓN 4: Crear directorio de backups si no existe ────────────
# [ ! -d "$BACKUP_DIR" ] = si el DIRECTORIO NO existe
if [ ! -d "$BACKUP_DIR" ]; then
    log "Creando directorio de backups: $BACKUP_DIR"
    mkdir -p "$BACKUP_DIR"
fi

# ── SECCIÓN 5: Crear el backup comprimido ──────────────────────────
log "Creando backup: $BACKUP_DIR/$BACKUP_FILE"

# tar -c (crear) -z (comprimir con gzip) -f (nombre del archivo de salida)
tar -czf "$BACKUP_DIR/$BACKUP_FILE" "$DB_FILE"

# $? contiene el código de salida del último comando (0=éxito, otro=error)
if [ $? -eq 0 ]; then
    BACKUP_SIZE=$(du -sh "$BACKUP_DIR/$BACKUP_FILE" | cut -f1)
    log "OK: Backup creado exitosamente ($BACKUP_SIZE)"
else
    log "ERROR: Falló la creación del backup. Revisa el espacio en disco."
    exit 1
fi

# ── SECCIÓN 6: Contar backups existentes ───────────────────────────
BACKUP_COUNT=$(ls "$BACKUP_DIR"/*.tar.gz 2>/dev/null | wc -l)
log "Backups en directorio: $BACKUP_COUNT (reteniendo últimos $RETENTION_DAYS días)"

# ── SECCIÓN 7: Eliminar backups más antiguos que RETENTION_DAYS ────
# find busca archivos, -mtime +N = modificados hace más de N días, -delete los elimina
find "$BACKUP_DIR" -name "*.tar.gz" -mtime "+$RETENTION_DAYS" -delete
log "Limpieza de backups antiguos completada."

# ── SECCIÓN 8: Resumen final ────────────────────────────────────────
FINAL_COUNT=$(ls "$BACKUP_DIR"/*.tar.gz 2>/dev/null | wc -l)
log "Backups actuales en directorio: $FINAL_COUNT"
log "Proceso de backup finalizado correctamente."

exit 0  # exit 0 = terminar con éxito
