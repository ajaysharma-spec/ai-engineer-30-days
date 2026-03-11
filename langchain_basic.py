from langchain_core.prompts import PromptTemplate

template = PromptTemplate(
    input_variables=["topic"],
    template="Explain {topic} in simple terms."
)

prompt = template.format(topic="Artificial Intelligence")

print(prompt)