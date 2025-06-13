#!/usr/bin/env python3
"""
Startup script for Enhanced Cross-Mind Consensus System
Provides easy configuration and deployment options
"""

import argparse
import signal
import subprocess
import sys
import time
from pathlib import Path


def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        "fastapi",
        "uvicorn",
        "openai",
        "requests",
        "pydantic",
        "scikit-learn",
        "sentence-transformers",
        "streamlit",
        "plotly",
        "pandas",
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing_packages.append(package)

    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("Install them with: pip install -r requirements.txt")
        return False

    print("✅ All required dependencies are installed")
    return True


def check_configuration():
    """Check if configuration files exist"""
    config_files = ["config.py", "env.template"]
    missing_files = []

    for file in config_files:
        if not Path(file).exists():
            missing_files.append(file)

    if missing_files:
        print(f"❌ Missing configuration files: {', '.join(missing_files)}")
        return False

    # Check if .env file exists
    if not Path(".env").exists():
        print(
            "⚠️  .env file not found. Copy env.template to .env and configure your API keys"
        )
        choice = input("Continue anyway? (y/N): ")
        if choice.lower() != "y":
            return False

    print("✅ Configuration files found")
    return True


def setup_directories():
    """Create necessary directories"""
    directories = ["logs", "backend/__pycache__"]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

    print("✅ Directory structure created")


def run_api_server(host="0.0.0.0", port=8000, reload=True):
    """Run the FastAPI server"""
    print(f"🚀 Starting API server on {host}:{port}")

    try:
        cmd = [
            sys.executable,
            "-m",
            "uvicorn",
            "backend.main:app",
            "--host",
            host,
            "--port",
            str(port),
        ]

        if reload:
            cmd.append("--reload")

        process = subprocess.Popen(cmd)
        return process
    except Exception as e:
        print(f"❌ Failed to start API server: {e}")
        return None


def run_dashboard(port=8501):
    """Run the Streamlit dashboard"""
    print(f"📊 Starting dashboard on port {port}")

    try:
        cmd = [
            sys.executable,
            "-m",
            "streamlit",
            "run",
            "streamlit_dashboard.py",
            "--server.port",
            str(port),
            "--server.address",
            "0.0.0.0",
        ]

        process = subprocess.Popen(cmd)
        return process
    except Exception as e:
        print(f"❌ Failed to start dashboard: {e}")
        return None


def run_tests():
    """Run the test suite"""
    print("🧪 Running test suite...")

    try:
        result = subprocess.run(
            [sys.executable, "test_system.py"], capture_output=True, text=True
        )
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)

        return result.returncode == 0
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Enhanced Cross-Mind Consensus System")
    parser.add_argument(
        "--mode",
        choices=["api", "dashboard", "both", "test"],
        default="both",
        help="What to run",
    )
    parser.add_argument("--api-host", default="0.0.0.0", help="API server host")
    parser.add_argument("--api-port", type=int, default=8000, help="API server port")
    parser.add_argument(
        "--dashboard-port", type=int, default=8501, help="Dashboard port"
    )
    parser.add_argument("--no-reload", action="store_true", help="Disable auto-reload")
    parser.add_argument(
        "--skip-checks", action="store_true", help="Skip dependency checks"
    )

    args = parser.parse_args()

    # ASCII Art Banner
    print(
        """
    ╔══════════════════════════════════════════════════════════════╗
    ║             🧠 Cross-Mind Consensus System v2.0              ║
    ║                Advanced Multi-LLM Platform                   ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    )

    # Pre-flight checks
    if not args.skip_checks:
        print("🔍 Running pre-flight checks...")

        if not check_dependencies():
            sys.exit(1)

        if not check_configuration():
            sys.exit(1)

    setup_directories()

    processes = []

    try:
        if args.mode == "test":
            success = run_tests()
            sys.exit(0 if success else 1)

        elif args.mode == "api":
            process = run_api_server(args.api_host, args.api_port, not args.no_reload)
            if process:
                processes.append(process)

        elif args.mode == "dashboard":
            process = run_dashboard(args.dashboard_port)
            if process:
                processes.append(process)

        elif args.mode == "both":
            # Start API server
            api_process = run_api_server(
                args.api_host, args.api_port, not args.no_reload
            )
            if api_process:
                processes.append(api_process)

            # Wait a bit for API to start
            time.sleep(3)

            # Start dashboard
            dashboard_process = run_dashboard(args.dashboard_port)
            if dashboard_process:
                processes.append(dashboard_process)

        if not processes:
            print("❌ No processes started successfully")
            sys.exit(1)

        print(f"\n✅ Started {len(processes)} process(es)")
        print("\n📋 Access Points:")

        if args.mode in ["api", "both"]:
            print(f"   🔗 API Server: http://{args.api_host}:{args.api_port}")
            print(f"   📚 API Docs: http://{args.api_host}:{args.api_port}/docs")

        if args.mode in ["dashboard", "both"]:
            print(f"   📊 Dashboard: http://localhost:{args.dashboard_port}")

        print("\n💡 Tips:")
        print("   - Use Ctrl+C to stop all services")
        print("   - Check logs directory for detailed logs")
        print("   - Configure .env file for API keys")

        # Wait for processes
        def signal_handler(sig, frame):
            print("\n🛑 Shutting down...")
            for process in processes:
                process.terminate()
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)

        # Keep running until interrupted
        for process in processes:
            process.wait()

    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        for process in processes:
            process.terminate()

    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        for process in processes:
            process.terminate()
        sys.exit(1)


if __name__ == "__main__":
    main()
