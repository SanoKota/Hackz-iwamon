from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class GeminiInput(BaseModel):
    prompt: str
    # 馬2頭のデータ
    # 仔馬の名前: str


class GeminiOutput(BaseModel):
    # 生のレスポンステキスト（JSONでない場合のフォールバック）
    response: Optional[str] = Field(None, description="raw response text (fallback)")

    # 期待するJSONフィールド（すべて任意）
    name: Optional[str] = Field(None, description="馬名")
    sex: Optional[str] = Field(None, description="性別")
    father: Optional[str] = Field(None, description="父")
    mother: Optional[str] = Field(None, description="母")
    grandfather: Optional[str] = Field(None, description="父方の祖父")

    race_record: Optional[List[Dict[str, Optional[str]]]] = Field(
        None,
        description="過去レースの配列。各要素は {race_name, ranking, date, detail} を含むdict",
    )

    prize_money: Optional[str] = Field(None, description="獲得賞金")
    trainer: Optional[str] = Field(None, description="調教師")
    stable: Optional[str] = Field(None, description="厩舎")
    owner: Optional[str] = Field(None, description="馬主")
    characteristics: Optional[str] = Field(None, description="特徴や適性などの自由記述")

    class Config:
        # 応答に余分なフィールドがあっても許容する
        extra = "allow"