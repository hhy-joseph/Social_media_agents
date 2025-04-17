from typing import Annotated
from langchain_core.messages import AnyMessage
from typing_extensions import TypedDict
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langchain_xai import ChatXAI
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.prebuilt import ToolNode, tools_condition
from dotenv import load_dotenv

load_dotenv()


class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


memory = MemorySaver()
graph_builder = StateGraph(State)

tool = DuckDuckGoSearchRun()
tools = [tool]

llm = ChatXAI(model="grok-2-1212")
llm_with_tools = llm.bind_tools(tools)


def chatbot(state: State) -> State:
    return {"messages": [llm_with_tools.invoke(state["messages"])]}


graph_builder.add_node("chatbot", chatbot)
tool_node = ToolNode(tools=tools)
graph_builder.add_node("tools", tool_node)

graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
graph_builder.add_edge("tools", "chatbot")
graph_builder.add_edge(START, "chatbot")

graph = graph_builder.compile(checkpointer=memory)
config = {"configurable": {"thread_id": "1"}}


def stream_graph_updates(user_input: str):
    for event in graph.stream(
        {"messages": [
            {"role": "system", "content": 'Reply in Hong Kong\'s traditional Chinese'},
            {"role": "user", "content": user_input}]
        },
        config=config,
        stream_mode="values",
    ):
        # event is the state dictionary
        print("Assistant:", event["messages"][-1].content)


def main():
    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break
            stream_graph_updates(user_input)
        except Exception as e:
            print(f"Error: {e}")
            # Fallback input
            user_input = "What do you know about LangGraph?"
            print("User: " + user_input)
            stream_graph_updates(user_input)
            break


if __name__ == "__main__":
    main()
