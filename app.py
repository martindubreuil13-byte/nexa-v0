import streamlit as st
import ingest_expert
import match_engine
import json

# Page Config
st.set_page_config(
    page_title="NEXA Lab",
    page_icon="🧬",
    layout="wide"
)

# --- BRANDING & STYLING ---
st.logo("logo.jpg")

st.markdown("""
<style>
    /* Modern Button Styling */
    div.stButton > button {
        border-radius: 8px;
        font-weight: bold;
        border: none;
        transition: all 0.3s ease;
    }
    
    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 224, 255, 0.3);
    }

    /* Header Styling */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        letter-spacing: -0.5px;
    }
    
    /* Input Field Styling */
    .stTextArea textarea, .stTextInput input {
        border-radius: 8px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: #00E0FF;
        box-shadow: 0 0 0 1px #00E0FF;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("🧬 NEXA v0")
    st.write("Expert Vetting & Matching Engine")
    st.caption("Powered by Gemini (or Mock) & SQLModel")
    
    st.divider()
    
    # Mock status for API Key
    import os
    if os.environ.get("GOOGLE_API_KEY"):
        st.success("✅ Gemini API Key Detected")
    else:
        st.warning("⚠️ Using Mock LLM Mode")

    st.divider()
    
    st.subheader("📊 Database Status")
    try:
        from sqlmodel import Session, select
        from models import Expert, engine
        with Session(engine) as session:
            experts = session.exec(select(Expert)).all()
            st.metric("Total Experts", len(experts))
            with st.expander("Show Names"):
                for e in experts:
                    st.text(f"• {e.name}")
    except Exception as e:
        st.error(f"DB Error: {e}")

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("⚠️ Reset (Seed)"):
            try:
                import seed
                from sqlmodel import SQLModel 
                from models import engine
                SQLModel.metadata.drop_all(engine)
                SQLModel.metadata.create_all(engine)
                seed.seed_data()
                st.toast("Reseeded!", icon="♻️")
            except Exception as e:
                st.error(f"Reset failed: {e}")
    
    with col2:
        if st.button("🗑️ Nuke All"):
            try:
                from sqlmodel import SQLModel
                from models import engine
                SQLModel.metadata.drop_all(engine)
                SQLModel.metadata.create_all(engine)
                st.toast("Nuked! DB Empty.", icon="☢️")
            except Exception as e:
                st.error(f"Nuke failed: {e}")

# Main Interface
st.title("The Lab")

tab1, tab2 = st.tabs(["🧪 Expert Vetting (Supply)", "🩺 SME Matching (Demand)"])

# --- TAB 1: EXPERT VETTING ---
with tab1:
    st.subheader("Ingest & Vet New Expert")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.write("#### 1. Expert Details")
        vet_name = st.text_input("Full Name", placeholder="e.g. Dr. Elena Vance")
        
        vet_links = st.text_input("External Links (comma separated)", placeholder="LinkedIn, Personal Site, Portfolio...")
        
        vet_bio = st.text_area(
            "Bio & Case Study Answer",
            height=200,
            placeholder="Paste their professional bio and answer to the case study question here..."
        )
        
        vet_btn = st.button("Vet Expert", type="primary", use_container_width=True)

    with col2:
        if vet_btn:
            if not vet_name or not vet_bio:
                st.warning("Please provide at least a Name and Bio.")
            else:
                with st.spinner(f"Analyzing {vet_name} with NEXA Core..."):
                    try:
                        # 1. Analyze
                        # Now passing name, bio, links separately
                        analysis = ingest_expert.analyze_profile(vet_name, vet_bio, vet_links)
                        
                        # 2. Save
                        expert = ingest_expert.save_expert(analysis, vet_name, vet_bio, vet_links)
                        
                        st.success(f"Expert '{expert.name}' Ingested Successfully!")
                        
                        # Display Results
                        st.metric("Confidence Score", f"{expert.confidence_score}/100")
                        st.write(f"**Headline:** {expert.headline}")
                        st.write(f"**Vetting Summary:** {expert.vetting_summary}")
                        
                        # Display specific skills/domains
                        st.write("**Extracted Skills:**")
                        st.markdown(" ".join([f"`{d}`" for d in expert.domains]))
                        
                        if expert.links:
                            st.caption(f"🔗 Links: {', '.join(expert.links)}")
                        
                        with st.expander("View Raw Database Record"):
                            st.json(expert.model_dump())
                        
                    except Exception as e:
                        st.error(f"Error processing expert: {e}")

# --- TAB 2: SME MATCHING ---
with tab2:
    st.subheader("Diagnose & Match SME Need")
    
    cols = st.columns([2, 1])
    with cols[0]:
        sme_query = st.text_input(
            "Describe the business problem...", 
            placeholder="e.g. I need B2B lead gen help for my SaaS."
        )
    with cols[1]:
        st.write("") # Spacer
        st.write("") 
        match_btn = st.button("Find Match", type="primary", use_container_width=True)
    
    st.divider()
    
    if match_btn and sme_query:
        with st.spinner("NEXA 'Smart Match' running..."):
            # Now returns list of dicts: {expert_name, score, reason}
            matches = match_engine.find_best_matches(sme_query)
        
        if not matches:
            st.info("No suitable matches found.")
        else:
            st.write(f"Found {len(matches)} AI-Ranked Matches:")
            
            for m in matches:
                # Find the full expert object from DB or just display what we have? 
                # The prompt returns name, so we might want to look up details if we strictly need them,
                # but for V0, displaying the Name + AI reason is key.
                # Let's try to match it back to the DB object for extra context if possible, 
                # or just display the AI output cleanly.
                
                with st.container(border=True):
                    c1, c2 = st.columns([3, 1])
                    with c1:
                        st.write(f"**{m['expert_name']}**")
                        st.info(f"💡 **Why:** {m['reason']}")
                    with c2:
                        st.metric("Match Score", f"{m['score']}/100")
