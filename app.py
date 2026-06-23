import uuid
import gradio as gr
from run_soteria import responder

# CSS personalizado para brindar una experiencia de diseño de alta gama (sleek dark mode)
css = """
body {
    background: radial-gradient(circle at top, #1e1b4b 0%, #09090b 100%) !important;
}
.gradio-container {
    max-width: 950px !important;
    margin: 0 auto !important;
    padding-top: 30px !important;
}
.header-container {
    text-align: center;
    margin-bottom: 25px;
    animation: fadeIn 1.2s ease-in-out;
}
.header-title {
    font-size: 3.2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #c7d2fe 0%, #818cf8 50%, #4f46e5 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 8px;
    letter-spacing: -0.05em;
}
.header-subtitle {
    font-size: 1.15rem;
    color: #a1a1aa;
    font-weight: 400;
}
.warning-banner {
    background: rgba(239, 68, 68, 0.08) !important;
    border: 1px solid rgba(239, 68, 68, 0.25) !important;
    border-radius: 16px !important;
    padding: 18px 24px !important;
    margin-bottom: 30px !important;
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    animation: slideDown 0.8s cubic-bezier(0.16, 1, 0.3, 1);
}
.warning-text {
    color: #fca5a5 !important;
    font-size: 0.95rem;
    font-weight: 500;
    line-height: 1.6;
    text-align: center;
    margin: 0 !important;
}
.chat-container {
    background: rgba(24, 24, 27, 0.55) !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    border-radius: 24px !important;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    padding: 15px !important;
    animation: fadeInUp 1s cubic-bezier(0.16, 1, 0.3, 1);
}
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}
@keyframes slideDown {
    from { transform: translateY(-20px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
}
@keyframes fadeInUp {
    from { transform: translateY(30px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
}
"""

async def predict_wrapper(message, history, session_state):
    """Encapsulador para aislar la llamada y refrescar el ID de sesión si el chat se limpia."""
    # Si el historial se borra o la sesión es nueva, generamos un id_sesion único
    if not history or "id_sesion" not in session_state:
        session_state["id_sesion"] = f"soteria_{uuid.uuid4()}"
    
    session_id = session_state["id_sesion"]
    user_id = "gradio_user"
    
    # Ejecutar el flujo de agentes (responder)
    response = await responder(message, history, session_id, user_id)
    return response

def get_initial_state():
    return {"id_sesion": f"soteria_{uuid.uuid4()}"}

# Construir bloque de interfaz principal (theme y css se pasan en launch() en Gradio 6.0)
with gr.Blocks() as demo:
    # Encabezado
    gr.HTML("""
    <div class='header-container'>
        <h1 class='header-title'>🛡️ SoterIA</h1>
        <p class='header-subtitle'>Asistente de Entrenamiento en Primeros Auxilios Psicológicos (PAP)</p>
    </div>
    """)
    
    # Banner de advertencia obligatorio
    gr.HTML("""
    <div class='warning-banner'>
        <p class='warning-text'>
            ⚠️ <strong>Aviso Importante:</strong> SoterIA es un simulador de 
            <strong>ENTRENAMIENTO</strong> en Primeros Auxilios Psicológicos, no atención en crisis. 
            Si tú o alguien está en peligro, llama al <strong>911</strong>, 
            Línea de la Vida (<strong>800 911 2000</strong>) o SAPTEL (<strong>55 5259 8121</strong>).
        </p>
    </div>
    """)
    
    # Contenedor de Chat
    with gr.Column(elem_classes="chat-container"):
        gr.ChatInterface(
            fn=predict_wrapper,
            additional_inputs=[gr.State(value=get_initial_state)],
            textbox=gr.Textbox(placeholder="Escribe tu mensaje aquí...", container=False, scale=7),
        )

if __name__ == "__main__":
    demo.queue().launch(
        theme=gr.themes.Soft(primary_hue="indigo", secondary_hue="blue"),
        css=css
    )
