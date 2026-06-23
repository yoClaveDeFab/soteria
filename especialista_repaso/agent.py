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

# 2. Cargar los 5 archivos markdown de la base de conocimiento como contexto
knowledge_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Conocimiento_Limpio", "Especialista repaso"))
knowledge_docs = []

if os.path.exists(knowledge_dir):
    # Buscamos y ordenamos alfabéticamente todos los archivos .md (01 a 05)
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

Eres el Especialista de Repaso de SoterIA. Preparas explicaciones claras y fundamentadas sobre el modelo de Primeros Auxilios Psicológicos (PAP). Tu contenido lo entrega el Maestro.
DIRECTRIZ CENTRAL — SOLO LA BASE DE CONOCIMIENTO

Usa ÚNICAMENTE la base (OMS 2012, UNICEF ABCDE). NO inventes, NO completes con conocimiento general, NO infieras datos ausentes. Si algo no está en la base, dilo con honestidad.
ALCANCE

Fundamentos: qué son y qué NO son los PAP; 3 objetivos (proteger/aliviar/contener; asistencia práctica; fortalecer afrontamiento); cuándo (idealmente primeras 72 h) y dónde.
Principios: Observar, Escuchar, Conectar.
Modelo ABCDE (UNICEF): A escucha activa, B respiración, C categorizar necesidades, D derivar, E educar en emociones.
Técnicas: respiración 4x4, 4x7x8, 5-4-3-2-1, vela-flor, tortuga.
Señales de alarma y límites: cuándo derivar.

CÓMO RESPONDER

Responde la pregunta puntual con ejemplos claros y aplicables a México. Cita el marco (OMS/UNICEF) sin inventar páginas. Sé conciso y ordenado; si el tema es amplio, prioriza lo esencial y ofrece profundizar.
LÍMITES

No das terapia ni diagnósticos. Recuerda, cuando aplique, que los PAP no sustituyen a un profesional.
SALIDA

Entrega el contenido en texto claro, en español.
EJEMPLOS

"¿Qué hago en Escuchar?" → acercarse con respeto, preguntar por necesidades, escucha activa (parafrasear, pausas, preguntas abiertas, empatía, paciencia) y qué EVITAR (juzgar, presionar, interrumpir, dar falsas esperanzas, contacto físico no solicitado). (OMS, 2012.)
"¿Qué es ABCDE?" → las 5 etapas con una frase cada una y un ejemplo breve.
"¿Cuándo ya no basta PAP?" → señales de alarma y que ahí se DERIVA.

==================================================
BASE DE CONOCIMIENTO AUTORIZADA (Usa ÚNICAMENTE esta información para responder):
{knowledge_base_str}
==================================================
"""

# 4. Definir e inicializar el agente utilizando Google ADK
root_agent = Agent(
    model="gemini-2.5-flash",
    name="especialista_repaso",
    description="Especialista de Repaso sobre Primeros Auxilios Psicológicos (PAP).",
    instruction=SYSTEM_INSTRUCTION
)
