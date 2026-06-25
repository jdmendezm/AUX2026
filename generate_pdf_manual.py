# -*- coding: utf-8 -*-
"""
generate_pdf_manual.py — Genera el manual de ejecución en formato PDF.
Uso: python generate_pdf_manual.py
"""

import os
from fpdf import FPDF

class PDFManual(FPDF):
    def header(self):
        # Logotipo / Encabezado
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, "FinTech Nova - Manual de Despliegue y Monitoreo", 0, 0, "L")
        self.cell(0, 10, "Sesion 13 - Lab 3", 0, 1, "R")
        # Línea divisoria
        self.set_draw_color(200, 200, 200)
        self.line(10, 18, 200, 18)
        self.ln(5)

    def footer(self):
        # Posición a 1.5 cm del final
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        # Línea divisoria
        self.set_draw_color(200, 200, 200)
        self.line(10, 282, 200, 282)
        # Número de página
        self.cell(0, 10, f"Pagina {self.page_no()}/{{nb}}", 0, 0, "C")

    def chapter_title(self, label):
        self.set_font("Helvetica", "B", 16)
        self.set_text_color(24, 43, 73) # Azul oscuro premium
        self.cell(0, 10, label, 0, 1, "L")
        self.ln(2)

    def section_title(self, label):
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(40, 80, 120)
        self.cell(0, 8, label, 0, 1, "L")
        self.ln(1)

    def body_text(self, text):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(50, 50, 50)
        self.multi_cell(0, 5, text)
        self.ln(3)

    def alert_box(self, text):
        self.set_fill_color(240, 244, 248) # Fondo azul claro suave
        self.set_draw_color(180, 200, 220)
        self.set_font("Helvetica", "I", 9)
        self.set_text_color(40, 60, 90)
        self.multi_cell(0, 5, text, border=1, fill=True)
        self.ln(3)

    def code_block(self, code):
        self.set_font("Courier", "", 9)
        self.set_text_color(30, 30, 30)
        self.set_fill_color(245, 245, 245) # Fondo gris claro
        self.set_draw_color(220, 220, 220)
        # Reemplazar tabulaciones por espacios
        clean_code = code.replace("\t", "    ")
        self.multi_cell(0, 4.5, clean_code, border=1, fill=True)
        self.ln(4)

