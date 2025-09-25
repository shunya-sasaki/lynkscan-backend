"""License checker with LLM."""

import os

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama
from pydantic import BaseModel
from pydantic import Field


class License(BaseModel):
    """License model."""

    full_name: str = Field(
        description="Full name of the license,"
        + " e.g., 'Apache License 2.0', 'MIT License'."
    )

    identifier: str = Field(
        description="SPDX identifier of the license,"
        + " e.g., 'Apache-2.0', 'MIT'."
    )


class LicenseDetector:
    """Detect license using LLM."""

    def __init__(
        self,
        model: str = "gemma3:latest",
    ):
        """Initialize the LicenseDetector."""
        self.model = model
        self.base_url = self._detect_base_url()
        self.llm = ChatOllama(model=self.model, base_url=self.base_url)
        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
            You are an expert in open source software licensing.
            Your task is to identify the primary OSS lisense
            from the input text.

            Instructions:
            - Focus on identifying starndard OSS lisenses such as Apache-2.0,
              MIT, GPL-3.0, BSD-3Clause, etc.
            - If multiple lisenses are mentioned, return the primary license
              (the one that governs most of the code).
            - Ignore project-specific names or contributors
              unless they define a custom license.
            - Return only the license name and SPDX identifier.
            - Do not include unrelated terms, contributors,
              or file names in the output.

            Output format:
            {{
                'full_name': 'Apache Lisense 2.0',
                'identifier': 'Apache-2.0'
            }}
            """,
                ),
                ("human", "{text}"),
            ]
        )

    def _detect_base_url(self, base_url: str | None = None) -> str:
        """Detect the base URL for Ollama API."""
        if base_url is not None:
            return base_url
        env_base_url = os.getenv("OLLAMA_HOST")
        if env_base_url is not None:
            return env_base_url
        return "http://localhost:11434"

    def run(
        self,
        text: str | None,
        license_file: str | None = None,
        max_length: int = 1000,
    ) -> License:
        """Run the license detector."""
        if text is None:
            with open(
                license_file, "r", encoding="utf-8", errors="ignore"
            ) as fin:
                text = fin.read()
        trimed_text = text[:max_length]
        chain = self.prompt | self.llm.with_structured_output(License)
        license = chain.invoke({"text": trimed_text})
        license = License.model_validate(license)
        return license
