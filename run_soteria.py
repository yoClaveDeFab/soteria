import sys
import asyncio
import json
from google.genai import types
from google.genai.errors import ServerError
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner

# Importar todos los agentes necesarios del proyecto
from analista_chats import root_agent as agent_analista
from enrutador import root_agent as agent_enrutador
from especialista_repaso import root_agent as agent_repaso
from especialista_derivacion import root_agent as agent_derivacion
from especialista_simulador import root_agent as agent_simulador
from maestro import root_agent as agent_maestro

# Configurar terminal para codificación UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

async def call_agent_with_retry(runner, session_service, app_name, session_id, user_id, text_input):
    content = types.Content(role="user", parts=[types.Part(text=text_input)])
    for attempt in range(4):
        try:
            response_parts = []
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=content
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            response_parts.append(part.text)
            return "".join(response_parts)
        except ServerError as e:
            if "503" in str(e) and attempt < 3:
                print(f"\n[Aviso]: Error temporal del modelo (503). Reintentando en 5s... (Intento {attempt + 1}/4)")
                await asyncio.sleep(5)
                # Reseteamos sesión en caso de error de conexión para evitar envíos duplicados
                try:
                    await session_service.delete_session(app_name=app_name, user_id=user_id, session_id=session_id)
                except Exception:
                    pass
                await session_service.create_session(
                    app_name=app_name,
                    user_id=user_id,
                    session_id=session_id
                )
            else:
                raise e
        except Exception as e:
            raise e

def detect_language_local(text: str) -> str:
    text_lower = text.lower()
    words = text_lower.split()
    
    english_words = {
        "the", "and", "you", "i", "to", "of", "a", "is", "in", "it", "that", "for", "on", "are", 
        "as", "with", "they", "at", "be", "this", "have", "from", "or", "one", "had", "by", "but", 
        "not", "what", "all", "were", "we", "when", "your", "can", "there", "use", "an", "each", 
        "which", "how", "their", "if", "will", "up", "other", "about", "out", "many", "then", "them", 
        "these", "so", "some", "would", "make", "like", "him", "into", "has", "look", "more", "write", 
        "go", "see", "no", "could", "people", "my", "than", "first", "been", "call", "who", "now", "find",
        "hello", "hi", "grief", "done", "help", "please", "thanks", "thank"
    }
    
    spanish_words = {
        "el", "la", "los", "las", "un", "una", "unos", "unas", "y", "o", "pero", "si", "no", "por", 
        "para", "con", "en", "de", "del", "al", "que", "es", "son", "esta", "este", "esto", "yo", 
        "tu", "él", "ella", "nosotros", "ellos", "me", "te", "se", "lo", "le", "como", "mas", "más", 
        "mi", "mis", "tus", "su", "sus", "cómo", "hola", "gracias", "duelo", "accidente", "violencia", 
        "desastre", "terminar", "ayuda", "por favor"
    }
    
    en_count = sum(1 for w in words if w in english_words)
    es_count = sum(1 for w in words if w in spanish_words)
    
    if en_count > es_count:
        return "en"
    return "es"

# Inicializar servicios globales para soportar múltiples sesiones concurrentes (ej: Gradio)
session_service = InMemorySessionService()

apps = {
    "analista": ("soteria_analista", agent_analista),
    "enrutador": ("soteria_enrutador", agent_enrutador),
    "repaso": ("soteria_repaso", agent_repaso),
    "derivacion": ("soteria_derivacion", agent_derivacion),
    "simulador": ("soteria_simulador", agent_simulador),
    "maestro": ("soteria_maestro", agent_maestro),
}

runners = {}
for key, (app_name, agent) in apps.items():
    runners[key] = Runner(agent=agent, app_name=app_name, session_service=session_service)

initialized_sessions = set()

async def ensure_session_initialized(session_id: str, user_id: str):
    """Inicializa la sesión para cada uno de los agentes de forma segura."""
    if session_id in initialized_sessions:
        return
    for key, (app_name, agent) in apps.items():
        try:
            await session_service.create_session(
                app_name=app_name,
                user_id=user_id,
                session_id=session_id
            )
        except Exception:
            # Si ya existe, se ignora la excepción
            pass
    initialized_sessions.add(session_id)

