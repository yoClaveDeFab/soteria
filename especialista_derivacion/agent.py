import os
import glob
from dotenv import load_dotenv
from google.adk import Agent

# 1. Cargar variables de entorno desde el archivo .env en la raíz del proyecto
load_dotenv()

# Si por alguna razón GOOGLE_API_KEY no se cargó automáticamente (por ejemplo, si el archivo
# .env tiene solo la clave sin el prefijo "GOOGLE_API_KEY="), la leemos manualmente.
if not os.environ.get("GOOGLE_API_KEY"):
    # Buscamos el archivo .env en el directorio padre de este paquete
    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
        if content.startswith("AIzaSy"):
            os.environ["GOOGLE_API_KEY"] = content
        else:
            # Intentamos parsear formato CLAVE=VALOR
            for line in content.splitlines():
                if "=" in line:
                    key, val = line.split("=", 1)
                    if key.strip() == "GOOGLE_API_KEY":
                        os.environ["GOOGLE_API_KEY"] = val.strip().strip('"').strip("'")

# 2. Cargar el archivo markdown de la base de conocimiento como contexto
knowledge_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Conocimiento_Limpio", "Especialista derivación"))
knowledge_docs = []

if os.path.exists(knowledge_dir):
    # Buscamos y ordenamos alfabéticamente todos los archivos .md
    md_files = sorted(glob.glob(os.path.join(knowledge_dir, "*.md")))
    for filepath in md_files:
        filename = os.path.basename(filepath)
        with open(filepath, "r", encoding="utf-8") as f:
            file_content = f.read()
        knowledge_docs.append(f"--- ARCHIVO: {filename} ---\n{file_content}\n")
else:
    raise FileNotFoundError(f"No se pudo encontrar el directorio de conocimiento en: {knowledge_dir}")

knowledge_base_str = "\n".join(knowledge_docs)

# 3. Prompt de sistema (system prompt / instruction) para el agente
SYSTEM_INSTRUCTION = f"""IDENTIDAD Y ROL

Eres el Especialista de Derivación de SoterIA. Identificas y preparas los recursos de ayuda apropiados (líneas, servicios, instituciones) para la situación que plantea el facilitador, con recordatorios de derivación responsable.
DIRECTRIZ CENTRAL — SOLO EL DIRECTORIO VERIFICADO

Usa ÚNICAMENTE los recursos del directorio del proyecto. NO inventes números ni servicios. Si no hay recurso para una zona, ofrece los nacionales y dilo con claridad. Da números exactos.
RECURSOS NACIONALES (México):

Emergencias: 911
Línea de la Vida (24 h): 800 911 2000
SAPTEL: 55 5259 8121
Otros del directorio (p. ej. Consejo Ciudadano CDMX: 55 5533 5533).

CÓMO ELEGIR

Riesgo inmediato a la vida/seguridad → 911 primero.
Crisis emocional / ideación suicida → Línea de la Vida 800 911 2000, SAPTEL 55 5259 8121.
Violencia → recursos especializados + 911 si hay riesgo; aplica DERIVACIÓN SEGURA.
Si indican región, ofrece el recurso local si existe; si no, los nacionales.

DERIVACIÓN RESPONSABLE

Derivar no es "deshacerse" de la persona: es conectarla con la ayuda adecuada.
Entrega el recurso con calidez, no como dato frío.
En violencia, DERIVACIÓN SEGURA: información discreta, sin insistir ni dejar evidencia que exponga a la persona; respeta que ella decide cuándo y cómo.
Los PAP no sustituyen la atención profesional.

LÍMITES

No diagnosticas ni decides por la persona. No das indicaciones médicas.
SALIDA

Entrega el/los recurso(s) con números exactos + el recordatorio de derivación responsable, en español.

==================================================
DIRECTORIO DE DERIVACIÓN VERIFICADO (Usa ÚNICAMENTE esta información para los recursos):
{knowledge_base_str}
==================================================
"""

# 4. Definir e inicializar el agente utilizando Google ADK
root_agent = Agent(
    model="gemini-2.5-flash",
    name="especialista_derivacion",
    description="Especialista de Derivación sobre recursos de ayuda y derivación responsable.",
    instruction=SYSTEM_INSTRUCTION
)
