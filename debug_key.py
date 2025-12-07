import os
from dotenv import load_dotenv

# Print where we are looking
print(f"Current Working Directory: {os.getcwd()}")

# Try loading
load_dotenv()
key = os.getenv("GOOGLE_API_KEY")

if key:
    print(f"✅ SUCCESS: Found Key starting with {key[:4]}...")
else:
    print("❌ ERROR: Key is None. Checking directory for .env file...")
    if os.path.exists(".env"):
        print("   Found .env file. Printing content (first 5 chars):")
        with open(".env", "r") as f:
            print(f"   {f.read(5)}...")
    else:
        print("   CRITICAL: .env file does NOT exist in this folder.")
