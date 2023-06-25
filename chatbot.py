import os

from langchain.agents.agent import AgentExecutor
from langchain.agents.openai_functions_agent.base import OpenAIFunctionsAgent
from langchain.memory import ConversationBufferWindowMemory
from langchain.chat_models import ChatOpenAI
from langchain.prompts import MessagesPlaceholder
from langchain.schema import SystemMessage
import tools


class Manager:
    def __init__(
        self,
        model_name: str,
        openai_api_key: str,
        system_message: str = "You are a helpful AI assistant.",
        tool_list: list = [],
    ):
        """Initialize the agent manager."""
        self.openai_api_key = openai_api_key
        self.system_message = system_message
        agent_tools = []
        for tool_name in tool_list:
            tool = tools.get_tools(tool_name)
            agent_tools.append(tool)
        self.create_agent(model_name=model_name, tools=agent_tools)

    def run(self, message: str, **kwargs) -> str:
        """Run the agent on a message."""
        return self.agent_executor.run(message, **kwargs)

    def create_agent(self, model_name, tools):
        """Create a new agent executor object."""
        memory = ConversationBufferWindowMemory(
            k=10, memory_key="memory", return_messages=True
        )

        llm = ChatOpenAI(
            model_name=model_name,
            temperature=0.2,
            streaming=False,
            openai_api_key=self.openai_api_key,
        )

        agent = OpenAIFunctionsAgent.from_llm_and_tools(
            llm=llm,
            tools=tools,
            system_message=SystemMessage(content=self.system_message),
            extra_prompt_messages=[MessagesPlaceholder(variable_name="memory")],
        )

        agent_executor = AgentExecutor.from_agent_and_tools(
            agent=agent,
            tools=tools,
            memory=memory,
            verbose=True,
            max_iterations=7,
            handle_parsing_errors="Error: Check your output and make sure it conforms!",
        )
        self.agent_executor = agent_executor
