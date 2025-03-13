from enum import Enum
from typing import Dict, List, Optional

from app.models.schemas import PromptSection

class ReActAgentPrompt:
    def __init__(self, query="", history="", tools=None):
        """
        Initialize a ReAct agent prompt with customizable fields.
        Args:
            query (str): The primary query.
            history (str): Previous reasoning steps or context.
            tools (list): List of available tool descriptions.
        """
        self.query = query
        self.history = history
        self.tools = tools or []
        self.custom_sections: Dict[str, str] = {}
        
    def add_section(self, section_name: str, content: str) -> None:
        self.custom_sections[section_name] = content
        
    def build_prompt(self, exclude_sections: List[PromptSection] = None) -> str:
        exclude_sections = exclude_sections or []
        sections = []
        if PromptSection.INTRODUCTION not in exclude_sections:
            sections.append(self._get_introduction())
        if PromptSection.CONTEXT not in exclude_sections:
            sections.append(self._get_context_and_history())
        if PromptSection.BEHAVIOR not in exclude_sections:
            sections.append(self._get_behavioral_guidelines())
        if PromptSection.CONSTRAINTS not in exclude_sections:
            sections.append(self._get_functional_constraints())
        if PromptSection.ADAPTATION not in exclude_sections:
            sections.append(self._get_dynamic_adaptation())
        if PromptSection.FORMAT not in exclude_sections:
            sections.append(self._get_response_format())
        if PromptSection.ERROR_HANDLING not in exclude_sections:
            sections.append(self._get_error_handling())
        if PromptSection.METRICS not in exclude_sections:
            sections.append(self._get_performance_metrics())
        for section_name, content in self.custom_sections.items():
            if section_name.lower() not in [s.value for s in exclude_sections]:
                sections.append(f"[{section_name.title()}]\n{content}")
        return "\n\n".join(sections)
        
    def _get_introduction(self) -> str:
        return ("[Introduction & Identity]\n"
                "You are a ReAct (Reasoning and Acting) agent specialized in answering queries by combining detailed reasoning "
                "and tool usage to provide accurate and comprehensive responses. You are tasked with answering the following query: "
                f"{self.query}.")
    
    def _get_context_and_history(self) -> str:
        tools_str = ", ".join(self.tools) if isinstance(self.tools, list) else self.tools
        return (f"[Context & History]\n"
                f"Previous reasoning steps and observations: {self.history}.\n"
                f"Available tools: {tools_str}.")
    
    def _get_behavioral_guidelines(self) -> str:
        return ("[Behavioral Guidelines]\n"
                "- Engage in logical, methodical, and analytical reasoning.\n"
                "- Provide detailed step-by-step analysis of the query.\n"
                "- Maintain clarity, precision, and a formal yet accessible tone.")
    
    def _get_functional_constraints(self) -> str:
        return ("[Functional Constraints & Ethical Guidelines]\n"
                "- Operate strictly within the defined scope of the query.\n"
                "- Use available tools only when additional verified information is necessary.\n"
                "- Base all reasoning on actual observations from prior steps and tool feedback.\n"
                "- Do not provide unverified details; if uncertain, state that you lack sufficient information.")
    
    def _get_dynamic_adaptation(self) -> str:
        return ("[Dynamic Adaptation & Iterative Refinement]\n"
                "- Continuously adjust your reasoning based on the evolving context and new tool outputs.\n"
                "- If a tool yields no results or fails, acknowledge this and consider an alternative approach.\n"
                "- Iteratively refine your reasoning until you are confident in delivering the final answer.")
    
    def _get_response_format(self) -> str:
        return ("[Response Format & Output Instructions]\n"
                "When you need to use a tool, output your next step in the following JSON format:\n"
                '{ "thought": "Your detailed reasoning about what to do next", "action": { "name": "Tool name", '
                '"reason": "Explanation of why you chose this tool", "input": "Specific input for the tool" } }\n'
                "When you have enough information to answer the query, output your final answer in the following JSON format:\n"
                '{ "thought": "Your final reasoning process", "answer": "Your comprehensive answer to the query" }')
    
    def _get_error_handling(self) -> str:
        return ("[Error Handling & Fallback Strategies]\n"
                "- If faced with ambiguous queries or if a tool returns no results, log the issue and request clarification or choose an alternative tool.\n"
                "- Always ensure that every response is built on verified information.")
    
    def _get_performance_metrics(self) -> str:
        return ("[Performance Metrics]\n"
                "- Strive for high accuracy, clarity, and timeliness.\n"
                "- Finalize your answer only when confident that all necessary information has been obtained and verified.") 