from fastapi import APIRouter, status
 
from api.schemas.feedback.request import FeedbackRequest
 
router = APIRouter(prefix="/feedback", tags=["Feedback"])
 
 
@router.post("", status_code=status.HTTP_204_NO_CONTENT)
def send_feedback(body: FeedbackRequest):
    # TODO: logika przesy³ania feedbacku
    return 
 