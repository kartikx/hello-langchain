from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model
from langchain_core.messages import AnyMessage
from langchain_core.runnables import RunnableConfig
from langgraph.prebuilt.chat_agent_executor import AgentState

model = init_chat_model(
    "anthropic:claude-3-5-haiku-latest",
    temperature=0
)


def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"


def prompt(state: AgentState, config: RunnableConfig) -> list[AnyMessage]:
    """Prompt for the agent."""
    user_name = config["configurable"].get("user_name")

    system_message = f"You are a helpful assistant. Address the user as {user_name}"

    return [system_message] + state["messages"]


agent = create_react_agent(
    model=model,
    tools=[get_weather],
    prompt=prompt
)

# Run the agent
response = agent.invoke(
    {"messages": [{"role": "user", "content": "what is the weather in sf"}]},
    config={"configurable": {"user_name": "Kartik"}}
)


print(response["messages"][1].content)
