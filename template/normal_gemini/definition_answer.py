from pydantic import BaseModel

class DefinitionAnswer(BaseModel):
    """Geminiが出力するものの型の定義"""
    
    answer: str
