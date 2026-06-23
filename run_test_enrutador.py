import sys
import asyncio
import json
from google.genai import types
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai.errors import ServerError
from enrutador import root_agent

# JSONs de prueba obligatorios
PRUEBAS_OBLIGATORIAS = [
    # 1. intencion: "repaso" -> debe dar ESPECIALISTA_REPASO
    {
        "intencion": "repaso",
        "etapa": "inicio",
        "senal_seguridad": {"detectada": False, "contexto": "practica", "tipo": None},
        "tema_pap": "abcde",
        "contexto_caso": {"perfil_caso": None, "nivel_caso": None},
        "metricas": {"tipo_consulta": "consulta_directa", "funcion_sugerida": "repaso_contenido", "seguridad_activada": False}
    },
    # 2. intencion: "simulador" -> debe dar ESPECIALISTA_SIMULADOR
    {
        "intencion": "simulador",
        "etapa": "inicio",
        "senal_seguridad": {"detectada": False, "contexto": "practica", "tipo": None},
        "tema_pap": None,
        "contexto_caso": {"perfil_caso": "duelo", "nivel_caso": 2},
        "metricas": {"tipo_consulta": "iniciar_simulacion", "funcion_sugerida": "seleccionar_caso", "seguridad_activada": False}
    },
    # 3. intencion: "derivacion" -> debe dar ESPECIALISTA_DERIVACION
    {
        "intencion": "derivacion",
        "etapa": "inicio",
        "senal_seguridad": {"detectada": False, "contexto": "practica", "tipo": None},
        "tema_pap": "derivacion",
        "contexto_caso": {"perfil_caso": None, "nivel_caso": None},
        "metricas": {"tipo_consulta": "consulta_directa", "funcion_sugerida": "derivar_recursos", "seguridad_activada": False}
    },
    # 4. senal_seguridad.contexto: "usuario_real" -> debe dar SEGURIDAD (¡prioridad sobre otra intención!)
    {
        "intencion": "simulador",
        "etapa": "en_curso",
        "senal_seguridad": {"detectada": True, "contexto": "usuario_real", "tipo": "ideacion_suicida"},
        "tema_pap": None,
        "contexto_caso": {"perfil_caso": "duelo", "nivel_caso": 2},
        "metricas": {"tipo_consulta": "crisis_emocional", "funcion_sugerida": "activar_protocolo_seguridad", "seguridad_activada": True}
    }
]

async def call_enrutador(runner, session_service, app_name, session_id, user_id, json_input):
    # Formatear el JSON como string de entrada
    json_str = json.dumps(json_input, ensure_ascii=False)
    content = types.Content(role="user", parts=[types.Part(text=json_str)])
    
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
                print("  [Alerta]: 503 detectado, reintentando en 5s...")
                await asyncio.sleep(5)
                try:
                    await session_service.delete_session(app_name=app_name, user_id=user_id, session_id=session_id)
                except Exception as ex:
                    print(f"Error al borrar sesión: {ex}")
                await session_service.create_session(
                    app_name=app_name,
                    user_id=user_id,
                    session_id=session_id
                )
            else:
                return f"Error 503: {e}"
        except Exception as e:
            return f"Error: {e}"

async def main():
    print("==================================================================")
    print("      BIENVENIDO AL ENRUTADOR DE SoterIA (Google ADK)      ")
    print("==================================================================\n")

    session_service = InMemorySessionService()
    session_id = "session_enrutador_01"
    user_id = "test_user"
    app_name = "enrutador_app"

    await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id
    )

    runner = Runner(
        agent=root_agent,
        app_name=app_name,
        session_service=session_service
    )

    print("--- EJECUTANDO PRUEBAS OBLIGATORIAS ---")
    for i, test_json in enumerate(PRUEBAS_OBLIGATORIAS, 1):
        print(f"\n[Prueba {i}] JSON de entrada:")
        print(json.dumps(test_json, indent=2, ensure_ascii=False))
        
        # Generar un ID de sesión fresco por prueba para que no interfieran entre sí
        test_session_id = f"session_enrutador_test_{i}"
        await session_service.create_session(
            app_name=app_name,
            user_id=user_id,
            session_id=test_session_id
        )
        
        response = await call_enrutador(runner, session_service, app_name, test_session_id, user_id, test_json)
        print("Decisión del Enrutador:")
        try:
            parsed = json.loads(response.strip())
            print(json.dumps(parsed, indent=2, ensure_ascii=False))
        except Exception:
            print(response)
        print("-" * 50)

    print("\n--- MODO INTERACTIVO (escribe 'salir' o 'exit' para terminar) ---")
    print("Pega un objeto JSON del Analista:")
    
    while True:
        try:
            print("\nIntroduce JSON (presiona Enter al terminar):")
            # Para permitir pegar JSONs multilínea, leemos hasta encontrar un corchete de cierre }
            lines = []
            while True:
                line = input().strip()
                if line.lower() in ["salir", "exit"]:
                    print("Hasta pronto.")
                    return
                lines.append(line)
                # Si parece que cerramos el JSON o si es de una línea
                if not line or line.endswith("}") or (line.startswith("{") and line.endswith("}")):
                    break
            
            user_input = "".join(lines).strip()
            if not user_input:
                continue
            
            try:
                json_data = json.loads(user_input)
            except json.JSONDecodeError as je:
                print(f"[Error de sintaxis JSON]: {je}. Reintenta.")
                continue

            test_session_id = "session_enrutador_interactive"
            # Asegurar sesión fresca
            try:
                await session_service.delete_session(app_name, user_id, test_session_id)
            except Exception:
                pass
            await session_service.create_session(
                app_name=app_name,
                user_id=user_id,
                session_id=test_session_id
            )

            print("Enrutando...")
            response = await call_enrutador(runner, session_service, app_name, test_session_id, user_id, json_data)
            print("\nResultado:")
            try:
                parsed = json.loads(response.strip())
                print(json.dumps(parsed, indent=2, ensure_ascii=False))
            except Exception:
                print(response)
        except (KeyboardInterrupt, EOFError):
            print("\nSaliendo...")
            break

if __name__ == "__main__":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\nOcurrió un error: {e}")
