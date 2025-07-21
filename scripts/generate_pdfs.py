from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

# Asegúrate de ejecutar este script desde la raíz de tu repo
OUTPUT_DIR = os.path.join(os.getcwd(), 'docs')
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Definimos título y texto de cada PDF
pdf_definitions = [
    ('maria_informe_psico.pdf', """\
Informe Psicológico - María Pérez
---------------------------------
Fecha: 12 de marzo de 2025
Paciente: María Pérez, 34 años.

Evaluación de síntomas de ansiedad y estrés postraumático.
Recomendaciones:
 - Continuar terapia cognitivo-conductual.
 - Grupo de apoyo mensual.
"""),
    ('maria_plan_intervencion.pdf', """\
Plan de Intervención Sociofamiliar - María Pérez
------------------------------------------------
Objetivos:
 - Reducir niveles de ansiedad.
 - Mejorar red de apoyo social.

Actividades:
  • Sesiones semanales de terapia grupal.
  • Taller de habilidades sociales cada jueves.
  • Seguimiento domiciliario quincenal.
"""),
    ('juan_cert_ingresos.pdf', """\
Certificado de Ingresos - Juan López
------------------------------------
Fecha: 15 de enero de 2025

Ingresos declarados:
 - 400 €/mes por trabajos esporádicos.

Ayudas recibidas:
 - 45 €/mes de subvención familiar.
"""),
    ('juan_solicitud_ayuda.pdf', """\
Solicitud de Ayuda de Emergencia - Juan López
---------------------------------------------
Razón:
 Pago urgente de suministros básicos atrasados.

Monto solicitado:
 300 €.

Documentación adjunta:
 - Informe Social
 - Certificado de Ingresos
"""),
]

# Función que crea cada PDF
for filename, text in pdf_definitions:
    path = os.path.join(OUTPUT_DIR, filename)
    c = canvas.Canvas(path, pagesize=letter)
    text_obj = c.beginText(40, 750)
    for line in text.splitlines():
        text_obj.textLine(line)
    c.drawText(text_obj)
    c.showPage()
    c.save()
    print(f"Generado {path}")

