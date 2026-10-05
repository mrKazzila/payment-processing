from pydantic import BaseModel


class SHealthcheckResponse(BaseModel):
    status: str
