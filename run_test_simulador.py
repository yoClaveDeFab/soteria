import sys
import asyncio
from google.genai import types
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from especialista_simulador import root_agent

async def main():
    print("==================================================================")
    print("   BIENVENIDO AL SIMULADOR DE PRÁCTICAS SoterIA (Google ADK)   ")
    print("==================================================================")
    print("Instrucciones:")
    print("- Para finalizar la simulación, escribe 'salir' o 'exit'.")
    print("- Escribe tu mensaje y presiona Enter para interactuar.")
    print("==================================================================\n")

    session_service = InMemorySessionService()
    session_id = "session_sim_01"
    user_id = "facilitador_test"
    app_name = "especialista_simulador_app"

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

    print("Simulador: Iniciando simulación... Por favor introduce tu primer mensaje.")
    print("(Ejemplo: 'Hola, me gustaría practicar un caso de Duelo en nivel básico' o simplemente 'Hola').")
    
    while True:
        try:
            # Capturar la entrada del usuario de manera síncrona
            user_input = input("\nFacilitador: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n\nSaliendo del simulador...")
            break

        if not user_input:
            continue

        if user_input.lower() in ["salir", "exit"]:
            print("Finalizando práctica del simulador. ¡Hasta pronto!")
            break

        # Formatear el mensaje del usuario para el ADK
        content = types.Content(role="user", parts=[types.Part(text=user_input)])
        
        print("Simulador: ", end="", flush=True)
        
        # Ejecutar de forma asíncrona enviando el mensaje a la misma sesión para conservar el historial
        try:
            async for event in runner.run_async(
                user_id=user_id,
                session_id=session_id,
                new_message=content
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            print(part.text, end="", flush=True)
            print()
        except Exception as e:
            print(f"\n[Error en ejecución]: {e}")

if __name__ == "__main__":
    # Configurar la terminal para admitir salida UTF-8 (emojis de retroalimentación)
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"\nOcurrió un error en el simulador: {e}")
