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
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

/* Color Variables and Theme Overrides */
:root, .gradio-container {
    --font: 'Plus Jakarta Sans', sans-serif !important;
    --body-background-fill: radial-gradient(circle at 50% 0%, #0d0e1c 0%, #030408 100%) !important;
    --background-fill-primary: rgba(13, 16, 29, 0.45) !important;
    --background-fill-secondary: rgba(18, 22, 41, 0.3) !important;
    --border-color-primary: rgba(45, 212, 191, 0.15) !important;
    --border-color-secondary: rgba(255, 255, 255, 0.04) !important;
    --text-color-primary: #f8fafc !important;
    --text-color-secondary: #94a3b8 !important;
    
    --input-background-fill: rgba(8, 10, 19, 0.6) !important;
    --input-border-width: 1px !important;
    --input-border-color: rgba(45, 212, 191, 0.15) !important;
    --input-border-color-focus: rgba(45, 212, 191, 0.6) !important;
    
    --button-primary-background-fill: linear-gradient(135deg, #14b8a6 0%, #0891b2 100%) !important;
    --button-primary-background-fill-hover: linear-gradient(135deg, #0d9488 0%, #06b6d4 100%) !important;
    --button-primary-text-color: #ffffff !important;
    --button-secondary-background-fill: rgba(30, 41, 59, 0.5) !important;
    --button-secondary-background-fill-hover: rgba(30, 41, 59, 0.8) !important;
    --button-secondary-text-color: #f8fafc !important;
    
    --radius-xl: 24px !important;
    --radius-lg: 16px !important;
    --radius-md: 12px !important;
}

body, html, .gradio-container {
    background: radial-gradient(circle at 50% 0%, #0d0e1c 0%, #030408 100%) !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

.gradio-container {
    max-width: 1100px !important;
    margin: 0 auto !important;
    padding: clamp(10px, 3vw, 30px) !important;
}

/* Custom Scrollbars */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: rgba(15, 23, 42, 0.1);
}
::-webkit-scrollbar-thumb {
    background: rgba(45, 212, 191, 0.2);
    border-radius: 4px;
}
::-webkit-scrollbar-thumb:hover {
    background: rgba(45, 212, 191, 0.4);
}

/* Header styling */
.header-container {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 20px;
    margin-bottom: 25px;
    animation: fadeIn 1.2s ease-in-out;
    padding: 20px;
    background: rgba(13, 16, 29, 0.4);
    border: 1px solid rgba(45, 212, 191, 0.15);
    border-radius: 24px;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
}
.header-logo {
    width: 64px;
    height: 64px;
    border-radius: 50%;
    border: 2px solid #2dd4bf;
    box-shadow: 0 0 15px rgba(45, 212, 191, 0.4);
    object-fit: cover;
}
.header-title {
    font-size: clamp(1.8rem, 6vw, 2.8rem);
    font-weight: 800;
    background: linear-gradient(135deg, #99f6e4 0%, #2dd4bf 50%, #06b6d4 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0 0 4px 0;
    letter-spacing: -0.04em;
    display: flex;
    align-items: center;
    gap: 8px;
}
.header-subtitle {
    font-size: clamp(0.85rem, 2.5vw, 1.05rem);
    color: #94a3b8;
    font-weight: 400;
    margin: 0;
}

/* Warning Banner & Safety Warnings */
.warning-banner {
    background: rgba(239, 68, 68, 0.05) !important;
    border: 1px solid rgba(239, 68, 68, 0.18) !important;
    border-left: 4px solid #ef4444 !important;
    border-radius: 16px !important;
    padding: clamp(12px, 3vw, 18px) clamp(16px, 4vw, 24px) !important;
    margin-bottom: 25px !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    animation: slideDown 0.8s cubic-bezier(0.16, 1, 0.3, 1);
}
.warning-text {
    color: #fca5a5 !important;
    font-size: clamp(0.8rem, 2.2vw, 0.9rem);
    font-weight: 500;
    line-height: 1.6;
    margin: 0 !important;
}

/* Loading notice during system wakeup */
.loading-notice {
    background: linear-gradient(135deg, rgba(20, 184, 166, 0.05) 0%, rgba(6, 182, 212, 0.05) 100%) !important;
    border: 1px solid rgba(20, 184, 166, 0.2) !important;
    border-radius: 16px !important;
    padding: 14px 20px !important;
    margin-bottom: 20px !important;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3) !important;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    animation: glowPulse 3s infinite ease-in-out;
}
.loading-notice-text {
    color: #99f6e4 !important;
    font-size: clamp(0.8rem, 2.5vw, 0.9rem);
    font-weight: 500;
    line-height: 1.5;
    text-align: center;
    margin: 0 !important;
}
@keyframes glowPulse {
    0%, 100% { border-color: rgba(20, 184, 166, 0.15); box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3); }
    50% { border-color: rgba(20, 184, 166, 0.4); box-shadow: 0 8px 32px 0 rgba(20, 184, 166, 0.1); }
}

/* Sidebar & Containers */
.sidebar-container {
    background: rgba(13, 16, 29, 0.5) !important;
    border: 1px solid rgba(45, 212, 191, 0.15) !important;
    border-radius: 24px !important;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.45) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    padding: 24px !important;
    margin-bottom: 20px !important;
    animation: fadeInUp 1s cubic-bezier(0.16, 1, 0.3, 1);
}
.sidebar-container h3, .sidebar-container h2 {
    color: #2dd4bf !important;
    font-size: 1.15rem !important;
    font-weight: 700 !important;
    margin: 0 0 16px 0 !important;
    letter-spacing: -0.01em !important;
}
.chat-column {
    margin-bottom: 20px !important;
}
.chat-container {
    background: rgba(13, 16, 29, 0.5) !important;
    border: 1px solid rgba(45, 212, 191, 0.15) !important;
    border-radius: 24px !important;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.45) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    padding: 20px !important;
    animation: fadeInUp 1s cubic-bezier(0.16, 1, 0.3, 1);
}

/* Form controls overrides */
.gradio-container select, .gradio-container textarea, .gradio-container input[type="text"] {
    background: rgba(8, 10, 19, 0.6) !important;
    border: 1px solid rgba(45, 212, 191, 0.15) !important;
    color: #f8fafc !important;
    border-radius: 12px !important;
    padding: 10px 14px !important;
    transition: all 0.3s ease !important;
}
.gradio-container select:focus, .gradio-container textarea:focus, .gradio-container input[type="text"]:focus {
    border-color: rgba(45, 212, 191, 0.6) !important;
    box-shadow: 0 0 10px rgba(45, 212, 191, 0.2) !important;
}

/* Button Upgrades */
.gradio-container button.primary {
    background: linear-gradient(135deg, #14b8a6 0%, #0891b2 100%) !important;
    border: none !important;
    box-shadow: 0 4px 15px rgba(20, 184, 166, 0.25) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}
.gradio-container button.primary:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 6px 20px rgba(20, 184, 166, 0.45), 0 0 8px rgba(45, 212, 191, 0.2) !important;
}
.gradio-container button.secondary {
    background: rgba(30, 41, 59, 0.45) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    transition: all 0.3s ease !important;
}
.gradio-container button.secondary:hover {
    background: rgba(30, 41, 59, 0.8) !important;
    border-color: rgba(45, 212, 191, 0.4) !important;
    transform: translateY(-1px) !important;
}

/* Chatbot Styles */
.chatbot .message {
    border-radius: 18px !important;
    padding: 14px 18px !important;
    font-size: 0.95rem !important;
    line-height: 1.6 !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15) !important;
    backdrop-filter: blur(8px) !important;
    -webkit-backdrop-filter: blur(8px) !important;
}
.chatbot .message.user, .chatbot [data-testid="user"] {
    background: rgba(45, 212, 191, 0.08) !important;
    border-color: rgba(45, 212, 191, 0.25) !important;
    color: #ffffff !important;
    border-bottom-right-radius: 4px !important;
}
.chatbot .message.assistant, .chatbot .message.bot, .chatbot [data-testid="bot"] {
    background: rgba(13, 16, 29, 0.7) !important;
    border-color: rgba(45, 212, 191, 0.15) !important;
    color: #f8fafc !important;
    border-bottom-left-radius: 4px !important;
}
.chatbot .avatar-container {
    border: 2px solid rgba(45, 212, 191, 0.3) !important;
    box-shadow: 0 0 10px rgba(45, 212, 191, 0.2) !important;
    border-radius: 50% !important;
    overflow: hidden !important;
}