async def responder_stream(user_input: str, history, session_id: str, user_id: str = "gradio_user"):
    """Ejecuta el flujo completo de agentes (Analista -> Enrutador -> Especialista -> Maestro) en streaming."""
    try:
        # Asegurar que las sesiones estén preparadas para esta sesión de usuario
        await ensure_session_initialized(session_id, user_id)
        
        # 1. Ejecutar el Analista de Chats
        analisis_json_str = await call_agent_with_retry(
            runners["analista"], session_service, "soteria_analista", session_id, user_id, user_input
        )

        # 2. Ejecutar el Enrutador
        enrutamiento_json_str = await call_agent_with_retry(
            runners["enrutador"], session_service, "soteria_enrutador", session_id, user_id, analisis_json_str
        )

        # Parsear las decisiones del enrutador
        try:
            decision = json.loads(enrutamiento_json_str.strip())
            destino = decision.get("destino", "MAESTRO_DIRECTO")
        except Exception:
            destino = "MAESTRO_DIRECTO"

        # 3. Flujo condicional basado en la decisión del Enrutador
        final_prompt = ""
        lang = detect_language_local(user_input)

        if destino == "SEGURIDAD":
            if lang == "en":
                final_prompt = (
                    "INTERNAL SAFETY INSTRUCTION: The real user/facilitator is experiencing a personal crisis. "
                    "Activate your safety gate immediately, halt any active simulation, and provide direct "
                    "national crisis resources with SoterIA's warmth and tone."
                )
            else:
                final_prompt = (
                    "INSTRUCCIÓN INTERNA DE SEGURIDAD: El facilitador real se encuentra en crisis personal. "
                    "Activa tu barrera de seguridad de inmediato, detén toda simulación y proporciona los "
                    "recursos nacionales directos (911, Línea de la Vida, SAPTEL) con calidez y tono de SoterIA."
                )

        elif destino == "MAESTRO_DIRECTO":
            final_prompt = user_input

        elif destino == "ESPECIALISTA_REPASO":
            explicacion_especialista = await call_agent_with_retry(
                runners["repaso"], session_service, "soteria_repaso", session_id, user_id, user_input
            )
            if lang == "en":
                final_prompt = (
                    f"The review specialist has generated this explanation for the facilitator's query:\n"
                    f"{explicacion_especialista}\n\n"
                    f"CRITICAL LANGUAGE RULE: The user is communicating in English. If any part of the explanation above is in Spanish, you MUST translate it to English. "
                    f"Deliver this information to the facilitator using SoterIA's unified warm voice, without altering any facts."
                )
            else:
                final_prompt = (
                    f"El especialista de repaso ha generado esta explicación para la consulta del facilitador:\n"
                    f"{explicacion_especialista}\n\n"
                    f"REGLA CRÍTICA DE IDIOMA: El usuario se está comunicando en español. Si alguna parte de la explicación está en inglés, debes traducirla al español. "
                    f"Entrégale esta información al facilitador utilizando tu voz y cuidado de SoterIA, sin alterar datos."
                )

        elif destino == "ESPECIALISTA_DERIVACION":
            recursos_especialista = await call_agent_with_retry(
                runners["derivacion"], session_service, "soteria_derivacion", session_id, user_id, user_input
            )
            if lang == "en":
                final_prompt = (
                    f"The referral specialist has provided these resources and guidance:\n"
                    f"{recursos_especialista}\n\n"
                    f"CRITICAL LANGUAGE RULE: The user is communicating in English. If any part of the resources above is in Spanish, you MUST translate it to English (except for official organization names like 'Línea de la Vida' or 'SAPTEL' and contact numbers). "
                    f"Communicate this information to the facilitator using SoterIA's warm and caring voice, "
                    f"delivering the exact phone numbers with warmth."
                )
            else:
                final_prompt = (
                    f"El especialista de derivación ha proporcionado estos recursos e indicaciones:\n"
                    f"{recursos_especialista}\n\n"
                    f"REGLA CRÍTICA DE IDIOMA: El usuario se está comunicando en español. Si alguna parte de los recursos está en inglés, debes traducirla al español (manteniendo nombres propios y números). "
                    f"Comunica esta información al facilitador utilizando tu voz y cuidado de SoterIA, "
                    f"entregando los números de teléfono exactos con calidez."
                )

        elif destino == "ESPECIALISTA_SIMULADOR":
            simulador_output = await call_agent_with_retry(
                runners["simulador"], session_service, "soteria_simulador", session_id, user_id, user_input
            )
            es_feedback = any(k in simulador_output for k in ["Fortalezas", "Áreas de mejora", "Retroalimentación", "✅", "🔧", "Strengths", "Improvements", "Feedback"])
            if es_feedback:
                if lang == "en":
                    final_prompt = (
                        f"This is the final feedback for the practice session provided by the simulator:\n"
                        f"{simulador_output}\n\n"
                        f"CRITICAL LANGUAGE RULE: The user is communicating in English. If any part of the feedback/scorecard above is in Spanish, you MUST translate it to English. "
                        f"Deliver this feedback scorecard to the facilitator using SoterIA's official warm voice."
                    )
                else:
                    final_prompt = (
                        f"Esta es la retroalimentación final de la práctica brindada por el simulador:\n"
                        f"{simulador_output}\n\n"
                        f"REGLA CRÍTICA DE IDIOMA: El usuario se está comunicando en español. Si alguna parte del feedback está en inglés, debes traducirla al español. "
                        f"Entrégale esta evaluación al facilitador utilizando tu voz oficial de SoterIA."
                    )
            else:
                if lang == "en":
                    final_prompt = (
                        f"This is a dialog turn from the simulation character:\n"
                        f"{simulador_output}\n\n"
                        f"CRITICAL LANGUAGE RULE: The user is communicating in English. If the dialog turn above is in Spanish, you MUST translate it to English so the character speaks in English. "
                        f"Deliver it exactly to the user. Do not add any meta-explanations or out-of-character comments."
                    )
                else:
                    final_prompt = (
                        f"Este es un turno del personaje de la simulación (diálogo en primer plano del personaje):\n"
                        f"{simulador_output}\n\n"
                        f"REGLA CRÍTICA DE IDIOMA: El usuario se está comunicando en español. Si el diálogo está en inglés, debes traducirlo al español. "
                        f"Transmítelo exactamente de forma IDÉNTICA e INALTERADA al usuario. No añadas explicaciones ni comentarios fuera de personaje."
                    )

        # 4. Transmitir en streaming la llamada final al Maestro
        content = types.Content(role="user", parts=[types.Part(text=final_prompt)])
        response_parts = []
        async for event in runners["maestro"].run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if part.text:
                        response_parts.append(part.text)
                        yield "".join(response_parts)

    except Exception as e:
        lang = detect_language_local(user_input)
        if lang == "en":
            yield "Oof — I'm getting a lot of requests right now and got a bit overloaded. Give me a few seconds and try again — I'm still here. 🤍"
        else:
            yield "Uy, justo ahora estoy recibiendo muchas consultas y me saturé tantito. Dame unos segundos y vuelve a intentar — aquí sigo. 🤍"

