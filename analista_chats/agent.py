import os
from dotenv import load_dotenv
from google.adk import Agent
from google.genai import types
from google.adk.tools.mcp_tool import McpToolset, StdioConnectionParams
from mcp import StdioServerParameters
from typing import Optional, Union

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

# Alinear SERVICE_ACCOUNT_PATH a GOOGLE_APPLICATION_CREDENTIALS si está disponible
if os.environ.get("SERVICE_ACCOUNT_PATH") and not os.environ.get("GOOGLE_APPLICATION_CREDENTIALS"):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.environ.get("SERVICE_ACCOUNT_PATH")

def google_sheets_header_provider(readonly_context) -> dict[str, str]:
    """Obtiene dinámicamente un token de acceso de Google para el servidor MCP.
    
    Busca credenciales en las siguientes fuentes ordenadas por prioridad:
    1. SERVICE_ACCOUNT_PATH o GOOGLE_APPLICATION_CREDENTIALS (archivo local).
    2. GOOGLE_SERVICE_ACCOUNT_JSON (contenido JSON de la cuenta de servicio en variable de entorno).
    3. GOOGLE_REFRESH_TOKEN (OAuth 2.0 Refresh Token con Client ID/Secret en variables de entorno).
    4. google.auth.default() (Application Default Credentials locales).
    """
    import os
    import json
    import google.auth
    from google.auth.transport.requests import Request
    from google.oauth2 import service_account
    from google.oauth2.credentials import Credentials as OAuthCredentials
    import logging
    try:
        scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        cred_path = os.environ.get("SERVICE_ACCOUNT_PATH") or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
        
        # 1. Archivo local de cuenta de servicio
        if cred_path and os.path.exists(cred_path):
            credentials = service_account.Credentials.from_service_account_file(
                cred_path, scopes=scopes
            )
        # 2. JSON de cuenta de servicio en variable de entorno
        elif os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON"):
            info = json.loads(os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON"))
            credentials = service_account.Credentials.from_service_account_info(
                info, scopes=scopes
            )
        # 3. OAuth 2.0 Refresh Token
        elif os.environ.get("GOOGLE_REFRESH_TOKEN") and os.environ.get("GOOGLE_CLIENT_ID") and os.environ.get("GOOGLE_CLIENT_SECRET"):
            credentials = OAuthCredentials(
                token=None,
                refresh_token=os.environ.get("GOOGLE_REFRESH_TOKEN"),
                token_uri="https://oauth2.googleapis.com/token",
                client_id=os.environ.get("GOOGLE_CLIENT_ID"),
                client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
                scopes=scopes
            )
        # 4. Credenciales por defecto locales (ADC)
        else:
            credentials, project = google.auth.default(scopes=scopes)
            
        credentials.refresh(Request())
        return {"Authorization": f"Bearer {credentials.token}"}
    except Exception as e:
        logging.getLogger("google_adk").warning(
            f"SoterIA Auth Warning: No se pudo obtener el token de acceso dinámico: {e}"
        )
        return {}



# Configurar el servidor MCP de Google Sheets
sheets_mcp_toolset = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command='npx',
            args=["-y", "google-sheets-mcp"],
            env=os.environ.copy()
        )
    ),
    header_provider=google_sheets_header_provider
)

async def append_row(
    id_sesion: str = "",
    marca_temporal: str = "",
    intencion: str = "",
    tema_pap: str = "",
    perfil_caso: str = "",
    nivel_caso: str = "",
    seguridad_activada: bool = False,
    satisfaccion: str = "",
    comentario: str = ""
) -> dict:
    """Registra una fila en la hoja de Google Sheets SoterIA_Metricas usando el servidor MCP.

    Args:
        id_sesion: ID único de la sesión de chat.
        marca_temporal: Marca temporal en formato ISO.
        intencion: Intención identificada en el mensaje.
        tema_pap: Tema de primeros auxilios psicológicos.
        perfil_caso: Perfil del caso simulado.
        nivel_caso: Nivel de complejidad del caso.
        seguridad_activada: Indica si se activó la alerta de seguridad.
        satisfaccion: Nivel de satisfacción de la encuesta (cierre).
        comentario: Comentario de la encuesta (cierre).
    """
    row = [
        id_sesion,
        marca_temporal,
        intencion,
        tema_pap,
        perfil_caso,
        nivel_caso,
        str(seguridad_activada).lower(),
        satisfaccion,
        comentario
    ]
    
    spreadsheet_id = "1o4ERfUvjSYbAhdb_V4tJRp7OIj5b_Tg72fme5LK-JIs"
    range_name = "Untitled"
    
    try:
        headers = google_sheets_header_provider(None)
        session = await sheets_mcp_toolset._mcp_session_manager.create_session(headers=headers)
        response = await session.call_tool(
            "values_append",
            arguments={
                "spreadsheetId": spreadsheet_id,
                "range": range_name,
                "values": [row],
                "valueInputOption": "USER_ENTERED"
            }
        )
        return response.model_dump(exclude_none=True, mode="json")
    except Exception as e:
        import logging
        logging.getLogger("google_adk").warning(f"Error al registrar métricas en Google Sheets vía MCP: {e}")
        return {"status": "error", "message": f"Metrics logging failed: {e}"}


