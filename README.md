---
title: SoterIA
emoji: 🛡️
colorFrom: indigo
colorTo: blue
sdk: gradio
sdk_version: 6.19.0
python_version: "3.11"
app_file: app.py
pinned: false
license: apache-2.0
---

# SoterIA: Simulador de Entrenamiento en Primeros Auxilios Psicológicos (PAP)

SoterIA es una plataforma conversacional inteligente basada en agentes autónomos orquestados, diseñada para entrenar y acompañar a facilitadores y personal de apoyo en la aplicación de **Primeros Auxilios Psicológicos (PAP)**.

> ⚠️ **Aviso de Seguridad:** SoterIA es una herramienta puramente didáctica y de simulación para entrenamiento. **No brinda atención real en crisis psicológicas.** Si tú o alguien que conoces se encuentra en situación de riesgo, por favor comunícate de inmediato a las líneas nacionales de emergencia:
> - **Emergencias:** 911 (si hay riesgo inmediato para la vida)
> - **Línea de la Vida (24 h):** 800 911 2000
> - **SAPTEL:** 55 5259 8121

---

## 🛠️ Arquitectura de Agentes (Google ADK)

SoterIA funciona mediante una red orquestada de agentes autónomos construida con el **Google Agent Development Kit (ADK)**:

1. **Analista de Chats:** Examina cada mensaje entrante para extraer intenciones, temas del modelo PAP y detectar de manera prioritaria posibles señales de crisis real del usuario (barrera de seguridad). Adicionalmente, registra métricas en Google Sheets vía MCP en segundo plano.
2. **Enrutador:** Recibe el análisis del Analista y determina a qué especialista o flujo (Seguridad, Repaso, Simulador, Derivación o Maestro Directo) se debe dirigir la conversación.
3. **Especialistas:**
   - **Repaso:** Resuelve dudas teóricas sobre el modelo PAP (como el protocolo ABCDE).
   - **Simulador:** Simula casos de práctica interactiva y ofrece retroalimentación formativa de desempeño.
   - **Derivación:** Proporciona los números de ayuda e indicaciones de canalización profesional.
4. **Maestro:** La voz unificada de SoterIA. Recibe el material de los especialistas y entrega la respuesta final de forma empática, cuidada y profesional.

---

## 📋 Requisitos y Configuración de Secretos en Hugging Face

Para desplegar esta aplicación en Hugging Face Spaces o ejecutarla de forma headless, debes configurar las siguientes variables de entorno (Secrets):

### 1. Clave de Gemini API
- `GOOGLE_API_KEY`: Tu API Key de Google AI Studio para acceder a los modelos `gemini-2.5-flash`.

### 2. Autenticación de Google Sheets (Métricas)
El servidor MCP de Google Sheets requiere un token de acceso para escribir los logs de métricas en la hoja compartida. SoterIA está programado para intentar autenticarse a través de tres métodos ordenados por prioridad:

#### Opción A: Mediante Archivo JSON de Cuenta de Servicio (Local)
* `SERVICE_ACCOUNT_PATH` o `GOOGLE_APPLICATION_CREDENTIALS`: Ruta local al archivo JSON de tu Service Account de GCP.

#### Opción B: Mediante JSON Completo en Variable (HF Spaces)
* `GOOGLE_SERVICE_ACCOUNT_JSON`: Pega el contenido de texto completo de tu archivo JSON de clave privada de Cuenta de Servicio como el valor de este Secret. El código lo leerá de memoria de manera segura sin guardarlo en disco.

#### Opción C: Mediante OAuth 2.0 Refresh Token (Headless sin Key Creation)
Si las políticas de seguridad de GCP (`iam.disableServiceAccountKeyCreation`) impiden crear llaves JSON de Cuentas de Servicio:
1. Crea un **OAuth 2.0 Client ID** tipo *Desktop* en Google Cloud Console.
2. Realiza el flujo de login inicial de OAuth en tu entorno local para autorizar a la app y extraer el **Refresh Token**.
3. Configura los siguientes 3 Secrets en Hugging Face Spaces:
   * `GOOGLE_CLIENT_ID`: El ID de cliente OAuth.
   * `GOOGLE_CLIENT_SECRET`: El secreto del cliente OAuth.
   * `GOOGLE_REFRESH_TOKEN`: El token de refresco OAuth obtenido.
   
El sistema se encargará de refrescar dinámicamente el token de acceso de manera automatizada y headless.

---

## 💻 Ejecución Local

1. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```
2. Instala e inicializa el entorno de Node.js si no lo tienes (requerido para ejecutar el servidor MCP de Sheets con `npx`):
   ```bash
   npm install -g google-sheets-mcp
   ```
3. Crea un archivo `.env` en la raíz del proyecto y configura tus variables de entorno locales (API keys y credenciales de Google).
4. Ejecuta la versión CLI interactiva en consola:
   ```bash
   python run_soteria.py
   ```
5. Ejecuta la interfaz de chat web de Gradio localmente:
   ```bash
   python app.py
   ```
