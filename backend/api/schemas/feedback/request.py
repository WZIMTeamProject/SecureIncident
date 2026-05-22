from pydantic import BaseModel

class FeedbackRequest(BaseModel):
    name: str
    email: str
    message: str