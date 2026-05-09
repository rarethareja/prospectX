import requests
import csv
import os
from supabase import create_client
from dotenv import load_dotenv

# Load credentials
load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def generate_email(lead):
    prompt = f"""Write a cold outreach email from a salesperson to a potential client.

Sender: Alex (a salesperson)
Recipient: {lead['first_name']}, {lead['job_title']} at {lead['company']} ({lead['industry']} industry)

Rules:
- Max 80 words
- Sound human and direct
- Reference their industry in line 1
- One specific question at the end
- Sign off as Alex
- No placeholders, no brackets"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "phi", "prompt": prompt, "stream": False}
    )
    return response.json()["response"].strip()


def process_and_save(csv_file):
    with open(csv_file, newline="") as f:
        leads = list(csv.DictReader(f))

    total = len(leads)
    for i, lead in enumerate(leads, 1):
        print(f"⏳ Processing {i}/{total}: {lead['first_name']} at {lead['company']}...")

        # Generate email
        email = generate_email(lead)

        # Save to Supabase
        supabase.table("leads").upsert({
            "first_name": lead["first_name"],
            "last_name":  lead.get("last_name", ""),
            "email":      lead["email"],
            "company":    lead["company"],
            "job_title":  lead["job_title"],
            "industry":   lead["industry"],
            "status":     "new",
            "generated_email": email
        }, on_conflict="email").execute()

        print(f"✅ Saved {lead['first_name']} to database")
        print(f"📧 Email preview: {email[:80]}...\n")


# Run it
process_and_save("test_leads.csv")
print("\n🎉 All leads saved to Supabase!")
