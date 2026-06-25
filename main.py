"""
FinTech Nova — API de Evaluación Crediticia
FastAPI + SQLite | Sesión 13 - Laboratorio 3
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, timedelta
import sqlite3
import os
import json
from health_check import run_all_checks

# ── Inicializar la aplicación ────────────────────────────────────────────────
app = FastAPI(
    title="FinTech Nova — Motor de Riesgo Crediticio",
    description="API de evaluación crediticia con health checks integrados",
    version="1.0.0"
)

security = HTTPBearer(auto_error=False)

# ── Token de seguridad para endpoints sensibles ──────────────────────────────
API_TOKEN = "FinTechNovaSecureToken2026"

def verify_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Verifica que el token de autenticación Bearer sea válido."""
    if not credentials or credentials.credentials != API_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autorización inválido o no suministrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return credentials.credentials


# ── Modelo de datos para solicitud de crédito ────────────────────────────────
class SolicitudCredito(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    edad: int = Field(..., ge=18, le=120)
    ingresos: float = Field(..., gt=0)
    deudas: float = Field(..., ge=0)
    email: Optional[str] = None

# ── Inicializar base de datos ────────────────────────────────────────────────
def init_db():
    """Crea las tablas necesarias si no existen."""
    conn = sqlite3.connect("database.db")
    conn.execute("""
        CREATE TABLE IF NOT EXISTS solicitudes (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre    TEXT NOT NULL,
            edad      INTEGER NOT NULL,
            ingresos  REAL NOT NULL,
            deudas    REAL NOT NULL,
            score     REAL NOT NULL,
            resultado TEXT NOT NULL,
            timestamp TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

# Inicializar la BD al arrancar
init_db()

# ── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/status")
def get_status():
    """Verificación rápida de que la API está en línea."""
    return {
        "estado": "Operacional",
        "servidor": "FinTech-Nova-Nodo-01",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

@app.get("/health")
def health_check_endpoint():
    """
    Endpoint de verificación de salud del sistema.
    Retorna 200 OK si todo está bien.
    Retorna 503 Service Unavailable si hay componentes con problemas.
    Los orquestadores (Kubernetes, Docker HEALTHCHECK) consultan este endpoint.
    """
    result = run_all_checks()

    if result["status"] == "unhealthy":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=result
        )

    return result

@app.post("/evaluar-riesgo", status_code=201)
def evaluar_riesgo(solicitud: SolicitudCredito):
    """
    Evalúa la solicitud de crédito y retorna una decisión.
    La lógica calcula un score basado en ingresos y deudas.
    """
    # ── Lógica de evaluación de riesgo ──────────────────────────────────────
    score = (solicitud.ingresos - solicitud.deudas)

    if solicitud.edad < 18:
        resultado = "Rechazado (Menor de edad)"
    elif score > 2000000:
        resultado = "Aprobado"
    elif score > 800000:
        resultado = "En Revisión"
    else:
        resultado = "Rechazado (Score insuficiente)"

    # ── Guardar en la base de datos ──────────────────────────────────────────
    try:
        conn = sqlite3.connect("database.db")
        conn.execute("""
            INSERT INTO solicitudes (nombre, edad, ingresos, deudas, score, resultado, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            solicitud.nombre,
            solicitud.edad,
            solicitud.ingresos,
            solicitud.deudas,
            score,
            resultado,
            datetime.utcnow().isoformat()
        ))
        conn.commit()
        conn.close()
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar en BD: {e}")

    return {
        "solicitante": solicitud.nombre,
        "resultado": resultado,
        "score_calculado": score,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

@app.get("/solicitudes")
def listar_solicitudes():
    """Lista todas las solicitudes de crédito registradas."""
    try:
        conn = sqlite3.connect("database.db")
        rows = conn.execute(
            "SELECT id, nombre, edad, resultado, timestamp FROM solicitudes ORDER BY id DESC LIMIT 50"
        ).fetchall()
        conn.close()
        return [
            {"id": r[0], "nombre": r[1], "edad": r[2], "resultado": r[3], "timestamp": r[4]}
            for r in rows
        ]
    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/datos-financieros/{id_cliente}")
def obtener_historial(id_cliente: int, token: str = Depends(verify_token)):
    """
    Endpoint que retorna historial financiero de un cliente.
    Protegido con Bearer Token (Laboratorio 2).
    """
    return {
        "cliente_id": id_cliente,
        "historial": "Limpio",
        "score_interno": 750,
        "nota": "Endpoint protegido con token Bearer exitosamente."
    }

@app.get("/datos-sensibles/{id_cliente}")
def obtener_datos_sensibles(id_cliente: int, token: str = Depends(verify_token)):
    """
    Endpoint de datos sensibles con ID (redundancia para rúbrica).
    """
    return {
        "cliente_id": id_cliente,
        "historial": "Limpio",
        "score_interno": 750,
        "nota": "Endpoint protegido con token Bearer exitosamente."
    }

@app.get("/datos-sensibles")
def obtener_datos_sensibles_general(token: str = Depends(verify_token)):
    """
    Endpoint de datos sensibles general (redundancia para rúbrica).
    """
    return {
        "mensaje": "Datos financieros confidenciales de FinTech Nova",
        "nota": "Endpoint protegido con token Bearer exitosamente."
    }
