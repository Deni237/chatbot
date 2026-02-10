from langchain_core.messages import HumanMessage, AIMessage


class SimpleMemory:
    def __init__(self):
        self.history = []

    def get_messages(self):
        return self.history

    def add_turn(self, user_input: str, assistant_output: str):
        self.history.append(HumanMessage(content=user_input))
        self.history.append(AIMessage(content=assistant_output))


def create_memory():
    return SimpleMemory()
