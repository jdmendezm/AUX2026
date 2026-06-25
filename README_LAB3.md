# FinTech Nova — Guía de Despliegue Completo

**Sesión 13 - Laboratorio 3 | Stack de Automatización y Contenedores**

---

## Estructura de Archivos del Proyecto

```
fintech-nova/
│
├── main.py               ← API FastAPI (endpoints de negocio + /health)
├── health_check.py       ← Lógica de verificación de salud del sistema
├── health_monitor.py     ← Script de monitoreo autónomo del /health
├── backup_db.sh          ← Script Bash de backup automático de la BD
├── log_analyzer.py       ← Detector de SQL Injection en logs
├── deploy.sh             ← Script de despliegue automatizado
│
├── Dockerfile            ← Receta para construir el contenedor Docker
├── .dockerignore         ← Archivos excluidos del contenedor
├── docker-compose.yml    ← Orquestación local (API + servicios)
├── requirements.txt      ← Dependencias exactas de Python
│
├── database.db           ← Base de datos SQLite (generada automáticamente)
├── server.log            ← Logs de la API (para análisis de seguridad)
└── backups/              ← Directorio de backups (generado por backup_db.sh)
    └── backup_FECHA.tar.gz
```

---

## Prerequisitos

- **Docker** 20.0+ instalado y en ejecución
- **Python** 3.11+ (para ejecutar scripts localmente sin Docker)
- **Git** (para clonar el repositorio)
- **GitHub Codespaces** (opción alternativa — Docker preinstalado)

---

## Configuración Inicial (una sola vez)

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/fintech-nova.git
cd fintech-nova

# 2. Instalar dependencias (para ejecución local sin Docker)
pip install -r requirements.txt

# 3. Dar permisos de ejecución a los scripts Bash
chmod +x backup_db.sh deploy.sh

# 4. Crear el directorio de datos para el volumen Docker
mkdir -p data backups
```

---

## Opción A: Ejecución con Docker (Recomendado para Producción)

```bash
# Construir la imagen Docker
docker build -t fintech-nova:1.0 .

# Ejecutar el contenedor
docker run -d \
  -p 8000:8000 \
  --name fintech-api \
  fintech-nova:1.0

# Verificar que está corriendo
docker ps

# Ver los logs
docker logs -f fintech-api

# Verificar el health check
curl http://localhost:8000/health
```

---

## Opción B: Ejecución Local (Para Desarrollo)

```bash
# Iniciar la API directamente con Python
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Acceder a la documentación interactiva
# http://localhost:8000/docs
```

---

## Opción C: Ejecución con docker-compose (API + Servicios)

```bash
# Iniciar todos los servicios
docker-compose up -d

# Ver estado de los servicios
docker-compose ps

# Ver logs
docker-compose logs -f api

# Detener todos los servicios
docker-compose down
```

---

## Automatización con Scripts

### Backup automático de la base de datos

```bash
# Ejecutar backup manualmente
./backup_db.sh

# Programar backup automático con Cron (todos los días a las 2AM)
crontab -e
# Agregar la siguiente línea:
0 2 * * * /ruta/completa/al/proyecto/backup_db.sh >> /tmp/backup.log 2>&1

# Verificar que el crontab quedó guardado
crontab -l
```

### Análisis de logs de seguridad

```bash
# Analizar el archivo de logs (detecta SQL Injection)
python3 log_analyzer.py server.log

# Analizar un archivo específico
python3 log_analyzer.py /var/log/app.log
```

### Monitoreo continuo del health check

```bash
# Iniciar el monitor (corre en primer plano, Ctrl+C para detener)
python3 health_monitor.py

# Con configuración personalizada
python3 health_monitor.py --url http://localhost:8000 --interval 30

# Ver el historial de monitoreo
cat health_monitor.log | python3 -m json.tool | head -50
```

---

## Verificación del Sistema

```bash
# 1. Verificar que la API responde
curl http://localhost:8000/status

# 2. Verificar el health check completo (todos los componentes)
curl -s http://localhost:8000/health | python3 -m json.tool

# 3. Probar la evaluación de crédito
curl -X POST http://localhost:8000/evaluar-riesgo \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Ana García", "edad": 28, "ingresos": 5000000, "deudas": 800000}'

# 4. Ver la documentación interactiva
# Abre en el navegador: http://localhost:8000/docs
```

---

## Solución de Problemas Comunes

**Error: `port is already allocated`**
El puerto 8000 ya está en uso.
```bash
# Ver qué proceso usa el puerto
lsof -i :8000
# Detener el proceso o usar otro puerto: -p 9000:8000
```

**Error: `ModuleNotFoundError` al iniciar el contenedor**
Falta una librería en requirements.txt.
```bash
# Regenerar requirements.txt con el entorno virtual activo
pip freeze > requirements.txt
# Reconstruir la imagen
docker build -t fintech-nova:1.0 .
```

**Health check siempre en estado `starting` o `unhealthy`**
El endpoint /health no responde correctamente.
```bash
# Diagnóstico: entrar al contenedor y probar manualmente
docker exec -it fintech-api bash
curl -v http://localhost:8000/health
exit
```

**El backup_db.sh falla con "Permission denied"**
El script no tiene permisos de ejecución.
```bash
chmod +x backup_db.sh
ls -la backup_db.sh   # Debe mostrar -rwxr-xr-x
```

---

## Deliverables del Laboratorio 3

Al completar la sesión, debes tener:

| Archivo               | Estado | Descripción                              |
|-----------------------|--------|------------------------------------------|
| `backup_db.sh`        | ✅     | Backup automático con cron configurado   |
| `log_analyzer.py`     | ✅     | Detector de SQL Injection funcional      |
| `health_check.py`     | ✅     | Verificaciones de BD, disco y backups    |
| `health_monitor.py`   | ✅     | Monitor autónomo del endpoint /health    |
| `Dockerfile`          | ✅     | Imagen construida y probada              |
| `docker-compose.yml`  | ✅     | Orquestación local funcional             |
| Contenedor activo     | ✅     | `docker ps` muestra el contenedor        |
| Health check activo   | ✅     | `/health` retorna `{"status":"healthy"}` |
| Al menos 2 ejercicios | ✅     | Completados entre los Ejercicios 1-8     |

---

*FinTech Nova — Unidad 3: Automatización de Procesos Tecnológicos*
*Sesión 13 - Laboratorio 3*
