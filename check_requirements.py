import sys
import subprocess

required_packages = [
    'python-telegram-bot>=20.0',
    'asyncio',
    'pytz'
]

def check_packages():
    for package in required_packages:
        try:
            __import__(package.split('>=')[0].replace('-', '_'))
            print(f"✅ {package} - OK")
        except ImportError:
            print(f"❌ {package} - MISSING")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
                print(f"✅ {package} - INSTALLED")
            except subprocess.CalledProcessError:
                print(f"❌ Failed to install {package}")

if __name__ == "__main__":
    check_packages()
