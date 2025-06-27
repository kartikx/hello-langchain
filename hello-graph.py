"""
A simple example of a state graph that processes user input through 3 nodes.
"""

from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END


class InputState(TypedDict):
    user_input: str


class OutputState(TypedDict):
    graph_output: str


class OverallState(TypedDict):
    intermediate: str
    user_input: str
    graph_output: str


def node1(state: InputState) -> OverallState:
    return {
        "intermediate": state["user_input"] + "\n\t-processed by node1",
    }


def node2(state: OverallState) -> OverallState:
    return {
        "intermediate": state["intermediate"] + "\n\t\t-processed by node2",
    }


def node3(state: OverallState) -> OutputState:
    return {
        "graph_output": state["intermediate"] + "\n\t\t\t-processed by node3",
    }


builder = StateGraph(OverallState, input=InputState, output=OutputState)
builder.add_node("node1", node1)
builder.add_node("node2", node2)
builder.add_node("node3", node3)
builder.add_edge(START, "node1")
builder.add_edge("node1", "node2")
builder.add_edge("node2", "node3")
builder.add_edge("node3", END)

graph = builder.compile()
output: OutputState = graph.invoke({"user_input": "Hello, Graph!"})

print(output["graph_output"])
