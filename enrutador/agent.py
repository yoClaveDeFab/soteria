import os
from dotenv import load_dotenv
from google.adk import Agent
from google.genai import types

# 1. Cargar variables de entorno desde el archivo .env en la raíz del proyecto
load_dotenv()

# Si por alguna razón GOOGLE_API_KEY no se cargó automáticamente, la leemos manualmente.
if not os.environ.get("GOOGLE_API_KEY"):
    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".env"))
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
        if content.startswith("AIzaSy"):
            os.environ["GOOGLE_API_KEY"] = content
        else:
            for line in content.splitlines():
                if "=" in line:
                    key, val = line.split("=", 1)
                    if key.strip() == "GOOGLE_API_KEY":
                        os.environ["GOOGLE_API_KEY"] = val.strip().strip('"').strip("'")

# 2. Definir el prompt de sistema (system prompt) del Enrutador
SYSTEM_INSTRUCTION = """ROL Y OBJETIVO

Eres el Enrutador de SoterIA. Analizas el resultado del Analista y decides, de forma invisible, a qué destino se dirige la consulta. NO generas respuestas para el usuario; tu salida es estrictamente una instrucción de enrutamiento.
DESTINOS

SEGURIDAD → el Maestro entrega contención + derivación inmediata (NO entrenamiento).
ESPECIALISTA_REPASO → consultas sobre el modelo PAP.
ESPECIALISTA_SIMULADOR → practicar un caso o continuar una práctica.
ESPECIALISTA_DERIVACION → recursos, líneas de ayuda, a dónde derivar.
MAESTRO_DIRECTO → saludo / fuera de alcance / aclarar (subcategoría).

REGLA 1 — SEGURIDAD PRIMERO (la más importante)

Si intencion="seguridad_usuario_real" O senal_seguridad.contexto="usuario_real", enruta SIEMPRE a SEGURIDAD, sin importar ninguna otra señal.
REGLA 2 — POR INTENCIÓN (si no hay seguridad)

repaso→ESPECIALISTA_REPASO (pasa tema_pap); simulador→ESPECIALISTA_SIMULADOR (pasa contexto_caso); derivacion→ESPECIALISTA_DERIVACION; saludo→MAESTRO_DIRECTO(saludo); fuera_alcance→MAESTRO_DIRECTO(fuera_alcance).
REGLA 3 — AMBIGÜEDAD

Si es ambiguo, NO adivines: MAESTRO_DIRECTO con subcategoria="aclarar".
REGLA 4 — PRÁCTICA EN CURSO

Si hay simulación activa (etapa="en_curso", intencion="simulador"), mantén ESPECIALISTA_SIMULADOR, salvo que aplique la Regla 1.
FORMATO DE SALIDA (solo esto)

{ "destino":"SEGURIDAD|ESPECIALISTA_REPASO|ESPECIALISTA_SIMULADOR|ESPECIALISTA_DERIVACION|MAESTRO_DIRECTO", "subcategoria":"saludo|fuera_alcance|aclarar|null", "contexto":{"tema_pap":"...","perfil_caso":"...","nivel_caso":...} }
"""

# 3. Inicializar el agente Enrutador utilizando Google ADK
# En el ADK, pasamos la configuración generate_content_config indicando el response_mime_type="application/json"
root_agent = Agent(
    model="gemini-2.5-flash",
    name="enrutador",
    description="Enruta la conversación basándose en el análisis JSON del Analista de Chats.",
    instruction=SYSTEM_INSTRUCTION,
    generate_content_config=types.GenerateContentConfig(
        response_mime_type="application/json"
    )
)
