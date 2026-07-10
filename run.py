#!/usr/bin/env python
import argparse
import subprocess
import sys
import time
import os

if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

def parse_args():
    parser = argparse.ArgumentParser(description="Ops Brain Local Launcher")
    parser.add_argument("--ui", action="store_true", help="Launch Streamlit UI only")
    parser.add_argument("--api", action="store_true", help="Launch FastAPI API only")
    parser.add_argument("--demo", action="store_true", help="Load seed data and run both UI + API")
    return parser.parse_args()

def start_api():
    print("🚀 Starting FastAPI backend on http://127.0.0.1:8000...")
    # Launch uvicorn as subprocess
    env = os.environ.copy()
    return subprocess.Popen([
        sys.executable, "-m", "uvicorn", "api.app:app",
        "--host", "0.0.0.0", "--port", "8000", "--reload"
    ], env=env)

def start_ui():
    print("🌐 Starting Streamlit UI on http://localhost:8501...")
    env = os.environ.copy()
    return subprocess.Popen([
        sys.executable, "-m", "streamlit", "run", "ui/app.py"
    ], env=env)

def run_seed():
    print("🌱 Seeding initial asset databases, work orders, and regulations...")
    try:
        subprocess.run([sys.executable, "scripts/seed.py"], check=True)
        print("✅ Seeding completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Seeding failed: {e}")
        sys.exit(1)

def main():
    args = parse_args()
    
    # Default: both UI and API if no flags or demo is selected
    run_api_flag = args.api or (not args.ui)
    run_ui_flag = args.ui or (not args.api)
    
    if args.demo:
        run_seed()
        run_api_flag = True
        run_ui_flag = True
        
    processes = []
    try:
        if run_api_flag:
            api_proc = start_api()
            processes.append(api_proc)
            
            # Wait for API backend to be online before opening Streamlit UI
            print("⏳ Waiting for API backend to initialize and bind to port 8000...")
            import urllib.request
            api_ready = False
            for _ in range(30):
                try:
                    with urllib.request.urlopen("http://127.0.0.1:8000/api/v1/health", timeout=1.0) as resp:
                        if resp.status == 200:
                            api_ready = True
                            break
                except Exception:
                    time.sleep(1)
            if api_ready:
                print("✅ API backend is online and ready!")
            else:
                print("⚠️ API backend took longer than expected to respond, launching UI anyway...")
            
        if run_ui_flag:
            ui_proc = start_ui()
            processes.append(ui_proc)
            
        # Keep launcher alive
        while True:
            for proc in processes:
                if proc.poll() is not None:
                    # One of the processes crashed or ended
                    print(f"⚠️ Subprocess {proc.args} exited with code {proc.returncode}")
                    return
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n👋 Stopping Ops Brain Local services...")
        for proc in processes:
            proc.terminate()
            proc.wait()
        print("Done.")

if __name__ == "__main__":
    main()
