import sys
import asyncio
from google.genai import types
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from especialista_simulador import root_agent

# Ensure UTF-8 output encoding for emojis
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

async def test_prompts():
    session_service = InMemorySessionService()
    app_name = "especialista_simulador_app"
    user_id = "facilitador_test"
    
    # Test case: Select specific case in English
    session_id_en = "session_test_en"
    await session_service.create_session(app_name=app_name, user_id=user_id, session_id=session_id_en)
    runner_en = Runner(agent=root_agent, app_name=app_name, session_service=session_service)
    
    # Message 1
    msg1 = "I want to practice a grief case"
    print(f"\n--- USER (EN): {msg1} ---")
    content1 = types.Content(role="user", parts=[types.Part(text=msg1)])
    async for event in runner_en.run_async(user_id=user_id, session_id=session_id_en, new_message=content1):
        pass # Consume response

    # Message 2
    msg2 = "I want to practice case P-10 in advanced level"
    print(f"\n--- USER (EN): {msg2} ---")
    content2 = types.Content(role="user", parts=[types.Part(text=msg2)])
    print("Agent output:")
    async for event in runner_en.run_async(user_id=user_id, session_id=session_id_en, new_message=content2):
        if event.content and event.content.parts:
            for part in event.content.parts:
                if part.text:
                    print(part.text, end="", flush=True)
    print()

if __name__ == "__main__":
    asyncio.run(test_prompts())
