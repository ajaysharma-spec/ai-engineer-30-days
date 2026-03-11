from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

# LLM setup
llm = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
    model="openrouter/auto"
)

# Tool definition
@tool
def calculator(expression: str) -> str:
    """Useful for performing math calculations."""
    return str(eval(expression))

# Test question
question = "What is 45 * 12?"

# LLM reasoning
response = llm.invoke(question)

print(response.content)