# 2. Definir el prompt de sistema (system prompt) del Analista de Chats
SYSTEM_INSTRUCTION = """ROL Y OBJETIVO

Eres el Analista de Chats de SoterIA (asistente de entrenamiento en PAP). Analizas el mensaje del facilitador y entregas SOLO un objeto JSON para el Enrutador. NO generas respuestas para el usuario. NO saludas.
QUÉ EXTRAER

intencion: "repaso" | "simulador" | "derivacion" | "saludo" | "fuera_alcance" | "seguridad_usuario_real".
etapa: "inicio" | "en_curso" | "seguimiento".
senal_seguridad: { detectada(true/false), contexto("practica"|"usuario_real"), tipo(texto|null) }.
tema_pap: "fundamentos"|"principios"|"abcde"|"tecnicas"|"senales_alarma"|"derivacion"|null.
contexto_caso: { perfil_caso("desastre"|"accidente"|"duelo"|"violencia"|null), nivel_caso(1|2|3|null) }.

DETECCIÓN DE SEGURIDAD (CRÍTICO)

Distingue una señal dentro de un CASO DE PRÁCTICA (el facilitador simula) de una señal del USUARIO REAL (la persona expresa estar mal ella misma). Ante duda del contexto, marca contexto="usuario_real" (prioriza la seguridad).
REGLAS

Si una simulación está en curso (etapa="en_curso"), mantén intencion="simulador", salvo señal de seguridad del usuario real (prioridad absoluta).
No respondas al usuario. No agregues texto fuera del JSON.

REGISTRO DE MÉTRICAS (MCP)
Después de analizar el mensaje, además del JSON, agrega UNA fila a la hoja SoterIA_Metricas usando la herramienta append_row, con los valores EN ESTE ORDEN:
  id_sesion, marca_temporal (ISO), intencion, tema_pap, perfil_caso, nivel_caso, seguridad_activada, satisfaccion, comentario
Reglas:
- id_sesion lo recibes de la sesión; úsalo igual en toda la conversación.
- En cada interacción llena lo que tengas; deja satisfaccion y comentario VACÍOS.
- satisfaccion (1–5) y comentario SOLO se llenan en la fila de cierre (encuesta).
- NUNCA registres datos personales, transcripciones ni el texto del mensaje.
- Si el registro falla, continúa normal (no debe bloquear la respuesta al usuario).

FORMATO DE SALIDA (solo esto)

{ "intencion":"...", "etapa":"...", "senal_seguridad":{"detectada":false,"contexto":"practica","tipo":null}, "tema_pap":null, "contexto_caso":{"perfil_caso":null,"nivel_caso":null} }
"""

def get_analista_instruction(context) -> str:
    session_id = context.session.id
    return SYSTEM_INSTRUCTION.replace(
        "- id_sesion lo recibes de la sesión; úsalo igual en toda la conversación.",
        f"- id_sesion es '{session_id}'; úsalo igual en toda la conversación."
    )

# 3. Inicializar el agente Analista de Chats utilizando Google ADK
root_agent = Agent(
    model="gemini-2.5-flash",
    name="analista_chats",
    description="Analiza mensajes de chats de SoterIA y extrae intenciones y datos en formato JSON.",
    instruction=get_analista_instruction,
    tools=[append_row]
)
