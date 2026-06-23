import sys
import asyncio
from google.genai import types
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from especialista_repaso import root_agent

async def ask_question(question: str):
    # 1. Inicializar el servicio de sesión en memoria
    session_service = InMemorySessionService()
    
    # 2. Crear una nueva sesión para la conversación
    session = await session_service.create_session(
        app_name="especialista_repaso_app",
        user_id="user_test",
        session_id="session_test_01"
    )
    
    # 3. Crear el Runner para orquestar el agente
    runner = Runner(
        agent=root_agent,
        app_name="especialista_repaso_app",
        session_service=session_service
    )
    
    # 4. Formatear la pregunta del usuario para el ADK
    content = types.Content(role="user", parts=[types.Part(text=question)])
    
    print(f"\n>>> Pregunta: {question}")
    print(">>> Respuesta: ", end="", flush=True)
    
    # 5. Ejecutar el agente de forma asíncrona
    async for event in runner.run_async(
        user_id="user_test",
        session_id="session_test_01",
        new_message=content
    ):
        # Mostrar el contenido del evento en tiempo real
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(part.text, end="", flush=True)
    print("\n")

if __name__ == "__main__":
    # Obtener la pregunta de los argumentos de la línea de comandos o usar una por defecto
    query = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "¿Qué es el modelo ABCDE?"
    
    try:
        asyncio.run(ask_question(query))
    except Exception as e:
        print(f"\nOcurrió un error al ejecutar el agente: {e}")
        import traceback
        traceback.print_exc()
