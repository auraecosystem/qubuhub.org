import subprocess
import sys
import time
import os
import signal

# Define services to launch concurrently
SERVICES = [
    {
        "name": "Aura FastAPI Backend",
        "cmd": [sys.executable, "-m", "uvicorn", "aura.api:app", "--reload", "--port", "8000"],
        "cwd": "."
    },
    {
        "name": "QubuHub Web Frontend (qubuhub.org)",
        "cmd": ["npm", "run", "dev"],
        "cwd": "./hub"
    }
]

processes = []

def signal_handler(sig, frame):
    print("\n[AURA-ORCHESTRATOR] Shutting down all services...")
    for p in processes:
        if p.poll() is None:
            p.terminate()
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

def main():
    print("==================================================")
    print("🚀 Starting Aura Ecosystem Master Orchestrator")
    print("==================================================")

    # Ensure dependencies for hub are installed if node_modules missing
    hub_path = os.path.join(".", "hub")
    if os.path.exists(hub_path) and not os.path.exists(os.path.join(hub_path, "node_modules")):
        print("[AURA-ORCHESTRATOR] Installing frontend dependencies for qubuhub.org...")
        subprocess.run(["npm", "install"], cwd=hub_path, shell=True)

    # Launch services
    for service in SERVICES:
        print(f"[AURA-ORCHESTRATOR] Launching {service['name']}...")
        p = subprocess.Popen(
            service["cmd"],
            cwd=service["cwd"],
            shell=True
        )
        processes.append(p)
        time.sleep(1) # Stagger startup slightly

    print("\n[AURA-ORCHESTRATOR] All services running. Press Ctrl+C to stop.\n")
    
    # Keep orchestrator alive and monitor processes
    while True:
        time.sleep(1)
        for p in processes:
            if p.poll() is not None:
                print(f"[AURA-ORCHESTRATOR] Warning: A service process exited unexpectedly.")

if __name__ == "__main__":
    main()
