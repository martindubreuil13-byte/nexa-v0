import os
import json
from sqlmodel import Session, select, create_engine
from dotenv import load_dotenv # CRITICAL FIX
from models import Expert, engine
import google.generativeai as genai

# 1. Force load the .env file
load_dotenv()

# DEBUG: API Key Check
print(f"DEBUG: API Key loaded? {bool(os.environ.get('GOOGLE_API_KEY'))}")

def find_best_matches(sme_text: str):
    """ Hybrid Matcher: Uses Gemini if Key exists, otherwise falls back to keyword matching. """
    with Session(engine) as session:
        experts = session.exec(select(Expert)).all()

    if not experts:
        return []

    # DEBUG: Prove we are talking to the DB
    print(f"DEBUG: Found {len(experts)} experts in DB: {[e.name for e in experts]}")
    
    api_key = os.environ.get("GOOGLE_API_KEY")

    # --- PATH A: SMART MATCHING (If Key Exists) ---
    if api_key:
        try:
            genai.configure(api_key=api_key)
            # Auto-discover a valid model
            available_models = []
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    available_models.append(m.name)
            # Prefer 'gemini-1.5' or 'gemini-pro', but take whatever works
            model_name = next((m for m in available_models if 'gemini-1.5' in m), None)
            if not model_name:
                model_name = next((m for m in available_models if 'gemini' in m), available_models[0])
            print(f"DEBUG: Selected Model: {model_name}")
            model = genai.GenerativeModel(model_name)
            
            experts_context = ""
            for e in experts:
                experts_context += f"- Name: {e.name} | Headline: {e.headline} | Skills: {e.domains}\n"
            
            system_prompt = f"""
            Act as a Matchmaker.
            SME PROBLEM: "{sme_text}"
            CANDIDATES:
            {experts_context}
            TASK: Pick the top 3 experts. Return JSON ONLY.
            [ {{ "expert_name": "Name", "score": 90, "reason": "Why..." }} ]
            """
            
            response = model.generate_content(system_prompt)
            cleaned = response.text.strip().replace('```json', '').replace('```', '')
            results = json.loads(cleaned)
            
            # Add Prefix
            for r in results:
                r["reason"] = f"⚡ [AI MATCH]: {r.get('reason', '')}"
                
            return results
            
        except Exception as e:
            # print(f"⚠️ AI Failed ({e}). Falling back to keywords.")
            # ERROR MODE: Return specific error card
            return [{
                "expert_name": "⚠️ AI CRASHED",
                "score": 0,
                "reason": str(e)
            }]

    # --- PATH B: DUMB FALLBACK (If No Key or AI Fails) ---
    # Disabled for debugging
    return []
    
    """
    print("⚠️ Using Keyword Fallback")
    matches = []
    search_terms = sme_text.lower().split()
    
    for e in experts:
    ...
    """