async def responder(user_input: str, history, session_id: str, user_id: str = "gradio_user") -> str:
    """Ejecuta el flujo completo de agentes (Analista -> Enrutador -> Especialista -> Maestro) de forma bloqueante."""
    last_chunk = ""
    async for chunk in responder_stream(user_input, history, session_id, user_id):
        last_chunk = chunk
    return last_chunk

async def main():
    print("==================================================================")
    print("           SOTERIA - SISTEMA PAP ORQUESTRADO (Google ADK)        ")
    print("==================================================================")
    print("Instrucciones:")
    print("- Escribe tu mensaje y presiona Enter para interactuar.")
    print("- Escribe 'salir' o 'exit' para finalizar la sesión.")
    print("==================================================================\n")

    user_id = "facilitador_user"
    import uuid
    session_id = f"soteria_{uuid.uuid4()}"

    # Iniciar flujo saludando (primer contacto)
    bienvenida = await responder("Hola", [], session_id, user_id)
    print(f"SoterIA: {bienvenida}\n")

    while True:
        try:
            user_input = input("Usuario: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nSaliendo...")
            break

        if not user_input:
            continue

        if user_input.lower() in ["salir", "exit"]:
            print("Hasta pronto.")
            break

        response = await responder(user_input, [], session_id, user_id)
        print(f"\nSoterIA: {response}\n")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\nError al ejecutar la aplicación: {e}")

