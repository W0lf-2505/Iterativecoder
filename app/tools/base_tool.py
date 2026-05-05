# app/tools/base_tool.py

import subprocess
from typing import Dict
from app.schema.tools_response import build_response
from app.llm.google_client import GoogleClient
from bs4 import BeautifulSoup
import urllib.parse
import requests
import json

class BaseTool:

    #  Static in-memory store (shared globally)
    MEMORY: Dict[str, str] = {}

    #  Allowed commands
    ALLOWED_COMMANDS = ["python", "pip", "pytest", "curl", "docker"]

    BLOCKED_PATTERNS = [
        "rm -rf", "del ", "shutdown", "reboot",
        "&&", "||", ";",
        "..", "/etc", "C:\\Windows"
    ]

    def __init__(self):
        self.google_client = GoogleClient()
    # =========================
    # 🔍 SANITY CHECKS
    # =========================

    @staticmethod
    def command_sanity_check(command: str) -> bool:
        if any(bad in command.lower() for bad in BaseTool.BLOCKED_PATTERNS):
            raise ValueError("Dangerous command detected")

        base_cmd = command.split()[0]

        if base_cmd not in BaseTool.ALLOWED_COMMANDS:
            raise ValueError(f"Command '{base_cmd}' not allowed")

        return True

    @staticmethod
    def path_sanity_check(path: str) -> bool:
        if any(bad in path for bad in BaseTool.BLOCKED_PATTERNS):
            raise ValueError("Dangerous file path detected")

        return True

    # =========================
    # 🌐 BASE TOOLS
    # =========================

    
    def search_web(self,query: str):
        if not query or not query.strip():
            raise ValueError("Search query cannot be empty")
        def clean_query(q: str) -> str:
            q = q.strip()
            if q.lower().startswith("search "):
                q = q[7:]
            return q

        url = "https://html.duckduckgo.com/html/?q=" + urllib.parse.quote_plus(clean_query(query))

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }

        try:
            res = requests.get(url, headers=headers, timeout=10)
            res.raise_for_status()

            soup = BeautifulSoup(res.text, "html.parser")

            raw_results = []

            for g in soup.select("div.tF2Cxc"):
                title = g.select_one("h3")
                link = g.select_one("a")
                snippet = g.select_one(".VwiC3b")

                if title and link:
                    raw_results.append({
                        "title": title.get_text(strip=True),
                        "link": link.get("href"),
                        "snippet": snippet.get_text(" ", strip=True) if snippet else ""
                    })

            if not raw_results:
                for g in soup.select("div.g"):
                    title = g.select_one("h3")
                    link = g.select_one("a")

                    if title and link:
                        raw_results.append({
                            "title": title.get_text(strip=True),
                            "link": link.get("href"),
                            "snippet": ""
                        })

            # Normalize
            def normalize(r):
                return {
                    "title": r["title"][:300],
                    "link": r["link"],
                    "snippet": r["snippet"][:300]
                }

            results = [normalize(r) for r in raw_results]

            # Rank
            def score(r):
                q = query.lower()
                s = 0
                if q in r["title"].lower():
                    s += 2
                if q in r["snippet"].lower():
                    s += 1
                return s

            def extract_clean_text(html: str) -> str:
                soup = BeautifulSoup(html, "html.parser")

                # Remove garbage
                for tag in soup(["script", "style", "noscript", "header", "footer"]):
                    tag.decompose()

                text = soup.get_text(separator=" ")

                # Collapse whitespace
                text = " ".join(text.split())

                return text[:4000]  # hard cap to control token cost
            
            results.sort(key=score, reverse=True)
            if not results:
                cleaned_text = extract_clean_text(res.text)

                return build_response(
                    tool="search_web",
                    input_data={"query": query, "results": [cleaned_text]},
                    stdout="",
                    stderr="run_llm_summary",
                    exit_code=1
                )

            structured_output = {
                "query": query,
                "results": results[:5],
                "count": len(results)
            }

            return build_response(
                tool="search_web",
                input_data={"query": query},
                stdout=json.dumps(structured_output, ensure_ascii=False),  # FIX
                stderr="",
                exit_code=0
            )

        except Exception as e:
            return build_response(
                tool="search_web",
                input_data={"query": query},
                stdout="",
                stderr=str(e),
                exit_code=1,
                error_type=type(e).__name__,
                error_message=str(e)
            )
        
    def search_google_web(self,query: str):
        
        if not query:
            raise ValueError("Search query cannot be empty")

        self.google_client.generate(query)

        try:
            result = self.google_client.generate(query)

            return build_response(
                tool="search_web",
                input_data={"query": query},
                stdout=result.stdout,
                stderr=result.stderr,
                exit_code=result.returncode
            )

        except Exception as e:
            return build_response(
                tool="search_web",
                input_data={"query": query},
                stderr=str(e),
                exit_code=1,
                error_type=type(e).__name__,
                error_message=str(e)
            )


    @staticmethod
    def store_memory(key: str, value: str):
        if not key or not value:
            raise ValueError("Memory key/value cannot be empty")

        if len(key) > 100 or len(value) > 1000:
            raise ValueError("Memory too large")

        BaseTool.MEMORY[key] = value

        return build_response(
            tool="store_memory",
            input_data={"key": key},
            stdout=f"Stored under key: {key}",
            exit_code=0
        )

    @staticmethod
    def retrieve_memory(query: str):
        return build_response(
            tool="retrieve_memory",
            input_data={"query": query},
            stdout=BaseTool.MEMORY.get(query, "No memory found"),
            exit_code=0
        )
    
    def analyze_error(self, error_message):
        
        from app.agent.debugger import DebuggerLLM
        self.llm = DebuggerLLM()
        response = self.llm.generate(error_message)

        return build_response(
            tool="analyze_error",
            input_data={"error": error_message},
            stdout=response,
            exit_code=0
        )