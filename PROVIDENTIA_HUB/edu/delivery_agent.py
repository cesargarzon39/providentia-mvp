import os
import time
from datetime import datetime

# Simulación de base de datos (En el futuro será Notion API)
PACIENTES = [
    {"nombre": "Paciente Demo", "celular": "+57XXXXXXXXXX", "dia": 0, "patologia": "Fractura"}
]

def send_video(paciente):
    dia = paciente['dia']
    # Lógica de selección de video según el día
    curriculum_map = {
        0: "00_bienvenida.md",
        1: "01_dia1_herida.md",
        3: "03_dia3_movilidad.md",
        7: "07_dia7_alarmas.md"
    }
    
    if dia in curriculum_map:
        archivo = curriculum_map[dia]
        print(f"🚀 Enviando {archivo} a {paciente['nombre']} ({paciente['celular']})...")
        # Aquí se integrará el comando: openclaw message send --target paciente['celular'] --message content
    else:
        print(f"⏳ No hay contenido programado para el día {dia} para {paciente['nombre']}.")

def main():
    print(f"--- PROVIDENTIA DELIVERY AGENT v1.0 ---")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    for p in PACIENTES:
        send_video(p)

if __name__ == "__main__":
    main()
