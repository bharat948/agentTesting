import re
import json
from typing import Dict, Optional, Tuple
import json
import re
from typing import Tuple, Optional, Dict, Any

def parse_agent_response(response: str) -> Tuple[str, str, Optional[Dict[str, Any]]]:
    """
    Parse the agent response to extract thought, answer, and action (if any).
    Args:
        response: The raw response from the agent
    Returns:
        Tuple of (thought, answer, action) where action is a dictionary (if available) or None.
    """
    thought = ""
    answer = ""
    action = None
    
    # Try to extract JSON from the response
    json_pattern = r'({[\s\S]*})'
    json_matches = re.findall(json_pattern, response)
    
    for potential_json in json_matches:
        try:
            data = json.loads(potential_json)
            # Check if this JSON contains any of our expected keys
            if any(key in data for key in ["thought", "answer", "action"]):
                thought = data.get("thought", "")
                answer = data.get("answer", "")
                action = data.get("action", None)
                return thought, answer, action
        except Exception:
            pass
    
    # Fall back to regex parsing if JSON extraction fails
    thought_match = re.search(r"Thought:\s*(.*?)(?=Answer:|Action:|\Z)", response, re.DOTALL)
    if thought_match:
        thought = thought_match.group(1).strip()
    
    answer_match = re.search(r"Answer:\s*(.*?)(?=Thought:|Action:|\Z)", response, re.DOTALL)
    if answer_match:
        answer = answer_match.group(1).strip()
    
    action_match = re.search(r"Action:\s*({.*?})", response, re.DOTALL)
    if action_match:
        try:
            action = json.loads(action_match.group(1))
        except Exception:
            pass
    
    # If no answer pattern is found and we haven't extracted JSON successfully,
    # use the entire response as the answer (only if thought and action are empty)
    if not answer and not thought and not action:
        answer = response
    
    return thought, answer, action

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