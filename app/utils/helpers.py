import re
import json
from typing import Dict, Optional, Tuple

def parse_agent_response(response: str) -> Tuple[str, str]:
    """
    Parse the agent response to extract thought and answer.
    
    Args:
        response: The raw response from the agent
        
    Returns:
        Tuple of (thought, answer)
    """
    thought = ""
    answer = ""
    
    # Try to parse as JSON first
    try:
        data = json.loads(response)
        thought = data.get("thought", "")
        answer = data.get("answer", "")
        if thought and answer:
            return thought, answer
    except:
        pass
    
    # Fall back to regex parsing
    thought_match = re.search(r"Thought:\s*(.*?)(?:\n|$)", response, re.DOTALL)
    if thought_match:
        thought = thought_match.group(1).strip()
    
    answer_match = re.search(r"Answer:\s*(.*)", response, re.DOTALL)
    if answer_match:
        answer = answer_match.group(1).strip()
    else:
        # If no answer pattern found, use the whole response
        answer = response
        
    return thought, answer

def sanitize_input(input_str: str) -> str:
    """
    Sanitize user input to prevent injection attacks.
    
    Args:
        input_str: The raw input string
        
    Returns:
        Sanitized input string
    """
    # Remove any potential script tags or dangerous patterns
    sanitized = re.sub(r'<script.*?>.*?</script>', '', input_str, flags=re.DOTALL)
    # Additional sanitization can be added as needed
    return sanitized 