import os
import json
import google.generativeai as genai
from sqlmodel import Session, select
from dotenv import load_dotenv
from models import Expert, engine

# Force Load Environment Variables (for local testing compatibility)
load_dotenv()

def analyze_profile(name: str, bio_text: str, links: str):
    """
    Uses Gemini to extract structured skills from raw text.
    If it fails, it returns a visible error card, not mock data.
    """
    api_key = os.environ.get("GOOGLE_API_KEY")
    
    if not api_key:
        # This should have been caught in app.py, but just in case
        raise ValueError("❌ GOOGLE_API_KEY not found. Analysis failed.")

    # Configure Gemini
    genai.configure(api_key=api_key)
    
    # Auto-discover valid model (safer than hardcoding)
    model_name = "models/gemini-1.5-flash"
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'gemini-1.5' in m.name:
                    model_name = m.name
                    break
    except:
        pass
        
    model = genai.GenerativeModel(model_name)

    # The Forensic Prompt
    system_prompt = f"""
    You are a Forensic Data Extractor for an Expert Marketplace.
    
    INPUT PROFILE:
    Name: {name}
    Bio/Context: {bio_text}
    Links: {links}
    
    TASK:
    Extract specific hard skills and attributes. 
    Do NOT summarize into generic titles like "Digital Marketer". Be specific.
    
    OUTPUT JSON ONLY:
    {{
        "headline": "A sharp, 3-part pipe-separated headline of specific skills (e.g. 'Facebook Ads | Conversion API | Pinterest Marketing')",
        "domains": ["List", "of", "10+", "specific", "tags", "found", "in", "text"],
        "icp_focus": "The exact business type they help (e.g. 'E-commerce Brands', 'Local Biz')",
        "strength_mix": {{ "Strategy": 0.0, "Execution": 0.0 }},
        "confidence_score": 90,
        "vetting_summary": "2 sentences analyzing their specific expertise based on the text provided."
    }}
    """

    try:
        response = model.generate_content(system_prompt)
        cleaned = response.text.strip().replace('```json', '').replace('```', '')
        return json.loads(cleaned)
    except Exception as e:
        # 🚨 THIS IS THE FIX: Return a clear error message instead of mock data 🚨
        print(f"ERROR in AI Analysis: {e}")
        return {
            "headline": "⚠️ AI ANALYSIS FAILED - Check Logs/Key",
            "domains": ["Error"],
            "icp_focus": "Unknown",
            "strength_mix": {"Strategy": 0, "Execution": 0},
            "confidence_score": 0,
            "vetting_summary": f"Error Log: {str(e)}"
        }

def save_expert(analysis_data, name, bio, links):
    """
    Saves the analyzed expert to the DB.
    """
    with Session(engine) as session:
        # Check if expert exists (by name) and update, or create new
        existing_expert = session.exec(select(Expert).where(Expert.name == name)).first()
        
        if existing_expert:
            expert = existing_expert
            # Update fields
            expert.headline = analysis_data.get("headline", "New Expert")
            expert.domains = analysis_data.get("domains", [])
            expert.icp_focus = analysis_data.get("icp_focus", "General")
            expert.strength_mix = analysis_data.get("strength_mix", {})
            expert.confidence_score = analysis_data.get("confidence_score", 50)
            expert.vetting_summary = analysis_data.get("vetting_summary", "")
            expert.mini_case_response = bio # Storing raw bio as case response for now
            expert.links = links
        else:
            # Create new
            expert = Expert(
                name=name,
                headline=analysis_data.get("headline", "New Expert"),
                domains=analysis_data.get("domains", []),
                icp_focus=analysis_data.get("icp_focus", "General"),
                strength_mix=analysis_data.get("strength_mix", {}),
                confidence_score=analysis_data.get("confidence_score", 50),
                vetting_summary=analysis_data.get("vetting_summary", ""),
                mini_case_response=bio,
                links=links
            )
            session.add(expert)
        
        session.commit()
        session.refresh(expert)
        return expert
