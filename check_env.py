import os
from dotenv import load_dotenv

def check_environment():
    load_dotenv()
    
    print("🔍 Environment Check")
    print("==================")
    
    required_vars = ['TELEGRAM_BOT_TOKEN', 'GEMINI_API_KEY']
    all_good = True
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * 10}...{value[-4:] if len(value) > 4 else '****'}")
        else:
            print(f"❌ {var}: Not found")
            all_good = False
    
    if all_good:
        print("\n✅ All environment variables are set!")
    else:
        print("\n❌ Missing environment variables!")
        print("Create a .env file with:")
        for var in required_vars:
            if not os.getenv(var):
                print(f"{var}=your_{var.lower()}")
    
    return all_good

if __name__ == "__main__":
    check_environment()
