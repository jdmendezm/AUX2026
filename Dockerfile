# ════════════════════════════════════════════════════════════════════
# Dockerfile — FinTech Nova API
# Sesión 13 - Laboratorio 3 | Bloque 3
# Integra: FastAPI + health_check.py + usuario no-root
# ════════════════════════════════════════════════════════════════════

# ── INSTRUCCIÓN 1: FROM — imagen base ───────────────────────────────
# python:3.9-slim = Python 3.9 sobre Debian mínimo
# ~130 MB en lugar de los ~900 MB de la imagen completa
FROM python:3.9-slim

# ── INSTRUCCIÓN 2: LABEL — metadatos (documentación de la imagen) ──
LABEL maintainer="fintech-nova@empresa.com"
LABEL version="1.0.0"
LABEL description="API de evaluación crediticia FinTech Nova"

# ── INSTRUCCIÓN 3: ENV — variables de entorno ───────────────────────
# PYTHONDONTWRITEBYTECODE=1 → no genera archivos .pyc (innecesarios en contenedor)
# PYTHONUNBUFFERED=1        → los logs aparecen en tiempo real sin buffering
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ── INSTRUCCIÓN 4: WORKDIR — directorio de trabajo ──────────────────
# Todos los COPY, RUN y CMD siguientes son relativos a /app
WORKDIR /app

# ── INSTRUCCIÓN 5: Crear usuario no-root (Principio Mínimo Privilegio)
# Por defecto Docker corre como root — si hay un ataque exitoso,
# el atacante tiene acceso total al contenedor.
# appuser solo tiene acceso a /app — el daño potencial está contenido.
RUN addgroup --system appgroup && \
    adduser  --system --ingroup appgroup appuser

# ── INSTRUCCIÓN 6: Dependencias del sistema ─────────────────────────
# curl: necesario para el HEALTHCHECK que consulta /health
# --no-install-recommends: no instala paquetes opcionales (menos tamaño)
# apt-get clean + rm: limpia la caché de apt después de instalar
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# ── INSTRUCCIÓN 7: Dependencias Python ──────────────────────────────
# IMPORTANTE: Copiar requirements.txt ANTES que el código fuente.
# Optimización de caché de Docker: si solo cambia el código (no las deps),
# Docker reutiliza la capa de pip install del build anterior → build mucho más rápido.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# --no-cache-dir: no guarda caché de pip dentro del contenedor (menos tamaño)

# ── INSTRUCCIÓN 8: Código de la aplicación ──────────────────────────
# Se copia DESPUÉS de las dependencias para aprovechar el caché.
# El .dockerignore excluye: .git, .env, __pycache__, venv, backups, logs
COPY . .

# ── INSTRUCCIÓN 9: Permisos de archivos ─────────────────────────────
# Asignar los archivos al usuario no-root para que pueda leer y ejecutar
RUN chown -R appuser:appgroup /app

# ── INSTRUCCIÓN 10: Cambiar al usuario no-root ──────────────────────
# Desde aquí en adelante, todos los comandos corren como appuser
USER appuser

# ── INSTRUCCIÓN 11: EXPOSE — documentar el puerto ───────────────────
# EXPOSE no abre el puerto — es solo documentación.
# El puerto real se mapea con -p al ejecutar: docker run -p 8000:8000
EXPOSE 8000

# ── INSTRUCCIÓN 12: HEALTHCHECK ─────────────────────────────────────
# Docker verifica la salud del contenedor automáticamente.
# Usa el endpoint /health implementado en health_check.py.
# --interval=30s: verificar cada 30 segundos
# --timeout=10s:  si no responde en 10s, cuenta como fallo
# --retries=3:    después de 3 fallos consecutivos → contenedor "unhealthy"
# Kubernetes y docker-compose usan este estado para tomar decisiones.
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# ── INSTRUCCIÓN 13: CMD — comando de inicio ──────────────────────────
# Inicia Uvicorn (servidor ASGI de FastAPI) cuando el contenedor arranca.
# --host 0.0.0.0: escuchar en TODAS las interfaces de red del contenedor
#                 sin esto, solo escucha en localhost y sería inaccesible desde fuera
# --port 8000:    debe coincidir con EXPOSE
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
