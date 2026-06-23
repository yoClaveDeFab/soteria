# SoterIA — Integración MCP: Métricas y Observabilidad
# SoterIA — MCP Integration: Metrics & Observability
### 5º concepto del Capstone: MCP Server (+ observabilidad) / 5th Capstone concept

> Idioma operativo: español. / Operative language: Spanish.
> El Analista registra cada interacción en una Google Sheet a través de un MCP de Google Sheets.
> The Analyst logs each interaction to a Google Sheet via a Google Sheets MCP.

---

## Qué hace / What it does
- **ES:** Además de su salida JSON, el Analista llama a una herramienta MCP que **agrega una fila** a la hoja `SoterIA_Metricas` con los metadatos de cada interacción. Esto demuestra **MCP Server + observabilidad**.
- **EN:** In addition to its JSON output, the Analyst calls an MCP tool that **appends a row** to the `SoterIA_Metricas` sheet with each interaction's metadata. This demonstrates **MCP Server + observability**.

## Hoja de métricas / Metrics sheet
- Archivo / File: **SoterIA_Metricas** (Google Sheets, en la carpeta PAP).
- ID de la hoja / Sheet ID: `1o4ERfUvjSYbAhdb_V4tJRp7OIj5b_Tg72fme5LK-JIs`
- Columnas / Columns:
  `marca_temporal, intencion, etapa, tema_pap, perfil_caso, nivel_caso, seguridad_activada, tipo_consulta, funcion_sugerida`

## 🔒 Salvaguarda de privacidad (CRÍTICA) / Privacy safeguard (CRITICAL)
- **ES:** Solo se registran **metadatos no identificables** de la práctica (intención, etapa, nivel, si se activó seguridad). NUNCA se guardan datos personales del usuario, ni transcripciones, ni el contenido textual de un mensaje de crisis. Esto protege a la persona y es coherente con el cuidado ético de SoterIA.
- **EN:** Only **non-identifying metadata** is logged (intent, stage, level, whether safety was triggered). NEVER store the user's personal data, transcripts, or the text of a crisis message. This protects the person and is consistent with SoterIA's ethical care.

---

## Fragmento para AGREGAR al prompt del Analista / Snippet to ADD to the Analyst prompt

### Español (operativo)
```
REGISTRO DE MÉTRICAS (MCP)
Después de analizar el mensaje, además del JSON, registra una fila en la hoja de métricas usando
la herramienta MCP de Google Sheets (append_row) con: marca_temporal (ISO), intencion, etapa,
tema_pap, perfil_caso, nivel_caso, seguridad_activada, tipo_consulta, funcion_sugerida.
NUNCA registres datos personales, transcripciones ni el texto del mensaje. Solo metadatos.
Si el registro falla, continúa normalmente (el registro no debe bloquear la respuesta al usuario).
```

### English (reference)
```
METRICS LOGGING (MCP)
After analyzing the message, in addition to the JSON, append a row to the metrics sheet using the
Google Sheets MCP tool (append_row) with: marca_temporal (ISO), intencion, etapa, tema_pap,
perfil_caso, nivel_caso, seguridad_activada, tipo_consulta, funcion_sugerida.
NEVER log personal data, transcripts, or the message text. Metadata only.
If logging fails, continue normally (logging must not block the user's response).
```

---

## Cómo se conecta en Antigravity / ADK — How to wire it
1. **ES:** Configurar el servidor MCP de Google Sheets en el proyecto (según la documentación de ADK/Antigravity).
   **EN:** Configure the Google Sheets MCP server in the project (per ADK/Antigravity docs).
2. Dar de alta el **ID de la hoja** (arriba) y exponer la herramienta `append_row` al Analista.
   Register the **sheet ID** (above) and expose the `append_row` tool to the Analyst.
3. 🔑 Credenciales/keys **por variable de entorno**, nunca en el código (regla del Capstone).
   Credentials/keys **via environment variable**, never in code (Capstone rule).
4. Probar: hacer una consulta y verificar que aparece una fila nueva en la hoja.
   Test: run a query and confirm a new row appears in the sheet.

## Conceptos del Capstone que esto añade / Capstone concepts this adds
- MCP Server ✅ · Observabilidad/Deployability ✅ → SoterIA pasa de 4 a **5–6 conceptos**.