def create_manual_pdf():
    pdf = PDFManual()
    pdf.alias_nb_pages()
    pdf.add_page()
    pdf.set_margins(10, 20, 10)

    # ── TÍTULO DE PORTADA / ENCABEZADO PRINCIPAL ──────────────────────────────
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(24, 43, 73)
    pdf.cell(0, 15, "FinTech Nova", 0, 1, "C")
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, "Manual de Ejecucion, Monitoreo y Automatizacion (Windows)", 0, 1, "C")
    pdf.ln(10)

    # ── SECCIÓN 1: INTRODUCCIÓN ─────────────────────────────────────────────
    pdf.chapter_title("1. Introduccion")
    pdf.body_text(
        "Este manual describe los pasos necesarios para desplegar, ejecutar y monitorear "
        "la API de FinTech Nova en un entorno Windows de manera local.\n\n"
        "La aplicacion consta de un backend desarrollado en FastAPI (Python) que evalua el "
        "riesgo crediticio y registra solicitudes en una base de datos SQLite. Adicionalmente, "
        "cuenta con una suite de herramientas de automatizacion para backups, monitoreo de recursos "
        "y analisis de logs de seguridad."
    )

    pdf.alert_box(
        "Nota de compatibilidad: Los scripts Bash (.sh) originales incluidos en el proyecto "
        "requieren entornos Linux. Para facilitar la ejecucion directa en Windows sin dependencias "
        "complejas como Docker o WSL, hemos creado equivalentes en scripts de Python (.py) "
        "nativos que realizan las mismas tareas de manera multiplataforma."
    )

    # ── SECCIÓN 2: REQUISITOS ───────────────────────────────────────────────
    pdf.chapter_title("2. Requisitos Previos")
    pdf.body_text(
        "Para ejecutar el proyecto necesitas:\n"
        "  - Python 3.10 o superior (Se ha verificado Python 3.10.6 instalado en el sistema).\n"
        "  - Pip (Administrador de paquetes de Python).\n"
        "  - Librerias listadas en requirements.txt (se detallan en el Paso 2)."
    )

    # ── SECCIÓN 3: PASOS PARA LA EJECUCIÓN ──────────────────────────────────
    pdf.chapter_title("3. Pasos de Instalacion y Ejecucion")
    
    pdf.section_title("Paso 1: Configurar el Entorno Virtual (venv)")
    pdf.body_text(
        "Se recomienda crear un entorno virtual para aislar las dependencias del proyecto. "
        "Abre una terminal PowerShell en el directorio raiz del proyecto y ejecuta:"
    )
    pdf.code_block(
        "# 1. Crear el entorno virtual llamado 'venv'\n"
        "python -m venv venv\n\n"
        "# 2. Activar el entorno virtual en PowerShell\n"
        ".\\venv\\Scripts\\Activate.ps1"
    )

    pdf.section_title("Paso 2: Instalar Dependencias")
    pdf.body_text(
        "Instala las dependencias especificadas utilizando requirements.txt (el archivo "
        "ha sido corregido para evitar conflictos de codificacion Unicode en Windows):"
    )
    pdf.code_block(
        "pip install -r requirements.txt"
    )

    pdf.section_title("Paso 3: Inicializar la Base de Datos SQLite")
    pdf.body_text(
        "La base de datos se inicializa automaticamente al arrancar la API. Tambien puedes "
        "crear la base de datos sqlite vacia manualmente ejecutando:"
    )
    pdf.code_block(
        "python -c \"import main; main.init_db()\""
    )

    pdf.add_page() # Nueva página para estructurar mejor

    pdf.section_title("Paso 4: Arrancar el Servidor FastAPI")
    pdf.body_text(
        "Inicia el servidor ASGI de uvicorn en tu localhost:"
    )
    pdf.code_block(
        "uvicorn main:app --reload --host 127.0.0.1 --port 8000"
    )
    pdf.body_text(
        "  - URL de Estado de la API: http://127.0.0.1:8000/status\n"
        "  - Endpoint de Health Check: http://127.0.0.1:8000/health\n"
        "  - Documentacion Interactiva (Swagger): http://127.0.0.1:8000/docs"
    )

    # ── SECCIÓN 4: AUTOMATIZACIONES Y MONITOREO ─────────────────────────────
    pdf.chapter_title("4. Herramientas de Automatizacion y Monitoreo")
    pdf.body_text(
        "En lugar de usar los archivos .sh que requieren Linux, ejecuta las versiones de Python:"
    )

    pdf.section_title("A. Copias de Seguridad de Base de Datos (backup_db.py)")
    pdf.body_text(
        "Genera un respaldo comprimido de 'database.db' y mantiene los ultimos 7 dias de copias:"
    )
    pdf.code_block("python backup_db.py")
    pdf.body_text(
        "Los archivos se guardaran en la carpeta 'backups/' con el formato 'backup_FECHA.tar.gz'."
    )

    pdf.section_title("B. Monitoreo de Recursos del Sistema (resource_monitor.py)")
    pdf.body_text(
        "Verifica el uso de CPU, RAM y espacio en disco en tu maquina local emitiendo alertas "
        "si se sobrepasan los umbrales criticos. Requiere la libreria psutil:"
    )
    pdf.code_block("python resource_monitor.py")

    pdf.section_title("C. Detector de SQL Injection en Logs (log_analyzer.py)")
    pdf.body_text(
        "Analiza un archivo de logs (como server.log) buscando patrones comunes de ataques "
        "de inyeccion SQL (ej. OR 1=1, DROP TABLE, UNION SELECT) y genera un reporte:"
    )
    pdf.code_block("python log_analyzer.py server.log")

    pdf.section_title("D. Monitoreo Continuo de la API (health_monitor.py)")
    pdf.body_text(
        "Consulta periodicamente el endpoint /health de la API y escribe un log historico "
        "en health_monitor.log. Util para verificar la disponibilidad del servicio:"
    )
    pdf.code_block("python health_monitor.py --url http://127.0.0.1:8000/health --interval 10")

    # Guardar el PDF en disco
    output_filename = "Manual_de_Ejecucion_FinTech_Nova.pdf"
    pdf.output(output_filename)
    print(f"PDF generado con exito: {output_filename}")

if __name__ == "__main__":
    create_manual_pdf()
