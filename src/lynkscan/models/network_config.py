"""This module define NetworkConfig."""

from __future__ import annotations

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field

from lynkscan.utils import FormatConverter


class NetworkConfig(BaseModel):
    """NetworkConfig data model."""

    model_config = ConfigDict(
        alias_generator=FormatConverter.snake_to_camel,
        populate_by_name=True,
    )

    verify_ssl: str | None = Field(
        default=None, description="Path to SSL certificate."
    )
