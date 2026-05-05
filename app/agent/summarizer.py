import os
from app.llm.agent_llm import AgentLLM


class SummarizerLLM:

    def __init__(self):
        self.llm = AgentLLM("summarizer.txt", "mistral")

    def generate_action(self, query: str, results: str):

        context = f""" WHere 
         query is {query} 
        and results is {chr(10).join(results)} """

        return self.llm.generate_action(context)