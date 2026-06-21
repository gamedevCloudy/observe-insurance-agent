import uuid

from langchain_core.messages import HumanMessage

from app.agents.call_agent.agent import build_agent


def main():
    agent = build_agent()
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    print("Observe Insurance Support Agent (CLI)")
    print("Type 'exit' to quit.\n")

    while True:
        user = input("You: ").strip()
        if not user:
            continue
        if user.lower() in {"exit", "quit"}:
            print("Goodbye.")
            break

        for event in agent.stream(
            {"messages": [HumanMessage(content=user)]},
            config,
            stream_mode="values",
        ):
            event["messages"][-1].pretty_print()
        print()


if __name__ == "__main__":
    main()
