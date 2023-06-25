from langchain.tools.python.tool import PythonAstREPLTool
from langchain import SerpAPIWrapper
from langchain.agents import Tool

def get_python_repl_tool():
    python_repl = PythonAstREPLTool()
    python_repl_tool = Tool(
        name="Python", func=python_repl.run, description=python_repl.description
    )
    python_repl_tool.run(
        "import numpy as np\nimport pandas as pd\nimport plotly.express as px",
        verbose=False,
        color=None,
    )
    return python_repl_tool


def get_search_api_tool():
    search_api = SerpAPIWrapper()
    search_api_tool = Tool(
        name="Search",
        func=search_api.run,
        description="Useful when you need to answer questions about general facts and current events. You should ask targeted questions.",
    )
    return search_api_tool


def get_tools(tool_name):
    tool_dict = dict(
        python_repl=get_python_repl_tool,
        search_api=get_search_api_tool,
    )
    return tool_dict[tool_name]()