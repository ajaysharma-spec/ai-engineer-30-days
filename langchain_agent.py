from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

# LLM setup
llm = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="YOUR_API_KEY",
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