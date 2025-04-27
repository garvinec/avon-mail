from http.client import HTTPException
from api.routes.gmail.get_mail import get_email
from fastapi import APIRouter
from llm.email_agent import EmailCategorizationAgent

router = APIRouter()
email_categorization_agent = EmailCategorizationAgent()


@router.post("/analyze-email/{email_id}")
async def analyze_email(email_id: str):
    email_data = await get_email(email_id)
    if email_data is None:
        raise HTTPException(status_code=404, detail="Email not found")
    subject = email_data["subject"]
    content = email_data["body"] if "body" in email_data else email_data["snippet"]
    result = await email_categorization_agent.categorize_email(subject, content)
    return result
