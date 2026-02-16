import os
import requests
from dotenv import load_dotenv

# Load secret API Key from environment
load_dotenv()
API_KEY = os.getenv("API_KEY")

def main():
    print("--- CheziousBot Secured CLI ---")
    
    username = input("Username: ").strip()
    location = input("Location (optional): ").strip()
    session_id = input("Session ID (optional): ").strip() or None
    
    url = "http://127.0.0.1:8000/chat"
    # Headers now include the required API Key
    headers = {"X-API-Key": API_KEY}

    while True:
        try:
            msg = input(f"\n{username} > ").strip()
            if not msg: continue
            if msg.lower() in ["exit", "quit"]: break
            
            payload = {
                "username": username,
                "message": msg,
                "location": location,
                "session_id": session_id
            }

            print("Bot > ", end="", flush=True)
            
            with requests.post(url, json=payload, headers=headers, stream=True) as r:
                if r.status_code == 403:
                    print("\nSecurity Error: Invalid or missing API Key.")
                    break
                
                if not session_id:
                    session_id = r.headers.get("X-Session-ID")
                    print(f"[Session: {session_id}]")

                for chunk in r.iter_content(chunk_size=None, decode_unicode=True):
                    print(chunk, end="", flush=True)
            print()

        except KeyboardInterrupt: break
        except Exception as e:
            print(f"\nConnection Error: {e}")
            break

if __name__ == "__main__":
    main()
