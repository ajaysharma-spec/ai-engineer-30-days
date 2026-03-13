from langchain_openai import ChatOpenAI

# LLM setup
llm = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
    model="openrouter/auto"
)

# research prompt
question = "Explain Artificial Intelligence in simple terms."

response = llm.invoke(question)

print(response.content)