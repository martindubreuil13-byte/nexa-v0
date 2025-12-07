import os
import json
import sys
from sqlmodel import Session, create_engine, select
import sys
from sqlmodel import Session, select
from models import Expert, engine

# --- USER INPUT (Legacy/Test) ---
RAW_PROFILE_TEXT = """
Name: Martin (MINDRA)
Headline: Founder & CEO
... (Legacy text for direct run)
"""

def mock_llm_analysis(name: str, bio: str) -> str:
    """Mock response."""
    print(f"⚠️  No API Key found. Using MOCK LLM response for '{name}'.")
    mock_data = {
        "headline": "AI Consultant & Strategist", # Inferred headline if not explicitly passed
        "domains": ["AI Strategy", "Executive Coaching", "Digital Transformation"],
        "icp_focus": "SME Leaders & Enterprise Execs",
        "strength_mix": {"strategy": 0.85, "execution": 0.15},
        "confidence_score": 92,
        "vetting_summary": f"Strong profile for {name}. Bio indicates deep experience in leadership and tech."
    }
    return json.dumps(mock_data)

def analyze_profile(name: str, bio: str, links: str) -> dict:
    """
    Analyzes expert based on structured inputs.
    links is a comma-separated string from the UI.
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    
    if not api_key:
        return json.loads(mock_llm_analysis(name, bio))

    try:
        import google.generativeai as genai
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
        
        system_prompt = f"""
        You are a Forensic Data Extractor. You are NOT a creative writer.
        Input: Expert Bio ({name}).
        Task: Extract exact keywords.
        Constraint: Do NOT invent generic titles like 'AI Consultant' or 'Strategist'.
        
        Analyzing Expert: {name}
        Context Links: {links}
        Profile Content: {bio}
        
        JSON Output Requirements:
        
        1. headline: Must be a string of the top 3 most distinct hard skills found in the text, separated by ' | '. (Example: 'Omnichannel Strategy | Org Design | Retail AI').
        2. domains: Extract 12-15 specific tags (e.g., 'Customer Experience', 'E-commerce Innovation').
        3. fidelity_score: Rate from 0-100 based on how many specific methodologies are mentioned. (Generic = 20, Specific = 90). Using key 'confidence_score' for DB compatibility.
        4. icp_focus: Extract the exact client type mentioned.
        5. strength_mix: precise strategy vs execution split.
        6. vetting_summary: brief forensic summary.
        
        OUTPUT FORMAT (JSON ONLY):
        {{
            "headline": "Skill 1 | Skill 2 | Skill 3",
            "domains": ["Tag1", "Tag2", ...],
            "icp_focus": "Specific Target",
            "strength_mix": {{"strategy": 0.X, "execution": 0.Y}},
            "confidence_score": 0-100,
            "vetting_summary": "Forensic analysis..."
        }}
        """
        
        response = model.generate_content(system_prompt)
        cleaned_response = response.text.strip().replace('```json', '').replace('```', '')
        return json.loads(cleaned_response)
        
    except Exception as e:
        print(f"❌ Error calling Gemini API: {e}")
        return json.loads(mock_llm_analysis(name, bio))

def save_expert(data: dict, name: str, bio: str, links: str):
    # Parse links
    link_list = [l.strip() for l in links.split(',') if l.strip()]
    
    # Check for duplicate
    with Session(engine) as session:
        existing = session.exec(select(Expert).where(Expert.name == name)).first()
        if existing:
            print(f"ℹ️  Expert '{name}' already exists. Updating (Force Overwrite)...")
            existing.headline = data.get("headline", existing.headline)
            existing.domains = data.get("domains", [])
            existing.icp_focus = data.get("icp_focus", "General")
            existing.strength_mix = data.get("strength_mix", {})
            existing.confidence_score = data.get("confidence_score", 0)
            existing.vetting_summary = data.get("vetting_summary", "")
            existing.links = link_list
            existing.mini_case_response = bio # Storing bio/case in this field for now
            
            session.add(existing)
            session.commit()
            session.refresh(existing)
            return existing

    expert = Expert(
        name=name,
        headline=data.get("headline", "Expert"),
        rate=0.0, # Default, could extract if asked
        links=link_list,
        domains=data.get("domains", []),
        icp_focus=data.get("icp_focus", "General"),
        strength_mix=data.get("strength_mix", {}),
        confidence_score=data.get("confidence_score", 0),
        mini_case_response=bio,
        vetting_summary=data.get("vetting_summary", "")
    )
    
    with Session(engine) as session:
        session.add(expert)
        session.commit()
        session.refresh(expert)
        print(f"✅ Expert '{expert.name}' CREATED.")
        return expert

if __name__ == "__main__":
    # Test run
    analyze_profile("Test User", "Bio here...", "http://example.com")
