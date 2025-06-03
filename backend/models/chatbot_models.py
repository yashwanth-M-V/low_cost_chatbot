from pydantic import BaseModel

class ChatInput(BaseModel):
    message: str
    user_id: str

class ChatOutput(BaseModel):
    response: str