"""License evaluator using LLMs."""

from enum import Enum

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from pydantic import BaseModel


class LicenseCategory(str, Enum):
    """License categories."""

    COPYLEFT: str = "Copyleft"
    WEAK_COPYLEFT: str = "Weak Copyleft"
    PERMISSIVE: str = "Permissive"
    NON_PERMISSIVE: str = "Non Permissive"


class LicenseCategoryResponse(BaseModel):
    """License category response model."""

    category: LicenseCategory


class LicenseEvaluator:
    """Evaluate license category using LLM."""

    def __init__(
        self,
        model: str = "gpt-5",
    ):
        """Initialize the LicenseEvaluator."""
        self.model = model
        self.llm = ChatOpenAI(model=model)

    def run(self, license_name: str, license_text: str) -> LicenseCategory:
        """Run the license evaluator."""
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """
            You are an expert in open source software licensing.
            Your task is to classify the given OSS license
            into one of the following categories:
            - Copyleft
            - Weak Copyleft
            - Permissive
            - Non permissive

            Instructions:
            - Analyze the provided license name and license text.
            - Determine the most appropriate category based on
              standard OSS licensing practices.
            - Return only the category name without any additional
              explanation or text.
            - Explanations of licenses are the following:
                - CopyLeft:
                    - Description:
                        - A license that requires derivative works or
                          redistributed code to be released under
                          the same license terms.
                    - Characteristics:
                      - Ensures that software freedom is preserved across
                        modifications and redistributions.
                        Derivative works cannot be made proprietary.
                    - Examples:
                        - GNU General Public License (GPL) versions 2 and 3
                - Weak CopyLeft:
                    - Description:
                        - A license with copyleft provisions,
                          but with exceptions that allow linking or
                          combining with code under other licenses.
                    - Characteristics:
                        - The copyleft obligation applies mainly to modifications
                          of the licensed component itself,
                          while allowing broader integration in mixed projects.
                    - Examples:
                        - GNU Lesser General Public License (LGPL)
                - Permissive:
                    - Description:
                        - A license that imposes minimal restrictions on reuse,
                          modification, and redistribution.
                    - Typically requires only preservation of copyright and
                      license notices. Derivative works can be released as
                      either open source or proprietary software.
                    - Examples:
                        - MIT License
                - Non permissive:
                    - Description:
                        - A license that places strong restrictions on use,
                          modification, or redistribution, often limiting commercial exploitation.
                    - Characteristics:
                        - May not fully align with the Open Source Definition
                          (as defined by OSI). Commonly used for academic or non-commercial purposes.
                    - Examples:
                        - Creative Commons Non-Commercial (CC-NC) licenses
            """,
                ),
                (
                    "user",
                    """
            License Name: {license_name}
            License Text: {license_text}

            Please provide the license category:
            """,
                ),
            ]
        )
        chain = prompt | self.llm.with_structured_output(
            LicenseCategoryResponse
        )
        response = chain.invoke(
            {
                "license_name": license_name,
                "license_text": license_text,
            }
        )
        category = LicenseCategory(response.category)
        return category
