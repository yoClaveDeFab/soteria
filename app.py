import uuid
import gradio as gr
import asyncio
import json

js_func = """
(() => {
    const forceDark = () => {
        if (!document.documentElement.classList.contains('dark')) {
            document.documentElement.classList.add('dark');
        }
    };
    forceDark();
    const observer = new MutationObserver(forceDark);
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ['class'] });
})()
"""

# CSS personalizado para brindar una experiencia de diseño de alta gama (sleek dark mode)
css = """
body, html, .gradio-container {
    background: radial-gradient(circle at top, #1e1b4b 0%, #09090b 100%) !important;
}
.loading-notice {
    background: rgba(20, 184, 166, 0.08) !important;
    border: 1px solid rgba(20, 184, 166, 0.25) !important;
    border-radius: 16px !important;
    padding: 14px 20px !important;
    margin-bottom: 20px !important;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    animation: pulse 2.5s infinite ease-in-out;
}
.loading-notice-text {
    color: #99f6e4 !important;
    font-size: clamp(0.8rem, 2.5vw, 0.9rem);
    font-weight: 500;
    line-height: 1.5;
    text-align: center;
    margin: 0 !important;
}
@keyframes pulse {
    0% { opacity: 0.7; }
    50% { opacity: 1; }
    100% { opacity: 0.7; }
}
.gradio-container {
    max-width: 1000px !important;
    margin: 0 auto !important;
    padding: clamp(10px, 3vw, 30px) !important;
}
.header-container {
    text-align: center;
    margin-bottom: 25px;
    animation: fadeIn 1.2s ease-in-out;
}
.header-title {
    font-size: clamp(2rem, 8vw, 3.2rem);
    font-weight: 800;
    background: linear-gradient(135deg, #99f6e4 0%, #2dd4bf 50%, #0d9488 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 8px;
    letter-spacing: -0.05em;
}
.header-subtitle {
    font-size: clamp(0.95rem, 3vw, 1.15rem);
    color: #a1a1aa;
    font-weight: 400;
}
.warning-banner {
    background: rgba(239, 68, 68, 0.08) !important;
    border: 1px solid rgba(239, 68, 68, 0.25) !important;
    border-radius: 16px !important;
    padding: clamp(12px, 3vw, 18px) clamp(16px, 4vw, 24px) !important;
    margin-bottom: 30px !important;
    box-shadow: 0 4px 30px rgba(0, 0, 0, 0.2);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    animation: slideDown 0.8s cubic-bezier(0.16, 1, 0.3, 1);
}
.warning-text {
    color: #fca5a5 !important;
    font-size: clamp(0.85rem, 2.5vw, 0.95rem);
    font-weight: 500;
    line-height: 1.6;
    text-align: center;
    margin: 0 !important;
}
.sidebar-container {
    background: rgba(24, 24, 27, 0.55) !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    border-radius: 24px !important;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    padding: 20px !important;
    margin-bottom: 20px !important;
    animation: fadeInUp 1s cubic-bezier(0.16, 1, 0.3, 1);
}
.chat-column {
    margin-bottom: 20px !important;
}
.chat-container {
    background: rgba(24, 24, 27, 0.55) !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    border-radius: 24px !important;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    padding: clamp(8px, 2vw, 15px) !important;
    animation: fadeInUp 1s cubic-bezier(0.16, 1, 0.3, 1);
}
.breathing-widget {
    text-align: center;
    padding: 15px;
    background: rgba(20, 184, 166, 0.04);
    border-radius: 16px;
    border: 1px solid rgba(20, 184, 166, 0.15);
    margin-bottom: 20px;
}
.widget-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #2dd4bf;
    margin: 0 0 12px 0;
}
.breathing-circle-container {
    position: relative;
    width: 110px;
    height: 110px;
    margin: 0 auto 12px auto;
    display: flex;
    align-items: center;
    justify-content: center;
}
.breathing-circle {
    width: 60px;
    height: 60px;
    background: radial-gradient(circle, #2dd4bf 0%, #0d9488 100%);
    border-radius: 50%;
    box-shadow: 0 0 15px rgba(45, 212, 191, 0.4);
    animation: breathe4x4 16s infinite ease-in-out;
}
.breathing-text {
    position: absolute;
    font-size: 0.8rem;
    font-weight: 700;
    color: #ffffff;
    pointer-events: none;
    text-shadow: 0 1px 3px rgba(0,0,0,0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    width: 90px;
}
.breathing-text::after {
    content: "Inhala / Inhale";
    animation: breatheWords 16s infinite ease-in-out;
}
.widget-desc {
    font-size: 0.75rem;
    color: #a1a1aa;
    line-height: 1.4;
    margin: 0;
}
@keyframes breathe4x4 {
    0%, 100% { transform: scale(1); box-shadow: 0 0 10px rgba(45, 212, 191, 0.3); }
    25% { transform: scale(1.6); box-shadow: 0 0 25px rgba(45, 212, 191, 0.7); } /* Inhale 4s */
    50% { transform: scale(1.6); box-shadow: 0 0 25px rgba(45, 212, 191, 0.7); } /* Hold 4s */
    75% { transform: scale(1); box-shadow: 0 0 10px rgba(45, 212, 191, 0.3); }   /* Exhale 4s */
}
@keyframes breatheWords {
    0%, 24.9% { content: "Inhala / Inhale"; }
    25%, 49.9% { content: "Retén / Hold"; }
    50%, 74.9% { content: "Exhala / Exhale"; }
    75%, 100% { content: "Retén / Hold"; }
}
.abcde-guide {
    padding: 15px;
    background: rgba(255, 255, 255, 0.02);
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.05);
}
.abcde-step {
    font-size: 0.8rem;
    color: #e4e4e7;
    margin-bottom: 8px;
    line-height: 1.4;
}
.abcde-step strong {
    color: #2dd4bf;
    font-weight: 700;
}
.feedback-dashboard {
    display: flex;
    flex-direction: column;
    gap: 15px;
    margin-top: 10px;
    text-align: left;
}
.feedback-card {
    border-radius: 16px;
    padding: 16px;
    border: 1px solid rgba(255, 255, 255, 0.05);
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}
.fortalezas-card {
    background: rgba(16, 185, 129, 0.08) !important;
    border-color: rgba(16, 185, 129, 0.25) !important;
}
.fortalezas-card h4 {
    color: #34d399 !important;
    margin: 0 0 8px 0 !important;
    font-size: 1rem;
    font-weight: 700;
}
.mejoras-card {
    background: rgba(245, 158, 11, 0.08) !important;
    border-color: rgba(245, 158, 11, 0.25) !important;
}
.mejoras-card h4 {
    color: #fbbf24 !important;
    margin: 0 0 8px 0 !important;
    font-size: 1rem;
    font-weight: 700;
}
.seguridad-card {
    background: rgba(239, 68, 68, 0.08) !important;
    border-color: rgba(239, 68, 68, 0.25) !important;
}
.seguridad-card h4 {
    color: #fca5a5 !important;
    margin: 0 0 8px 0 !important;
    font-size: 1rem;
    font-weight: 700;
}
.principio-card, .consejo-card {
    background: rgba(45, 212, 191, 0.08) !important;
    border-color: rgba(45, 212, 191, 0.25) !important;
}
.principio-card h4, .consejo-card h4 {
    color: #2dd4bf !important;
    margin: 0 0 8px 0 !important;
    font-size: 1rem;
    font-weight: 700;
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
@media (max-width: 768px) {
    .chat-column {
        order: -1 !important;
    }
}
"""

