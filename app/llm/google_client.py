import os
import requests
from dotenv import load_dotenv
from google.adk.agents import Agent, SequentialAgent, ParallelAgent, LoopAgent
from google.adk.models.google_llm import Gemini
from google.adk.agents import LlmAgent 
from google.adk.runners import InMemoryRunner
from google.adk.tools import AgentTool, FunctionTool, google_search
from google.genai import types
from app.llm.base import BaseLLM
import asyncio


load_dotenv()


class GoogleClient(BaseLLM): #Gemini 3.1 Flash Lite
    # "gemini-3.1-flash-live-preview"
    # "gemini-3.1-flash-lite-preview"

    def __init__(self, model="gemini-3.1-flash-live-preview"):
        self.model = os.getenv("GOOGLE_MODEL") or model

    def generate(self, prompt: str) -> str:

        retry_config=types.HttpRetryOptions(
            attempts=5,  # Maximum retry attempts
            exp_base=7,  # Delay multiplier
            initial_delay=1, # Initial delay before first retry (in seconds)
            http_status_codes=[429, 500, 503, 504] # Retry on these HTTP errors
        )

        research_agent = LlmAgent(
            name="ResearchAgent",
            # model=Gemini(
            #     model=self.model,
            #     retry_options=retry_config    
            # ),
            model=self.model,
            instruction="""You are a specialized research agent. Your only job is to use the
            google_search tool to find 2-3 pieces of relevant information on the given topic and present the findings with citations.""",
            tools=[google_search],
            output_key="research_findings",  # The result of this agent will be stored in the session state with this key.
        )

        # Summarizer Agent: Its job is to summarize the text it receives.
        summarizer_agent = LlmAgent(
            name="SummarizerAgent",
            # model=Gemini(
            #     model=self.model,
            #     retry_options=retry_config    
            # ),
            model=self.model,
            # The instruction is modified to request a bulleted list for a clear output format.
            instruction="""Read the provided research findings: {research_findings}
        Create a concise summary as a bulleted list with 3-5 key points.""",
            output_key="final_summary",
        )


        root_agent = LlmAgent(
            name="ResearchCoordinator",
            # model=Gemini(
            #     model=self.model,
            #     retry_options=retry_config    
            # ),
            model=self.model,
            # This instruction tells the root agent HOW to use its tools (which are the other agents).
            instruction="""You are a research coordinator. Your goal is to answer the user's query by orchestrating a workflow.
        1. First, you MUST call the `ResearchAgent` tool to find relevant information on the topic provided by the user.
        2. Next, after receiving the research findings, you MUST call the `SummarizerAgent` tool to create a concise summary.
        3. Finally, present the final summary clearly to the user as your response.""",
            # We wrap the sub-agents in `AgentTool` to make them callable tools for the root agent.
            tools=[AgentTool(research_agent), AgentTool(summarizer_agent)],
        )

        runner = InMemoryRunner(agent=root_agent)

        response = asyncio.run(runner.run_debug(
            prompt
        ))
        return response

