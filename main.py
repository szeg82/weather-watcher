import subprocess
import sys
import time
import os

def run_backend():
    """Elindítja a FastAPI backendet uvicorn-nal."""
    print("Backend indítása...")
    return subprocess.Popen([
        sys.executable, "-m", "uvicorn", "backend.main:app", 
        "--host", "127.0.0.1", "--port", "8000"
    ])

def run_frontend():
    """Elindítja a Streamlit frontendet."""
    print("Frontend indítása...")
    return subprocess.Popen([
        sys.executable, "-m", "streamlit", "run", "frontend/app.py"
    ])

if __name__ == "__main__":
    # Ellenőrizzük, létezik-e a frontend mappa/fájl
    if not os.path.exists("frontend"):
        os.makedirs("frontend")

    backend_process = None
    frontend_process = None

    try:
        backend_process = run_backend()
        time.sleep(2)  # Várunk, hogy a backend elinduljon
        
        frontend_process = run_frontend()

        print("\nA rendszer fut!")
        print("Backend: http://127.0.0.1:8000")
        print("Frontend: http://localhost:8501")
        print("Kilépéshez nyomj CTRL+C-t")

        # Folyamatosan fut, amíg meg nem szakítják
        backend_process.wait()
        frontend_process.wait()

    except KeyboardInterrupt:
        print("\nLeállítás...")
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        print("Rendszer leállítva.")