def format_feedback_html(text: str) -> str:
    """Detecta la retroalimentación estructurada del simulador y la formatea en tarjetas HTML visuales."""
    if not any(k in text for k in ["Fortalezas", "Áreas de mejora", "Retroalimentación", "✅", "🔧"]):
        return text
    
    try:
        lines = text.split("\n")
        intro = []
        sections = {
            "fortalezas": [],
            "mejoras": [],
            "principio": [],
            "consejo": [],
            "seguridad": []
        }
        
        current_section = None
        
        for line in lines:
            line_strip = line.strip()
            if not line_strip:
                continue
            
            # Detectar sección basada en emojis
            if "✅" in line_strip and "Fortalezas" in line_strip:
                current_section = "fortalezas"
                sections[current_section].append(line_strip)
            elif "🔧" in line_strip and "mejora" in line_strip:
                current_section = "mejoras"
                sections[current_section].append(line_strip)
            elif "📖" in line_strip and "Principio" in line_strip:
                current_section = "principio"
                sections[current_section].append(line_strip)
            elif "🎯" in line_strip and ("consejo" in line_strip.lower() or "tip" in line_strip.lower()):
                current_section = "consejo"
                sections[current_section].append(line_strip)
            elif "🛡️" in line_strip and "seguridad" in line_strip.lower():
                current_section = "seguridad"
                sections[current_section].append(line_strip)
            else:
                if current_section is not None:
                    sections[current_section].append(line_strip)
                else:
                    intro.append(line_strip)
                    
        has_sections = any(len(v) > 0 for v in sections.values())
        if not has_sections:
            return text
            
        html_cards = []
        if intro:
            html_cards.append(f"<div class='feedback-intro'><p>{'<br>'.join(intro)}</p></div>")
            
        titles = {
            "fortalezas": "✅ Fortalezas / Strengths",
            "mejoras": "🔧 Áreas de Mejora / Areas to Improve",
            "principio": "📖 Principio PAP / PFA Principle",
            "consejo": "🎯 Consejo / Tip",
            "seguridad": "🛡️ Nota de Seguridad / Safety Note"
        }
        
        for key in ["fortalezas", "mejoras", "principio", "consejo", "seguridad"]:
            content_list = sections[key]
            if content_list:
                first_line = content_list[0]
                if ":" in first_line:
                    _, first_line_content = first_line.split(":", 1)
                    first_line_content = first_line_content.strip()
                else:
                    first_line_content = first_line
                    # Eliminar la etiqueta de título de la primera línea si no hay dos puntos
                    first_line_content = first_line_content.replace("✅", "").replace("Fortalezas", "")
                    first_line_content = first_line_content.replace("🔧", "").replace("Áreas de mejora", "")
                    first_line_content = first_line_content.replace("📖", "").replace("Principio PAP", "")
                    first_line_content = first_line_content.replace("🎯", "").replace("Un consejo", "")
                    first_line_content = first_line_content.replace("🛡️", "").replace("Nota de seguridad", "")
                    first_line_content = first_line_content.strip()
                
                body_lines = []
                if first_line_content:
                    body_lines.append(first_line_content)
                body_lines.extend(content_list[1:])
                
                content_html = "<br>".join(body_lines)
                card_class = f"feedback-card {key}-card"
                html_cards.append(
                    f"<div class='{card_class}'>"
                    f"  <h4>{titles[key]}</h4>"
                    f"  <p>{content_html}</p>"
                    f"</div>"
                )
                
        return "<div class='feedback-dashboard'>" + "".join(html_cards) + "</div>"
    except Exception:
        # Fallback robusto en caso de error de parseo: retornar texto plano
        return text

