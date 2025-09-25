"""This module define NetworkConfig."""

from __future__ import annotations

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field

from lynkscan.utils import FormatConverter


class LlmConfig(BaseModel):
    """LLM configuration data model."""

    model_config = ConfigDict(
        alias_generator=FormatConverter.snake_to_camel,
        populate_by_name=True,
    )

    detector_model: str = Field(
        default="gemma3:latest", description="Model for license detection"
    )
