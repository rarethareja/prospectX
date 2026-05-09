import requests
from dotenv import load_dotenv

# Ask Ollama (running locally) to generate an email
def generate_email(lead):
    prompt = f"""Write a short personalized cold email to {lead['first_name']}, 
who is the {lead['job_title']} at {lead['company']} in the {lead['industry']} industry.

Rules:
- Max 100 words
- Sound human, not salesy
- End with one simple question
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": "phi",
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json()["response"]


# Our fake test lead
lead = {
    "first_name": "Sarah",
    "company": "Acme Corp",
    "job_title": "VP of Sales",
    "industry": "SaaS"
}

email = generate_email(lead)
print(email)
