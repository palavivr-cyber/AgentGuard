from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class RetrievalResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    found: bool
    trust: float = Field(ge=0.0, le=1.0)
    latency: float = Field(ge=0.0)
    doc: str
    status: str
    vendor: str
    retrieval_mode: Literal["LOCAL_DEMO", "MOSS", "MOSS_ERROR", "UNKNOWN"]
