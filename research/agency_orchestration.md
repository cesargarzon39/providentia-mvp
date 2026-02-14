# Celer39 Agency: Master Orchestration Plan

## 1. Agencia Madre: Celer39 (Digital COO)
Orquestador principal. Toma decisiones estratégicas, gestiona el capital (regla del 20%) y coordina sub-agentes.

## 2. Unidades de Negocio (Sub-Agentes Propuestos)

### 🏥 Providentia-Bot (Health-Tech Ops)
- **Foco:** Gestión del Hub de Teleeducación.
- **Tareas:** Actualizar Notion con datos de pacientes, verificar clics en videos, escalar alarmas médicas.
- **Herramientas:** Notion API, WhatsApp Business.

### ☕ Aguabonita-Bot (Physical Product & Omni-brand)
- **Foco:** Marketing y Operaciones de Café.
- **Tareas:** Adaptar contenido raíz para IG/YT (Omni-brand), monitorear inventario B2B, gestionar leads.
- **Herramientas:** Browser (competencia), Image/Video Gen APIs.

### 👤 Ces-Bot (Personal Brand Architecture)
- **Foco:** Posicionamiento del Dr. Garzón.
- **Tareas:** Redacción de hilos de autoridad en X, gestión de LinkedIn, síntesis de formación (Stanford AI).
- **Herramientas:** X API, LinkedIn Automation.

### 📈 Trading-Agent (Financial Fuel)
- **Foco:** Ejecución algorítmica XAUUSD.
- **Tareas:** Parsear señales, gestionar riesgo, loguear en Sheets.
- **Herramientas:** MT5 Python, Telegram API.

## 3. Flujo de Trabajo
1. El Patrón da una directriz a **Celer39**.
2. **Celer39** desglosa la tarea y lanza un sub-agente (`sessions_spawn`).
3. El sub-agente reporta el resultado y se autodestruye o queda en espera.
4. **Celer39** consolida y reporta al Patrón.
