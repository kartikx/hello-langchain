"""
A simple example of a state graph that processes user input through 3 nodes using Ray remote classes.
"""
import ray
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent

"""
Notes
Using a ray.ObjectRef without any of the ray.remote stuff works fine.
"""


class GraphState(TypedDict):
    # ref resolves to the previous state's messages.
    ref: ray.ObjectRef
    messages: list[str]


@ray.remote
class Agent:
    def __init__(self, agent):
        self.agent = agent

    def invoke(self, state: GraphState) -> GraphState:
        print("Running agent: ", self.agent.name)
        print("State: ", state)

        last_messages = ray.get(state["ref"])

        print("Last messages: ", last_messages)

        # ? Even if I hardcode these, it still fails.
        result = self.agent.invoke({"messages": last_messages})

        return {"ref": result}


class LangGraphNode:
    def __init__(self, agent):
        self.agent = Agent.remote(agent)

    def invoke(self, state: GraphState) -> GraphState:
        ref = state["ref"]
        print("Invoking LangGraphNode with ref: ", ref)
        next_ref = self.agent.invoke.remote({"ref": ref})
        print("Next ref: ", next_ref)
        return {"ref": next_ref}


def github_search(query: str) -> str:
    """
    Search GitHub for repositories matching the query.
    """

    print(f"Searching GitHub for: {query}")
    results = ["Langchain is a framework for building LLM applications",]
    return ",".join(results)


github_agent = create_react_agent(
    model="anthropic:claude-3-5-haiku-latest",
    tools=[github_search],
    prompt="""
        You are a helpful assistant that can search GitHub.
        When asked to search GitHub, use the github_search tool.
        Respond with the search results.
        """,
    name="github_agent",
)


github_node = LangGraphNode(github_agent)

builder = StateGraph(GraphState)
builder.add_node("github_node", github_node.invoke)
builder.add_edge(START, "github_node")
builder.add_edge("github_node", END)

graph = builder.compile()

messages = [{"role": "user",
             "content": "Search code for most recent news app."}]

init_message_ref = ray.put(messages)

output = graph.invoke({"ref": init_message_ref, "messages": []})

output = ray.get(output["ref"])
print("Output is: ", output)
