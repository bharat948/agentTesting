import os
import re
import httpx
import subprocess
import logging
import asyncio
from typing import Dict, List, Optional

from app.core.logging import setup_logging

global_logger = setup_logging()

class Tool:
    """Base class for all tools."""
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def __call__(self, *args, **kwargs) -> str:
        raise NotImplementedError("Tool must implement __call__ method")
    
    async def async_call(self, *args, **kwargs) -> str:
        """Async version of the call method"""
        return self(*args, **kwargs)

class CalculateTool(Tool):
    """Evaluates mathematical expressions."""
    def __init__(self):
        super().__init__(
            name="calculate",
            description="Evaluates mathematical expressions. Example: calculate: 4 * 7 / 3"
        )
    def __call__(self, operation: str) -> str:
        global_logger.info(f"Calculating: {operation}")
        try:
            result = eval(operation)
            return str(result)
        except Exception as e:
            global_logger.error(f"Calculation error: {e}")
            return f"Error in calculation: {str(e)}"

class WikipediaTool(Tool):
    """Searches Wikipedia for information."""
    def __init__(self):
        super().__init__(
            name="wikipedia",
            description="Searches Wikipedia for information. Example: wikipedia: Django"
        )
    def __call__(self, query: str) -> str:
        global_logger.info(f"Searching Wikipedia for: {query}")
        try:
            response = httpx.get("https://en.wikipedia.org/w/api.php", params={
                "action": "query",
                "list": "search",
                "srsearch": query,
                "format": "json"
            })
            response.raise_for_status()
            data = response.json()
            if "query" in data and "search" in data["query"] and data["query"]["search"]:
                return data["query"]["search"][0]["snippet"]
            return "No results found on Wikipedia."
        except Exception as e:
            global_logger.error(f"Wikipedia search error: {e}")
            return f"Error searching Wikipedia: {str(e)}"
    
    async def async_call(self, query: str) -> str:
        global_logger.info(f"Async searching Wikipedia for: {query}")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get("https://en.wikipedia.org/w/api.php", params={
                    "action": "query",
                    "list": "search",
                    "srsearch": query,
                    "format": "json"
                })
                response.raise_for_status()
                data = response.json()
                if "query" in data and "search" in data["query"] and data["query"]["search"]:
                    return data["query"]["search"][0]["snippet"]
                return "No results found on Wikipedia."
        except Exception as e:
            global_logger.error(f"Async Wikipedia search error: {e}")
            return f"Error searching Wikipedia: {str(e)}"

# File Management Tools
class FileReadTool(Tool):
    """Reads content from a file."""
    def __init__(self):
        super().__init__(
            name="read_file",
            description="Reads content from a file. Example: read_file: path/to/file.txt"
        )
    def __call__(self, file_path: str) -> str:
        global_logger.info(f"Reading file: {file_path}")
        try:
            with open(file_path, 'r') as file:
                return file.read()
        except Exception as e:
            global_logger.error(f"File reading error: {e}")
            return f"Error reading file: {str(e)}"

class FileWriteTool(Tool):
    """Writes content to a file."""
    def __init__(self):
        super().__init__(
            name="write_file",
            description="Writes content to a file. Format: 'file_path||content'. Example: write_file: example.txt||Hello world"
        )
    def strip_code_fence(self, content: str) -> str:
        content = content.strip()
        pattern_backticks = r"^```(?:\w+)?\n?(.*?)\n?```$"
        match = re.match(pattern_backticks, content, re.DOTALL)
        if match:
            return match.group(1).strip()
        pattern_triple_quotes = r'^"""(?:\w+)?\n?(.*?)\n?"""$'
        match = re.match(pattern_triple_quotes, content, re.DOTALL)
        if match:
            return match.group(1).strip()
        return content
    def __call__(self, args: str) -> str:
        global_logger.info(f"Writing to file with args: {args}")
        try:
            if "||" in args:
                file_path, content = args.split("||", 1)
            else:
                return "Error: Invalid format. Use 'file_path||content'"
            content = self.strip_code_fence(content)
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            with open(file_path, 'w') as file:
                global_logger.info(f"Writing content to {file_path}")
                file.write(content)
            return f"Successfully wrote to {file_path}"
        except Exception as e:
            global_logger.error(f"File writing error: {e}")
            return f"Error writing to file: {str(e)}"

class FileAppendTool(Tool):
    """Appends content to a file."""
    def __init__(self):
        super().__init__(
            name="append_file",
            description="Appends content to a file. Format: 'file_path||content'. Example: append_file: example.txt||Hello world"
        )
    def __call__(self, args: str) -> str:
        global_logger.info(f"Appending to file with args: {args}")
        try:
            if "||" in args:
                file_path, content = args.split("||", 1)
            else:
                return "Error: Invalid format. Use 'file_path||content'"
            content = FileWriteTool().strip_code_fence(content)
            with open(file_path, 'a') as file:
                global_logger.info(f"Appending content to {file_path}")
                file.write(content)
            return f"Successfully appended to {file_path}"
        except Exception as e:
            global_logger.error(f"File appending error: {e}")
            return f"Error appending to file: {str(e)}"

