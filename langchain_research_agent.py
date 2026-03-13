from langchain_openai import ChatOpenAI

# LLM setup
llm = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="your_api_key",
    model="openrouter/auto"
)

# research prompt
question = "Explain Artificial Intelligence in simple terms."

response = llm.invoke(question)

print(response.content)