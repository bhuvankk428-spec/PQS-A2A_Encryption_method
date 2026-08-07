from agent.ai.model import AIModel


class Conversation:

    def __init__(self):

        self.agent_a = AIModel("Agent A")

        self.agent_b = AIModel("Agent B")