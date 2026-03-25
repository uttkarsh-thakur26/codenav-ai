import os
from typing import Optional

# --- GOOGLE GENAI IMPORTS (Commented out for future use) ---
# from langchain_google_genai import ChatGoogleGenerativeAI

# --- OPENAI IMPORTS ---
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate


class AnswerGenerator:
    # --- GOOGLE GENAI INIT SIGNATURE (Commented out) ---
    # def __init__(self, model_name: str = "gemini-2.5-flash", api_key: str = None) -> None:
    
    # --- OPENAI INIT SIGNATURE ---
    def __init__(self, model_name: str = "gpt-4o", api_key: Optional[str] = None) -> None:
        
        # --- GOOGLE GENAI KEY RESOLUTION (Commented out) ---
        # actual_key = api_key or os.environ.get("GOOGLE_API_KEY")
        
        # --- OPENAI KEY RESOLUTION ---
        actual_key = api_key or os.environ.get("OPENAI_API_KEY")
        
        if not actual_key:
            raise ValueError(
                "OPENAI_API_KEY is missing! Make sure your .env file is in the root directory and named exactly '.env'."
            )

        # --- GOOGLE GENAI INITIALIZATION (Commented out) ---
        # self.llm = ChatGoogleGenerativeAI(
        #     model=model_name,
        #     api_key=actual_key,
        #     temperature=0.2,
        # )

        # --- OPENAI INITIALIZATION ---
        self.llm = ChatOpenAI(
            model=model_name,
            api_key=actual_key,
            temperature=0.2,
        )

        self.prompt = PromptTemplate(
            input_variables=["context", "question"],
            template=(
                "You are a senior software engineer helping explain a codebase.\n"
                "Use ONLY the provided context to answer.\n"
                "Do not invent details that are not explicitly present in context.\n"
                "You MUST strictly cite file names and line numbers when available in context.\n\n"
                "Context:\n{context}\n\n"
                "Question:\n{question}\n\n"
                "Answer:"
            ),
        )

    def generate(self, question: str, context: str) -> str:
        formatted_prompt = self.prompt.format(context=context, question=question)
        response = self.llm.invoke(formatted_prompt)

        content = getattr(response, "content", "")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts: list[str] = []
            for part in content:
                if isinstance(part, str):
                    parts.append(part)
                elif isinstance(part, dict):
                    text_value = part.get("text")
                    if isinstance(text_value, str):
                        parts.append(text_value)
            return "\n".join(parts).strip()

        return str(response)