def get_initial_state():
    return {"id_sesion": f"soteria_{uuid.uuid4()}"}

# Funciones de lógica para la interfaz custom
def user_msg(message, history):
    if not message:
         return "", history
    # Limpia el cuadro de entrada y añade el mensaje del usuario a la historia
    return "", history + [{"role": "user", "content": message}]

def extract_text_from_content(content):
    """Extrae el contenido de texto plano de los diferentes formatos de mensaje de Gradio 6."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, str):
                text_parts.append(item)
            elif isinstance(item, dict):
                text_parts.append(item.get("text", ""))
            elif hasattr(item, "text"):
                text_parts.append(item.text)
        return "".join(text_parts)
    if isinstance(content, dict):
        return content.get("text", "")
    if hasattr(content, "text"):
        return content.text
    return str(content)

async def bot_msg(history, session_state):
    if not history:
        yield history
        return
        
    user_message = extract_text_from_content(history[-1]["content"])
    
    # Prepara el espacio para la respuesta del bot
    history.append({"role": "assistant", "content": ""})
    yield history
    
    # Genera un ID de sesión único si no existe
    if "id_sesion" not in session_state:
        session_state["id_sesion"] = f"soteria_{uuid.uuid4()}"
    session_id = session_state["id_sesion"]
    user_id = "gradio_user"
    
    # Importar el generador de flujo de agentes
    from run_soteria import responder_stream
    
    # Consumir el generador en streaming
    async for chunk in responder_stream(user_message, history[:-1], session_id, user_id):
        # Aplicamos el formateador a cada fragmento acumulado
        formatted_chunk = format_feedback_html(chunk)
        history[-1]["content"] = formatted_chunk
        yield history

# Construir bloque de interfaz principal
with gr.Blocks() as demo:
    session_state = gr.State(value=get_initial_state)
    
    # Encabezado
    gr.HTML("""
    <div class='header-container'>
        <h1 class='header-title'>🛡️ SoterIA 🌱</h1>
        <p class='header-subtitle'>Asistente de Entrenamiento Bilingüe en Primeros Auxilios Psicológicos (PAP)</p>
    </div>
    """)
    
    # Banner de advertencia obligatorio
    gr.HTML("""
    <div class='warning-banner'>
        <p class='warning-text'>
            ⚠️ <strong>Aviso Importante / Important Notice:</strong><br>
            SoterIA es una herramienta educativa y de práctica. No sustituye la atención de un profesional ni los servicios de emergencia. Si tú o alguien más está en riesgo, marca: <strong>Línea de la Vida — 800 911 2000</strong> (gratis, 24 h, México) · <strong>Emergencias — 911</strong>.<br><br>
            SoterIA is an educational and practice tool. It is not a substitute for professional care or emergency services. If you or someone else is at risk, call: <strong>Línea de la Vida — 800 911 2000</strong> (free, 24/7, Mexico) · <strong>Emergencies — 911</strong>, or your local emergency number.
        </p>
    </div>
    """)
    
    # Mensaje de carga inicial (Despertando a SoterIA)
    gr.HTML("""
    <div class='loading-notice'>
        <p class='loading-notice-text'>
            🌱 <strong>Despertando a SoterIA...</strong> esto puede tardar unos 30 segundos la primera vez. Gracias por tu paciencia.<br>
            <strong>Waking SoterIA up...</strong> this may take about 30 seconds the first time. Thanks for your patience.
        </p>
    </div>
    """)
    
    # Diseño de dos columnas
    with gr.Row():
        # Columna Izquierda: Panel de Herramientas PAP (Sidebar)
        with gr.Column(scale=1, min_width=300, elem_classes="sidebar-container"):
            gr.Markdown("### 🎯 Selector de Casos PAP")
            event_type = gr.Dropdown(
                choices=["Desastres", "Accidentes", "Duelo", "Violencia"], 
                value="Desastres", 
                label="Tipo de Evento / Event Type"
            )
            difficulty = gr.Radio(
                choices=["Básico / Basic", "Intermedio / Intermediate", "Avanzado / Advanced"], 
                value="Básico / Basic", 
                label="Dificultad / Difficulty"
            )
            btn_start = gr.Button("Iniciar Práctica / Start Practice", variant="primary")
            
            gr.HTML("<hr style='border: 0; border-top: 1px solid rgba(255,255,255,0.08); margin: 20px 0;'>")
            
            # Widget de Respiración Guiada
            gr.HTML("""
            <div class="breathing-widget">
                <h3 class="widget-title">🧘 Respiración 4x4 / 4x4 Breathing</h3>
                <div class="breathing-circle-container">
                    <div class="breathing-circle"></div>
                    <div class="breathing-text"></div>
                </div>
                <p class="widget-desc">Regula tu ritmo o el del personaje de práctica siguiendo el pulso. / Regulate your breathing following the pulse.</p>
            </div>
            """)
            
            # Guía ABCDE
            with gr.Accordion("Guía Rápida ABCDE / Quick PFA Guide", open=True):
                gr.HTML("""
                <div class="abcde-guide">
                    <div class="abcde-step"><strong>A:</strong> Escucha Activa / Active Listening</div>
                    <div class="abcde-step"><strong>B:</strong> Respiración (4x4) / Breathing</div>
                    <div class="abcde-step"><strong>C:</strong> Categorizar Necesidades / Categorize Needs</div>
                    <div class="abcde-step"><strong>D:</strong> Derivar Redes / Referral</div>
                    <div class="abcde-step"><strong>E:</strong> Psicoeducación / Psychoeducation</div>
                </div>
                """)
        
        # Columna Derecha: Chat Area
        with gr.Column(scale=3, elem_classes="chat-column"):
            with gr.Column(elem_classes="chat-container"):
                chatbot = gr.Chatbot(
                    value=[
                        {
                            "role": "assistant",
                            "content": "Hola / Hi 🤍 Escríbeme en español, in English, o en otra lengua: me adapto a ti. Write to me in Spanish, English, or another language — I'll follow your lead."
                        }
                    ],
                    avatar_images=(None, "bot_avatar.png"),
                )
                
                with gr.Row():
                    textbox = gr.Textbox(
                        placeholder="Escribe tu mensaje aquí... / Type your message here...", 
                        container=False, 
                        scale=7
                    )
                    submit_btn = gr.Button("Enviar / Send", scale=1, variant="secondary")
                
                # Ejemplos (prompts sugeridos)
                examples = gr.Examples(
                    examples=[
                        "¿Qué son los primeros auxilios psicológicos?",
                        "I want to practice a grief case",
                        "¿Cómo apoyo a alguien después de un accidente?",
                        "Practice a case (you choose)",
                        "¿Dónde puedo encontrar ayuda o a quién acudir?"
                    ],
                    inputs=textbox,
                    label="Ejemplos / Examples"
                )
                
                with gr.Accordion("🌱 ¿Cómo funciona SoterIA? / How SoterIA works", open=False):
                    gr.Markdown(
                        "SoterIA opera con un ecosistema multi-agente avanzado / SoterIA operates on an advanced multi-agent ecosystem:\n\n"
                        "- **Arquitectura / Architecture**: Coordinada por el SDK de agentes de Google (**Google ADK**), gestionando de forma invisible agentes especializados (Analista, Enrutador, Especialistas de Repaso, Simulador y Derivación / Chat Analyst, Router, Review/Simulator/Referral Specialists).\n"
                        "- **Modelo Base / LLM**: Impulsado por modelos **Gemini** de Google, garantizando empatía, adaptabilidad bilingüe y barreras de seguridad críticas.\n"
                        "- **Protocolo MCP / MCP Protocol**: Conexión con servidores de contexto (**Model Context Protocol**) para registro de métricas de práctica.\n"
                        "- **Interfaz / UI**: Diseñada en **Gradio**, responsiva, con herramientas de contención (respiración guiada y guía ABCDE)."
                    )

    # Eventos de Envío
    # 1. Enviar mensaje de texto
    submit_event = submit_btn.click(
        fn=user_msg,
        inputs=[textbox, chatbot],
        outputs=[textbox, chatbot],
        queue=False
    ).then(
        fn=bot_msg,
        inputs=[chatbot, session_state],
        outputs=chatbot
    )
    
    textbox.submit(
        fn=user_msg,
        inputs=[textbox, chatbot],
        outputs=[textbox, chatbot],
        queue=False
    ).then(
        fn=bot_msg,
        inputs=[chatbot, session_state],
        outputs=chatbot
    )
    
    # 2. Iniciar práctica desde selector
    def start_practice_msg(event, diff):
        # Normalizamos la dificultad eliminando el texto extra en inglés para el prompt interno
        diff_clean = diff.split("/")[0].strip().lower()
        return f"Quiero practicar un caso de {event} en nivel {diff_clean}"

    btn_start.click(
        fn=start_practice_msg,
        inputs=[event_type, difficulty],
        outputs=textbox,
        queue=False
    ).then(
        fn=user_msg,
        inputs=[textbox, chatbot],
        outputs=[textbox, chatbot],
        queue=False
    ).then(
        fn=bot_msg,
        inputs=[chatbot, session_state],
        outputs=chatbot
    )

if __name__ == "__main__":
    demo.queue().launch(theme=gr.themes.Soft(primary_hue="teal", secondary_hue="slate"), css=css, js=js_func)
