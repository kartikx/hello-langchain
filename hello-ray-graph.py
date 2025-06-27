"""
A simple example of a state graph that processes user input through 3 nodes using Ray remote classes.
"""
import ray
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


@ray.remote
class Node1:
    def process(self, state: InputState) -> OverallState:
        return {
            "intermediate": state["user_input"] + "\n\t-processed by node1",
        }


@ray.remote
class Node2:
    def process(self, state: OverallState) -> OverallState:
        return {
            "intermediate": state["intermediate"] + "\n\t\t-processed by node2",
        }


@ray.remote
class Node3:
    def process(self, state: OverallState) -> OutputState:
        return {
            "graph_output": state["intermediate"] + "\n\t\t\t-processed by node3",
        }


# Create remote actors
node1_actor = Node1.remote()
node2_actor = Node2.remote()
node3_actor = Node3.remote()

# Wrapper functions to interface with LangGraph


def node1(state: InputState) -> OverallState:
    future = node1_actor.process.remote(state)
    return ray.get(future)


def node2(state: OverallState) -> OverallState:
    future = node2_actor.process.remote(state)
    return ray.get(future)


def node3(state: OverallState) -> OutputState:
    future = node3_actor.process.remote(state)
    return ray.get(future)


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
