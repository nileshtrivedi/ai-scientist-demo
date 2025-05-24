from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

from google.adk.agents.llm_agent import Agent
from google.adk.tools import load_artifacts

from .tools import list_models, read_text_file, write_text_file, execute_python_code_snippet, read_png_file, execute_shell_command, browse
from .pysd_prompt import pysd_expert_instruction


# from .base_prompt import base_instruction

# cli_and_browsing_expert = Agent(
#     model="gemini-2.5-flash-preview-04-17",
#     name="cli_and_browsing_expert",
#     instruction=base_instruction(),
#     tools=[execute_shell_command, browse,]
# )

root_agent = Agent(
    # model="gemini-2.5-flash-preview-04-17",
    # model="gemma-3-12b-it",
    model=LiteLlm(model="ollama_chat/phi4:latest"),
    name="pysd_expert_agent",
    instruction=pysd_expert_instruction(),
    tools=[
        list_models,
        execute_python_code_snippet,
        read_png_file,
        read_text_file,
        write_text_file,
        load_artifacts,
    ]
)