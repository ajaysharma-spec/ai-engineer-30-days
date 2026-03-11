from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="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",
    model="openrouter/auto"
)

template = PromptTemplate(
    input_variables=["topic"],
    template="Explain {topic} in simple terms."
)

prompt = template.format(topic="Neural Networks")

response = llm.invoke(prompt)

print(response.content)