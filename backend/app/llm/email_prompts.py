from langchain_core.prompts import PromptTemplate

EMAIL_CATEGORIZATION_PROMPT = PromptTemplate(
    input_variables=["subject_line", "email_content"],
    template="""
    An email can be categorized as "rejected", "accepted", "action_required", "confirmation", "others", and "unknown".
    'confirmation' emails refer to emails regarding your job application confirmation.
    'rejected' emails refer to emails where you are told that your job application has been rejected,
    or that the position has been filled or closed and that you are not selected.
    'action_required' emails refer to emails where the recruiter/employer ask you to do something,
    that includes asking you to schedule a time for an interview, an online assessment, a take-home assignment,
    or just anything that requires some sort of action from your end. This also includes calendar invites.
    'others' emails refer to emails that do not fall into any of the above categories and are not related to
    job applications or job searching.
    'unknown' emails refer to emails that cannot be categorized but are related to job applications or job searching,
    or an email that you are unsure about.

    Categorize the following email with the following subject line:

    Subject Line: {subject_line}
    Email Content: {email_content}
    """
)
