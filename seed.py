from sqlmodel import SQLModel, Session
from models import Expert, engine

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def seed_data():
    experts = [
        Expert(
            name="Elena 'The Strategist' V.",
            headline="B2B SaaS Growth Strategy for Series A+",
            rate=350.0,
            domains=["B2B Lead Gen", "SaaS Pricing", "GTM Strategy"],
            icp_focus="Post-PMF SaaS Scale-ups",
            strength_mix={"strategy": 0.9, "execution": 0.1},
            confidence_score=95,
            mini_case_response="To fix the leaky bucket, I'd first audit the churn analytics by cohort. Usually, it's an activation problem, not a retention one. I'd implement a concierge onboarding flow for high-value tiers.",
            vetting_summary="Top-tier strategic thinker. Expensive but high leverage. Best for teams that have developers to execute but lack direction."
        ),
        Expert(
            name="Mark 'The Builder' S.",
            headline="HubSpot Implementation & Automation Specialist",
            rate=85.0,
            domains=["CRM Setup", "Email Automation", "HubSpot"],
            icp_focus="Early-stage Solopreneurs / Small Teams",
            strength_mix={"strategy": 0.2, "execution": 0.8},
            confidence_score=88,
            mini_case_response="I'll set up 3 core workflows: Lead Nurture, Deal Pipeline automations, and a Re-engagement campaign. I can get this live in 48 hours if you provide the copy.",
            vetting_summary="Pure executor. Great value for money if you know exactly what you want built. Not a strategist."
        ),
        Expert(
            name="Sarah 'Niche' K.",
            headline="FinTech Compliance & Risk Consultant",
            rate=200.0,
            domains=["FinTech", "Compliance", "Risk Management"],
            icp_focus="FinTech Startups (Seed to Series B)",
            strength_mix={"strategy": 0.6, "execution": 0.4},
            confidence_score=92,
            mini_case_response="For the new lending product, we need to review the KYC flow against the latest AML directives. I'd propose a risk-based approach to minimize friction for low-risk users.",
            vetting_summary="Deep domain expert in a high-stakes niche. Essential for FinTechs, irrelevant for everyone else."
        ),
        Expert(
            name="David 'The Scaling' R.",
            headline="Performance Marketing (FB/Google Ads)",
            rate=150.0,
            domains=["Paid Social", "PPC", "Creative Strategy"],
            icp_focus="E-commerce & D2C Brands",
            strength_mix={"strategy": 0.4, "execution": 0.6},
            confidence_score=85,
            mini_case_response="I'd A/B test 5 creative variations on FB focusing on UGC style ads. For Google, we need to tighten the negative keywords list to stop wasting spend on 'free' seekers.",
            vetting_summary="Solid performance marketer. Good balance of thinking and doing. metrics-driven."
        ),
        Expert(
            name="Jessica 'The Fixer' L.",
            headline="Operational Efficiency & Process Design",
            rate=120.0,
            domains=["Notion", "Zapier", "SOP Creation"],
            icp_focus="Agencies & Service Businesses",
            strength_mix={"strategy": 0.5, "execution": 0.5},
            confidence_score=90,
            mini_case_response="Your team is drowning because knowledge is siloed. I'll build a central team wiki in Notion and automate the client onboarding handoff using Zapier.",
            vetting_summary="Excellent at bringing order to chaos. Very practical and hands-on."
        )
    ]

    with Session(engine) as session:
        # Check if DB is already seeded to avoid duplicates
        existing = session.query(Expert).first()
        if existing:
            print("Database already contains data. Skipping seed.")
            return

        for expert in experts:
            session.add(expert)
        session.commit()
    print("Seeding complete: 5 experts added.")

if __name__ == "__main__":
    create_db_and_tables()
    seed_data()
