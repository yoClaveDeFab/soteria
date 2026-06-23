import os
import sys
from google_auth_oauthlib.flow import InstalledAppFlow

# Scopes exactos definidos en analista_chats/agent.py
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

def main():
    print("==================================================================")
    print("        Generador de OAuth 2.0 Refresh Token para SoterIA")
    print("==================================================================")
    
    # 1. Solicitar credenciales del usuario
    client_id = input("1. Introduce tu GOOGLE_CLIENT_ID: ").strip()
    client_secret = input("2. Introduce tu GOOGLE_CLIENT_SECRET: ").strip()

    if not client_id or not client_secret:
        print("\n[Error]: El Client ID y el Client Secret son obligatorios.")
        return

    # Construir configuración estructurada de OAuth
    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs"
        }
    }

    print("\nIniciando flujo de autenticación local...")
    print("Se abrirá una pestaña en tu navegador web predeterminado.")
    print("Inicia sesión con la cuenta de Google que tiene acceso a la hoja.")
    print("Si aparece una advertencia de 'Google has not verified this app', haz clic en 'Advanced' y luego en 'Go to... (unsafe)' para continuar.")
    
    try:
        # Inicializar el flujo local en un puerto disponible
        flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
        creds = flow.run_local_server(port=0)

        print("\n==================================================================")
        print("                     ¡AUTENTICACIÓN EXITOSA!")
        print("==================================================================")
        print("Guarda exactamente estas tres variables de entorno:")
        print(f"GOOGLE_CLIENT_ID={client_id}")
        print(f"GOOGLE_CLIENT_SECRET={client_secret}")
        print(f"GOOGLE_REFRESH_TOKEN={creds.refresh_token}")
        print("==================================================================")
        print("\nNota: Una vez anotados estos valores, puedes eliminar este script.")
        
    except Exception as e:
        print(f"\n[Error durante el flujo]: {e}")

if __name__ == "__main__":
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    main()