/* Breathing Widget Upgrade */
.breathing-widget {
    text-align: center;
    padding: 20px 15px;
    background: rgba(20, 184, 166, 0.03);
    border-radius: 20px;
    border: 1px solid rgba(20, 184, 166, 0.15);
    margin-bottom: 20px;
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}
.widget-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #2dd4bf;
    margin: 0 0 15px 0;
}
.breathing-circle-container {
    position: relative;
    width: 120px;
    height: 120px;
    margin: 0 auto 15px auto;
    display: flex;
    align-items: center;
    justify-content: center;
}
.breathing-circle {
    width: 60px;
    height: 60px;
    background: radial-gradient(circle, #2dd4bf 0%, #0d9488 100%);
    border-radius: 50%;
    box-shadow: 0 0 20px rgba(45, 212, 191, 0.4);
    animation: breathe4x4 16s infinite ease-in-out;
    position: relative;
}
.breathing-circle::after {
    content: '';
    position: absolute;
    top: -10px; left: -10px; right: -10px; bottom: -10px;
    border-radius: 50%;
    border: 2px solid rgba(45, 212, 191, 0.2);
    animation: auraPulse 16s infinite ease-in-out;
    pointer-events: none;
}
.breathing-text {
    position: absolute;
    font-size: 0.8rem;
    font-weight: 700;
    color: #ffffff;
    pointer-events: none;
    text-shadow: 0 1px 3px rgba(0,0,0,0.6);
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    width: 90px;
    z-index: 10;
}
.breathing-text::after {
    content: "Inhala / Inhale";
    animation: breatheWords 16s infinite ease-in-out;
}
.widget-desc {
    font-size: 0.75rem;
    color: #94a3b8;
    line-height: 1.4;
    margin: 0;
}

@keyframes breathe4x4 {
    0%, 100% { transform: scale(1); box-shadow: 0 0 10px rgba(45, 212, 191, 0.3); }
    25% { transform: scale(1.6); box-shadow: 0 0 25px rgba(45, 212, 191, 0.7); } /* Inhale 4s */
    50% { transform: scale(1.6); box-shadow: 0 0 25px rgba(45, 212, 191, 0.7); } /* Hold 4s */
    75% { transform: scale(1); box-shadow: 0 0 10px rgba(45, 212, 191, 0.3); }   /* Exhale 4s */
}
@keyframes auraPulse {
    0%, 100% { transform: scale(1); opacity: 0.3; }
    25% { transform: scale(1.4); opacity: 0.8; border-color: rgba(6, 182, 212, 0.4); } /* Inhale */
    50% { transform: scale(1.4); opacity: 0.8; } /* Hold */
    75% { transform: scale(1); opacity: 0.3; }  /* Exhale */
}
@keyframes breatheWords {
    0%, 24.9% { content: "Inhala / Inhale"; }
    25%, 49.9% { content: "Retén / Hold"; }
    50%, 74.9% { content: "Exhala / Exhale"; }
    75%, 100% { content: "Retén / Hold"; }
}

/* Accordion Custom Styling */
.gradio-container .accordion {
    background: rgba(15, 23, 42, 0.2) !important;
    border: 1px solid rgba(45, 212, 191, 0.1) !important;
    border-radius: 16px !important;
    overflow: hidden !important;
    margin-bottom: 12px !important;
}

/* ABCDE Guide */
.abcde-guide {
    padding: 12px;
    background: rgba(255, 255, 255, 0.01);
    border-radius: 12px;
}
.abcde-step {
    font-size: 0.8rem;
    color: #e2e8f0;
    margin-bottom: 8px;
    line-height: 1.4;
}
.abcde-step:last-child {
    margin-bottom: 0;
}
.abcde-step strong {
    color: #2dd4bf;
    font-weight: 700;
}

/* Feedback Cards & Dashboard */
.feedback-dashboard {
    display: flex;
    flex-direction: column;
    gap: 15px;
    margin-top: 10px;
    text-align: left;
}
.feedback-card {
    border-radius: 16px !important;
    padding: 18px !important;
    border: 1px solid rgba(255, 255, 255, 0.05) !important;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3) !important;
    backdrop-filter: blur(12px) !important;
    -webkit-backdrop-filter: blur(12px) !important;
    transition: all 0.3s ease !important;
}
.feedback-card:hover {
    transform: translateY(-2px) !important;
}
.fortalezas-card {
    background: rgba(16, 185, 129, 0.04) !important;
    border-left: 4px solid #10b981 !important;
}
.fortalezas-card h4 {
    color: #34d399 !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    margin: 0 0 8px 0 !important;
}
.mejoras-card {
    background: rgba(245, 158, 11, 0.04) !important;
    border-left: 4px solid #f59e0b !important;
}
.mejoras-card h4 {
    color: #fbbf24 !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    margin: 0 0 8px 0 !important;
}
.seguridad-card {
    background: rgba(239, 68, 68, 0.04) !important;
    border-left: 4px solid #ef4444 !important;
}
.seguridad-card h4 {
    color: #fca5a5 !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    margin: 0 0 8px 0 !important;
}
.principio-card, .consejo-card {
    background: rgba(6, 182, 212, 0.04) !important;
    border-left: 4px solid #06b6d4 !important;
}
.principio-card h4, .consejo-card h4 {
    color: #2dd4bf !important;
    font-size: 1.05rem !important;
    font-weight: 700 !important;
    margin: 0 0 8px 0 !important;
}

/* Animations */
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}
@keyframes slideDown {
    from { transform: translateY(-15px); opacity: 0; }
    to { transform: translateY(0); opacity: 1; }
}
@keyframes fadeInUp {
    from { transform: translateY(20px); opacity: 0; }
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
        <img src='/file=bot_avatar.png' class='header-logo' alt='SoterIA Logo'>
        <div>
            <h1 class='header-title'>SoterIA</h1>
            <p class='header-subtitle'>Asistente de Entrenamiento Bilingüe en Primeros Auxilios Psicológicos (PAP)</p>
        </div>
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
