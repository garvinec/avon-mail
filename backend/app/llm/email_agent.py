from dotenv import load_dotenv
import os
from typing import Literal
from typing_extensions import TypedDict
from llm.email_prompts import EMAIL_CATEGORIZATION_PROMPT
from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

load_dotenv()


class EmailCategory(BaseModel):
    category: str = Field(
        None, description="The category of the email.")
    reasoning: str = Field(
        None, description="Why the email is categorized as this category."
    )


class EmailCategorizationAgent:
    def __init__(self, model_name: str = "gemini-2.0-flash"):
        self.llm = ChatGoogleGenerativeAI(
            model=model_name, api_key=os.getenv("GOOGLE_API_KEY"))
        self.workflow = self._create_workflow()

    class State(TypedDict):
        subject_line: str
        email: str
        final: Literal["rejected", "accepted", "action_required",
                       "confirmation", "others", "unknown", '']

    def _keyword_search(self, state: State):
        """Use keyword search to determine if the email is a rejection, acceptance, action required, or confirmation email."""
        rejection_keywords = [
            "unfortunately",
            "not move forward",
            "not to move forward",
            "not to move you forward",
            "will not be moving forward",
            "won't be moving forward",
            "not selected",
            "regret to inform you",
            "move forward with another candidate",
            "move forward with other candidates"
        ]

        acceptance_keywords = [
            "congratulations",
            "excited to offer",
            "delighted to offer"
        ]

        action_required_keywords = [
            "invite you to",
            "to chat",
            "technical assessment",
            "coding assessment",
            "coding challenge",
            "online assessment",
            "online test",
            "assessment",
            "hackerrank",
            "video interview",
            "next step",
            "next steps",
            "please provide",
            "calendly",
            "one-time pass code",
            "otp",
            "verify your email",
            "verify your account",
            "confirm your email"
        ]

        confirmation_keywords = [
            "received your application",
            "reviewing your application",
            "we'll review",
            "will review",
            "will reach out",
            "to receive your application",
            "application has been received",
            "application was sent"
        ]

        # First, count how many categories have matching keywords
        matches = 0
        has_rejection = any(keyword in state["email"].lower()
                            for keyword in rejection_keywords)
        has_acceptance = any(
            keyword in state["email"].lower() for keyword in acceptance_keywords)
        has_action = any(keyword in state["email"].lower()
                         for keyword in action_required_keywords)
        has_confirmation = any(
            keyword in state["email"].lower() for keyword in confirmation_keywords)

        # Count total matches
        matches = sum([has_rejection, has_acceptance,
                      has_action, has_confirmation])

        # If more than one category matches, return empty
        if matches > 1:
            return {"final": ''}

        # If exactly one category matches, return that category
        if has_rejection:
            return {"final": 'rejected'}
        elif has_acceptance:
            return {"final": 'accepted'}
        elif has_action:
            return {"final": 'action_required'}
        elif has_confirmation:
            return {"final": 'confirmation'}
        else:
            return {"final": ''}

    def _check_keyword_search_result(self, state: State):
        """Gate function to check if keyword search is enough to determine the email category."""
        if state["final"] == '':
            return "Fail"
        return "Pass"

    def _llm_call(self, state: State):
        """LLM call to categorize the email"""
        prompt_formatted_str: str = EMAIL_CATEGORIZATION_PROMPT.format(
            subject_line=state["subject_line"],
            email_content=state["email"])
        structured_llm = self.llm.with_structured_output(EmailCategory)
        msg = structured_llm.invoke(prompt_formatted_str)
        return {"final": msg.category}

    def _create_workflow(self):
        """Create the workflow graph"""
        workflow = StateGraph(self.State)

        # Add nodes
        workflow.add_node("keyword_search", self._keyword_search)
        workflow.add_node("llm_call", self._llm_call)

        # Add edges to connect nodes
        workflow.add_edge(START, "keyword_search")
        workflow.add_conditional_edges(
            "keyword_search",
            self._check_keyword_search_result,
            {"Fail": "llm_call", "Pass": END}
        )
        workflow.add_edge("llm_call", END)

        return workflow.compile()

    async def categorize_email(self, subject_line: str, email_content: str) -> str:
        """
        Categorize an email using the workflow.

        Args:
            email_content: The content of the email to categorize

        Returns:
            str: The category of the email (rejected, accepted, action_required, confirmation, others, or unknown)
        """
        result = await self.workflow.ainvoke({"subject_line": subject_line, "email": email_content, "final": ''})
        return result["final"]

    # TODO: POSSIBLY REMOVE THIS IF NOT NEEDED
    def categorize_email_sync(self, subject_line: str, email_content: str) -> str:
        """
        Synchronous version of categorize_email
        """
        result = self.workflow.invoke(
            {"subject_line": subject_line, "email": email_content, "final": ''})
        return result["final"]
