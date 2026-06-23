import sys
import asyncio
from google.genai import types
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from analista_chats import root_agent

async def main():
    print("==================================================================")
    print("    BIENVENIDO AL ANALISTA DE CHATS DE SoterIA (Google ADK)    ")
    print("==================================================================")
    print("Instrucciones:")
    print("- Para finalizar, escribe 'salir' o 'exit'.")
    print("- Escribe el mensaje del facilitador y presiona Enter.")
    print("- El Analista analizará el mensaje y mostrará el objeto JSON resultante.")
    print("==================================================================\n")

    session_service = InMemorySessionService()
    import uuid
    session_id = f"test_analista_{uuid.uuid4()}"
    user_id = "facilitador_test"
    app_name = "analista_app"

    # Crear la sesión persistente
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

    while True:
        try:
            user_input = input("\nMensaje del Facilitador: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nSaliendo...")
            break

        if not user_input:
            continue

        if user_input.lower() in ["salir", "exit"]:
            print("Hasta pronto.")
            break

        content = types.Content(role="user", parts=[types.Part(text=user_input)])
        
        print("\nJSON devuelto por el Analista:")
        print("------------------------------------------------------------------")
        
        try:
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=content
            ):
                print(f"\n[EVENT] Author: {event.author}")
                import json
                print(json.dumps(event.model_dump(exclude_none=True, mode="json"), indent=2, ensure_ascii=False))
            print()
        except Exception as e:
            print(f"\n[Error en ejecución]: {e}")
        print("------------------------------------------------------------------")

if __name__ == "__main__":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\nOcurrió un error: {e}")
