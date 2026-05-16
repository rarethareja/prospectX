import requests
import csv
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

def generate_email(lead):
    prompt = f"""You are Alex, a salesperson at ProspectX.

ProspectX helps businesses automate their sales outreach using AI — saving hours of manual work and booking more meetings.

You are writing a cold email TO a potential client.

THE RECIPIENT IS:
- Name: {lead['first_name']}
- Job Title: {lead['job_title']}
- Company: {lead['company']}
- Industry: {lead['industry']}

YOU are Alex from ProspectX. THEY are the potential client.

Write the email following these rules:
- Max 70 words
- Do NOT say you are from {lead['company']} — you are from ProspectX
- First line: one specific observation about the {lead['industry']} industry
- Middle: one sentence on how ProspectX can help them specifically
- End: one simple question like "Would you be open to a 15 min call?"
- Sign off as: Alex, ProspectX
- No brackets, no placeholders, no generic greetings like "I hope this finds you well"

Write the email only. Nothing else."""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "phi", "prompt": prompt, "stream": False}
    )
    raw = response.json()["response"].strip()
    
    for cutoff in ["Alex, ProspectX", "Alex from ProspectX", "Best regards"]:
        if cutoff in raw:
            idx = raw.index(cutoff) + len(cutoff)
            raw = raw[:idx].strip()
            break
    return raw

def send_email(to_email, subject, body):
    gmail = os.getenv("GMAIL_ADDRESS")
    password = os.getenv("GMAIL_APP_PASSWORD")

    msg = MIMEMultipart()
    msg["From"] = gmail
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(gmail, password)
        server.send_message(msg)


def process_and_save(csv_file):
    with open(csv_file, newline="") as f:
        leads = list(csv.DictReader(f))

    total = len(leads)
    for i, lead in enumerate(leads, 1):
        print(f"⏳ Processing {i}/{total}: {lead['first_name']} at {lead['company']}...")

        email = generate_email(lead)

        supabase.table("leads").upsert({
            "first_name": lead["first_name"],
            "last_name":  lead.get("last_name", ""),
            "email":      lead["email"],
            "company":    lead["company"],
            "job_title":  lead["job_title"],
            "industry":   lead["industry"],
            "status":     "contacted",
            "generated_email": email
        }, on_conflict="email").execute()

        # Send the email
        send_email(
            to_email=lead["email"],
            subject=f"Quick idea for {lead['company']}",
            body=email
        )

        print(f"✅ Saved & sent to {lead['email']}")
        print(f"📧 Preview: {email[:80]}...\n")


# Run it
process_and_save("test_leads.csv")
print("\n🎉 All done!")
