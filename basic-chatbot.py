# Step 1. Define the State.
from typing import Annotated

from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START

from langchain.chat_models import init_chat_model

llm = init_chat_model("anthropic:claude-3-5-haiku-latest")


class State(TypedDict):
    messages: Annotated[list, add_messages]


def chatbot(state: State) -> State:
    context = state["messages"]

    response = llm.invoke(context)

    return {"messages": [response]}


# Step 2. Setup the graph.
graph_builder = StateGraph(State)

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")

graph = graph_builder.compile()


def stream_graph_updates(user_input: str):
    for event in graph.stream({"messages": [{"role": "user", "content": user_input}]}):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)


while True:
    user_input = input("User: ")
    if user_input.lower() in ["quit", "exit", "q"]:
        print("Goodbye!")
        break
    stream_graph_updates(user_input)
