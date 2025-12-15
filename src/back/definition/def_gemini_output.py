from pydantic import BaseModel

class GeminiInput(BaseModel):
    prompt: str
    # 馬2頭のデータ
    # 仔馬の名前: str


class GeminiOutput(BaseModel):
    response: str
