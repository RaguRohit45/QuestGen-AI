import google.generativeai as genai

GEMINI_API_KEY = "AIzaSyDmBlXPzju0WiGNUFbSVh3Rvh9Woc1GvbA"
genai.configure(api_key=GEMINI_API_KEY)

print("Listing available models...")
try:
    models = genai.list_models()
    print("\nAvailable models with generateContent support:")
    for model in models:
        if 'generateContent' in model.supported_generation_methods:
            print(f"  - {model.name}")
            print(f"    Display name: {model.display_name}")
            print()
except Exception as e:
    print(f"Error listing models: {e}")

test_models = [
    'gemini-1.5-flash',
    'gemini-1.5-pro',
    'gemini-pro',
    'models/gemini-1.5-flash',
    'models/gemini-1.5-pro'
]

print("\nTesting models...")
for model_name in test_models:
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Say hello")
        print(f"✓ {model_name} - Works! Response: {response.text[:50]}")
        break
    except Exception as e:
        print(f"✗ {model_name} - Failed: {str(e)[:100]}")

