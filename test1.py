import requests
import csv

def generate_email(lead):
    prompt = f"""You are an expert B2B sales copywriter.

Write a cold email for these details:
- Name: {lead['first_name']}
- Company: {lead['company']}
- Title: {lead['job_title']}
- Industry: {lead['industry']}

Rules:
- Max 80 words
- No placeholders like [Your Name]
- Sound human, direct, not salesy
- First line must be specific to their industry
- End with one short question
- Sign off as "Alex"

Write the email only, nothing else."""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "phi", "prompt": prompt, "stream": False}
    )
    return response.json()["response"]


def process_csv(filename):
    with open(filename, newline="") as f:
        reader = csv.DictReader(f)
        for lead in reader:
            print(f"\n--- Email for {lead['first_name']} at {lead['company']} ---")
            print(generate_email(lead))
            print()


# Create a small test CSV on the fly
test_leads = """first_name,company,job_title,industry
Sarah,Acme Corp,VP of Sales,SaaS
Raj,TechFlow,CEO,Fintech
Priya,GrowthLabs,Head of Marketing,Ecommerce"""

with open("test_leads.csv", "w") as f:
    f.write(test_leads)

print("Generating emails for all leads...\n")
process_csv("test_leads.csv")
