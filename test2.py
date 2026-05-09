import requests
import csv
import json
from datetime import datetime

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


def process_csv(filename):
    results = []

    with open(filename, newline="") as f:
        leads = list(csv.DictReader(f))

    total = len(leads)
    for i, lead in enumerate(leads, 1):
        print(f"⏳ Generating {i}/{total}: {lead['first_name']} at {lead['company']}...")
        email = generate_email(lead)
        results.append({
            "lead": lead,
            "email": email
        })

    return results


def save_results(results):
    # Save as readable text file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"emails_{timestamp}.txt"

    with open(filename, "w") as f:
        for r in results:
            lead = r["lead"]
            f.write(f"TO: {lead['first_name']} {lead.get('last_name','')} <{lead.get('email','')}>\n")
            f.write(f"COMPANY: {lead['company']} | TITLE: {lead['job_title']}\n")
            f.write("-" * 50 + "\n")
            f.write(r["email"] + "\n")
            f.write("=" * 50 + "\n\n")

    print(f"\n✅ Saved {len(results)} emails to {filename}")
    return filename


# --- Test leads CSV ---
test_leads = """first_name,last_name,email,company,job_title,industry
Sarah,Chen,sarah@acme.com,Acme Corp,VP of Sales,SaaS
Raj,Kumar,raj@techflow.com,TechFlow,CEO,Fintech
Priya,Sharma,priya@growthlabs.com,GrowthLabs,Head of Marketing,Ecommerce"""

with open("test_leads.csv", "w") as f:
    f.write(test_leads)

# --- Run ---
results = process_csv("test_leads.csv")
save_results(results)

# --- Preview first email ---
print("\n📧 Preview of first email:")
print("-" * 40)
print(results[0]["email"])