class FileSearchTool(Tool):
    """Searches for a string in a file."""
    def __init__(self):
        super().__init__(
            name="search_file",
            description="Searches for a string in a file. Format: 'file_path||search_string'. Example: search_file: example.txt||Hello"
        )
    def __call__(self, args: str) -> str:
        global_logger.info(f"Searching in file with args: {args}")
        try:
            if "||" in args:
                file_path, search_string = args.split("||", 1)
            else:
                return "Error: Invalid format. Use 'file_path||search_string'"
            with open(file_path, 'r') as file:
                content = file.read()
            matches = re.findall(re.escape(search_string), content)
            return f"Found {len(matches)} occurrences of '{search_string}'"
        except Exception as e:
            global_logger.error(f"File search error: {e}")
            return f"Error searching file: {str(e)}"

class FileListTool(Tool):
    """Lists files in a directory."""
    def __init__(self):
        super().__init__(
            name="list_files",
            description="Lists files in a directory. Example: list_files: path/to/directory"
        )
    def __call__(self, directory_path: str) -> str:
        global_logger.info(f"Listing files in directory: {directory_path}")
        try:
            files = os.listdir(directory_path)
            return "\n".join(files)
        except Exception as e:
            global_logger.error(f"Error listing files: {e}")
            return f"Error listing files: {str(e)}"

class FileDeleteTool(Tool):
    """Deletes a file."""
    def __init__(self):
        super().__init__(
            name="delete_file",
            description="Deletes a file. Example: delete_file: path/to/file.txt"
        )
    def __call__(self, file_path: str) -> str:
        global_logger.info(f"Deleting file: {file_path}")
        try:
            os.remove(file_path)
            return f"Successfully deleted {file_path}"
        except Exception as e:
            global_logger.error(f"File deletion error: {e}")
            return f"Error deleting file: {str(e)}"

class DirectoryCreateTool(Tool):
    """Creates a directory."""
    def __init__(self):
        super().__init__(
            name="create_directory",
            description="Creates a directory. Example: create_directory: path/to/directory"
        )
    def __call__(self, directory_path: str) -> str:
        global_logger.info(f"Creating directory: {directory_path}")
        try:
            os.makedirs(directory_path, exist_ok=True)
            return f"Successfully created directory {directory_path}"
        except Exception as e:
            global_logger.error(f"Directory creation error: {e}")
            return f"Error creating directory: {str(e)}"

class DirectoryDeleteTool(Tool):
    """Deletes a directory."""
    def __init__(self):
        super().__init__(
            name="delete_directory",
            description="Deletes a directory. Example: delete_directory: path/to/directory"
        )
    def __call__(self, directory_path: str) -> str:
        global_logger.info(f"Deleting directory: {directory_path}")
        try:
            os.rmdir(directory_path)
            return f"Successfully deleted directory {directory_path}"
        except Exception as e:
            global_logger.error(f"Directory deletion error: {e}")
            return f"Error deleting directory: {str(e)}"

# Command Execution Tool
class CommandExecutionTool(Tool):
    """Executes shell commands."""
    def __init__(self):
        super().__init__(
            name="execute_command",
            description="Executes a shell command. Example: execute_command: ls -la"
        )
    def __call__(self, command: str) -> str:
        global_logger.info(f"Executing command: {command}")
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout
            else:
                return f"Command error: {result.stderr}"
        except Exception as e:
            global_logger.error(f"Command execution error: {e}")
            return f"Error executing command: {str(e)}"

# Container Management Tool
class PythonContainerTool(Tool):
    """Runs Python code in a container."""
    def __init__(self):
        super().__init__(
            name="run_python_container",
            description="Runs Python code in a container. Example: run_python_container: path/to/script.py"
        )
    def __call__(self, script_path: str) -> str:
        global_logger.info(f"Running Python script in container: {script_path}")
        try:
            # This is a placeholder for actual container execution logic
            # You might use Docker or another container system here
            result = subprocess.run(f"python {script_path}", shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout
            else:
                return f"Container execution error: {result.stderr}"
        except Exception as e:
            global_logger.error(f"Container execution error: {e}")
            return f"Error running container: {str(e)}"

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        
    def register(self, tool: Tool) -> Tool:
        self.tools[tool.name] = tool
        return tool
        
    def get(self, tool_name: str) -> Optional[Tool]:
        return self.tools.get(tool_name)
        
    def list_tools(self) -> List[Tool]:
        return list(self.tools.values())
        
    def remove(self, tool_name: str) -> bool:
        if tool_name in self.tools:
            del self.tools[tool_name]
            return True
        return False

    def save_state(self):
        # Implement logic to save the current state of tools to a file or database
        pass

    def load_state(self):
        # Implement logic to load the state of tools from a file or database
        pass

# Initialize the tool registry and register all tools
tool_registry = ToolRegistry()
tool_registry.register(CalculateTool())
tool_registry.register(WikipediaTool())
tool_registry.register(FileReadTool())
tool_registry.register(FileWriteTool())
tool_registry.register(FileAppendTool())
tool_registry.register(FileSearchTool())
tool_registry.register(FileListTool())
tool_registry.register(FileDeleteTool())
tool_registry.register(DirectoryCreateTool())
tool_registry.register(DirectoryDeleteTool())
tool_registry.register(CommandExecutionTool())
tool_registry.register(PythonContainerTool())

def some_tool_function():
    # existing code...
    return "Tool function result"

# existing code...