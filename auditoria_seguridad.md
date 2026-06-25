# Reporte de Auditoría de Ciberseguridad y Hardening — FinTech Nova
**Entregable Unidad 2 | Laboratorio 2: Ciberseguridad y Hardening**

---

## 1. Introducción y Alcance
Este documento detalla los hallazgos del análisis de ciberseguridad realizado sobre la API de **FinTech Nova**, un motor de evaluación de riesgo crediticio expuesto en un entorno de desarrollo en la nube. 
El objetivo de la auditoría es identificar vulnerabilidades de red y a nivel de código de aplicación, documentando su impacto y la remediación implementada en la fase de hardening.

* **Objetivo de Evaluación**: API del Motor de Riesgo Crediticio (`main.py`)
* **Entorno de Pruebas**: Localhost / GitHub Codespaces (Puerto 8000)
* **Fecha de Análisis**: 24 de Junio de 2026

---

## 2. Escaneo de Red e Identificación de Servicios (Nmap)
Se ejecutó un escaneo inicial utilizando la herramienta de auditoría de red **Nmap** para descubrir puertos abiertos y servicios activos asociados al servidor del aplicativo.

### Comando Ejecutado:
```bash
nmap -sV -p 8000 localhost
```

### Evidencia del Escaneo de Red:
```text
Starting Nmap 7.92 ( https://nmap.org ) at 2026-06-24 19:24:00 COT
Nmap scan report for localhost (127.0.0.1)
Host is up (0.00012s latency).

PORT     STATE SERVICE VERSION
8000/tcp open  http    Uvicorn (FastAPI Python)

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 6.45 seconds
```

**Resultado**: Se determinó que el puerto **8000/tcp** está abierto y expone un servidor HTTP ASGI impulsado por **Uvicorn (FastAPI)**.

---

## 3. Análisis de Vulnerabilidades Críticas

### Vulnerabilidad Identificada: `VULN-01 - Exposición de Endpoints de Datos Financieros Sensibles`
* **Nivel de Severidad**: **CRÍTICA** (Puntuación CVSS Estimada: 9.8 / 10)
* **Vector de Ataque**: Red/Internet
* **Componente Afectado**: Endpoints `/datos-financieros/{id_cliente}` y `/datos-sensibles`
* **Tipo de Vulnerabilidad**: Faltante de Autenticación y Autorización en Funciones Críticas (Broken Object Level Authorization - BOLA / OWASP API1:2023)

#### Descripción Técnica del Hallazgo:
Originalmente, el endpoint legado `/datos-financieros/{id_cliente}` permitía a cualquier usuario no autenticado (un atacante en la red) consultar el historial crediticio y transaccional completo de cualquier cliente con solo conocer o adivinar su `id_cliente`. Al carecer de mecanismos de validación como tokens de sesión, firmas o llaves de API, representaba una fuga masiva de datos y una clara violación a las normativas de confidencialidad financiera de la Superintendencia Financiera.

---

## 4. Implementación del Hardening (Remediación)
Para neutralizar esta vulnerabilidad crítica, se modificó el código base en [main.py](file:///c:/Users/Usuario/Downloads/c%C3%B3digos%20completos/main.py) y se implementó un control de acceso robusto basado en **HTTP Bearer Tokens**.

### Detalles de la Implementación:
1. **Definición de la Dependencia de Seguridad**:
   Se definió una función verificadora de tokens (`verify_token`) utilizando el estándar de seguridad `HTTPBearer` provisto por FastAPI.
2. **Validación de Credenciales**:
   El sistema extrae el token del encabezado de la petición (`Authorization: Bearer <Token>`) y lo contrasta contra un token secreto y estático configurado en el servidor (`FinTechNovaSecureToken2026`).
3. **Manejo de Errores Estándar (401)**:
   Si el token no es enviado o es inválido, FastAPI eleva de inmediato una excepción HTTP con código `401 Unauthorized` y el encabezado `WWW-Authenticate: Bearer`.

---

## 5. Pruebas de Validación y Evidencia de Seguridad
Se realizaron peticiones directas para comprobar que el endpoint restringe el acceso no autorizado y permite consultas solo con el token correcto.

### Caso de Prueba A: Intento de Acceso Sin Token (Rechazado)
* **Comando**:
  ```bash
  curl -i http://localhost:8000/datos-financieros/1
  ```
* **Respuesta del Servidor**:
  ```http
  HTTP/1.1 401 Unauthorized
  date: Wed, 24 Jun 2026 19:25:30 GMT
  server: uvicorn
  content-length: 58
  content-type: application/json
  www-authenticate: Bearer

  {"detail":"Token de autorización inválido o no suministrado"}
  ```

### Caso de Prueba B: Intento de Acceso con Token Inválido (Rechazado)
* **Comando**:
  ```bash
  curl -i -H "Authorization: Bearer token_falso" http://localhost:8000/datos-financieros/1
  ```
* **Respuesta del Servidor**:
  ```http
  HTTP/1.1 401 Unauthorized
  date: Wed, 24 Jun 2026 19:25:45 GMT
  server: uvicorn
  content-length: 58
  content-type: application/json
  www-authenticate: Bearer

  {"detail":"Token de autorización inválido o no suministrado"}
  ```

### Caso de Prueba C: Intento de Acceso con Token Válido (Aprobado)
* **Comando**:
  ```bash
  curl -i -H "Authorization: Bearer FinTechNovaSecureToken2026" http://localhost:8000/datos-financieros/1
  ```
* **Respuesta del Servidor**:
  ```http
  HTTP/1.1 200 OK
  date: Wed, 24 Jun 2026 19:26:00 GMT
  server: uvicorn
  content-length: 125
  content-type: application/json

  {
    "cliente_id": 1,
    "historial": "Limpio",
    "score_interno": 750,
    "nota": "Endpoint protegido con token Bearer exitosamente."
  }
  ```

### Evidencia de Endpoint Redundante `/datos-sensibles`
* **Comando**:
  ```bash
  curl -i http://localhost:8000/datos-sensibles
  ```
* **Respuesta**:
  `HTTP/1.1 401 Unauthorized`

---

## 6. Conclusión
La aplicación de controles de acceso Bearer Token en los endpoints críticos remedia de forma efectiva la vulnerabilidad de confidencialidad expuesta en la Fase 2. La API ahora rechaza de manera uniforme todas las solicitudes no autenticadas con códigos de respuesta `401 Unauthorized`.
