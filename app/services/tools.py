import os
import re
import json
import httpx
import inspect
import subprocess
import importlib
import asyncio
from typing import Dict, List, Optional, Any, Callable

class Tool:
    """Base class for all tools."""
    def __init__(self, name: str, description: str, call_func: Optional[Callable] = None):
        self.name = name
        self.description = description
        self._call_func = call_func

    def __call__(self, *args, **kwargs) -> str:
        if self._call_func:
            return self._call_func(*args, **kwargs)
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
        try:
            result = eval(operation)
            return str(result)
        except Exception as e:
            return f"Error in calculation: {str(e)}"

class WikipediaTool(Tool):
    """Searches Wikipedia for information."""
    def __init__(self):
        super().__init__(
            name="wikipedia",
            description="Searches Wikipedia for information. Example: wikipedia: Django"
        )
    def __call__(self, query: str) -> str:
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
            return f"Error searching Wikipedia: {str(e)}"
    
    async def async_call(self, query: str) -> str:
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
        try:
            with open(file_path, 'r') as file:
                return file.read()
        except Exception as e:
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
        try:
            if "||" in args:
                file_path, content = args.split("||", 1)
            else:
                return "Error: Invalid format. Use 'file_path||content'"
            content = self.strip_code_fence(content)
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            with open(file_path, 'w') as file:
                file.write(content)
            return f"Successfully wrote to {file_path}"
        except Exception as e:
            return f"Error writing to file: {str(e)}"

class FileAppendTool(Tool):
    """Appends content to a file."""
    def __init__(self):
        super().__init__(
            name="append_file",
            description="Appends content to a file. Format: 'file_path||content'. Example: append_file: example.txt||Hello world"
        )
    def __call__(self, args: str) -> str:
        try:
            if "||" in args:
                file_path, content = args.split("||", 1)
            else:
                return "Error: Invalid format. Use 'file_path||content'"
            content = FileWriteTool().strip_code_fence(content)
            with open(file_path, 'a') as file:
                file.write(content)
            return f"Successfully appended to {file_path}"
        except Exception as e:
            return f"Error appending to file: {str(e)}"

class FileSearchTool(Tool):
    """Searches for a string in a file."""
    def __init__(self):
        super().__init__(
            name="search_file",
            description="Searches for a string in a file. Format: 'file_path||search_string'. Example: search_file: example.txt||Hello"
        )
    def __call__(self, args: str) -> str:
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
            return f"Error searching file: {str(e)}"

class FileListTool(Tool):
    """Lists files in a directory."""
    def __init__(self):
        super().__init__(
            name="list_files",
            description="Lists files in a directory. Example: list_files: path/to/directory"
        )
    def __call__(self, directory_path: str) -> str:
        try:
            files = os.listdir(directory_path)
            return "\n".join(files)
        except Exception as e:
            return f"Error listing files: {str(e)}"

class FileDeleteTool(Tool):
    """Deletes a file."""
    def __init__(self):
        super().__init__(
            name="delete_file",
            description="Deletes a file. Example: delete_file: path/to/file.txt"
        )
    def __call__(self, file_path: str) -> str:
        try:
            os.remove(file_path)
            return f"Successfully deleted {file_path}"
        except Exception as e:
            return f"Error deleting file: {str(e)}"

class DirectoryCreateTool(Tool):
    """Creates a directory."""
    def __init__(self):
        super().__init__(
            name="create_directory",
            description="Creates a directory. Example: create_directory: path/to/directory"
        )
    def __call__(self, directory_path: str) -> str:
        try:
            os.makedirs(directory_path, exist_ok=True)
            return f"Successfully created directory {directory_path}"
        except Exception as e:
            return f"Error creating directory: {str(e)}"

class DirectoryDeleteTool(Tool):
    """Deletes a directory."""
    def __init__(self):
        super().__init__(
            name="delete_directory",
            description="Deletes a directory. Example: delete_directory: path/to/directory"
        )
    def __call__(self, directory_path: str) -> str:
        try:
            os.rmdir(directory_path)
            return f"Successfully deleted directory {directory_path}"
        except Exception as e:
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
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout
            else:
                return f"Command error: {result.stderr}"
        except Exception as e:
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
        try:
            # This is a placeholder for actual container execution logic
            # You might use Docker or another container system here
            result = subprocess.run(f"python {script_path}", shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout
            else:
                return f"Container execution error: {result.stderr}"
        except Exception as e:
            return f"Error running container: {str(e)}"

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Tool] = {}
        
    def register(self, tool: Tool) -> Tool:
        self.tools[tool.name] = tool
        print("all the tools", self.tools)
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
        
    def create_tool_from_code(self, name: str, description: str, call_code: str, init_code: str = "") -> Tool:
        """Create a tool from provided code for both __init__ and __call__ methods"""
        try:
            # Define a safe subset of allowed globals
            safe_globals = {
                're': re,
                'os': os,
                'str': str,
                'int': int,
                'float': float,
                'list': list,
                'dict': dict,
                'set': set,
                'tuple': tuple,
                'Exception': Exception,
                'Tool': Tool,  # Allow access to base Tool class
            }
            
            # Create a context for the class
            tool_context = {}
            
            # Properly indent the code blocks
            if init_code:
                # Add additional indentation for init_code
                indented_init_code = "            " + init_code.replace("\n", "\n            ")
            else:
                indented_init_code = "            pass"
                
            if call_code:
                # Add additional indentation for call_code
                indented_call_code = "            " + call_code.replace("\n", "\n            ")
            else:
                indented_call_code = "            pass"
            
            # Remove leading indentation from the template
            class_template = """class DynamicTool(Tool):
        def __init__(self, *args, **kwargs):
            super().__init__(name="{name}", description="{description}")
            try:
    {init_code}
            except Exception as e:
                raise RuntimeError(f"Error in tool initialization: {{str(e)}}")
        
        def __call__(self, *args, **kwargs):
            try:
    {call_code}
            except Exception as e:
                return f"Error in tool execution: {{str(e)}}"
    """.format(name=name, description=description, init_code=indented_init_code, call_code=indented_call_code)

            # Compile and execute the class template in a controlled namespace
            exec(class_template, safe_globals, tool_context)
            
            # Create an instance of the dynamic tool
            custom_tool = tool_context['DynamicTool']()
            return custom_tool
        except Exception as e:
            raise RuntimeError(f"Error creating tool: {str(e)}")
    def load_state(self):
        """Load the tool registry state from a JSON file, if it exists."""
        try:
            if os.path.exists("tool_registry.json"):
                with open("tool_registry.json", "r") as f:
                    tools_state = json.load(f)
                
                for name, info in tools_state.items():
                    # Re-register a simple tool with no custom call function
                    self.tools[name] = Tool(name=name, 
                                           description=info.get("description", ""), 
                                           call_func=None)
        except Exception as e:
            pass
    def save_state(self):
        """Persist the current tool registry state to a JSON file.
        
        This method saves all registered tools' metadata including name, description,
        and code information when available. For dynamic tools created with code,
        it attempts to save the original code used to create them.
        """
        try:
            tools_state = {}
            
            for name, tool in self.tools.items():
                tool_info = {
                    "name": tool.name,
                    "description": tool.description,
                    "type": tool.__class__.__name__
                }
                
                # Try to extract source code for dynamic tools if available
                if hasattr(tool, '_init_code') and tool._init_code:
                    tool_info['init_code'] = tool._init_code
                    
                if hasattr(tool, '_call_code') and tool._call_code:
                    tool_info['call_code'] = tool._call_code
                
                tools_state[name] = tool_info
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath("tool_registry.json")), exist_ok=True)
            
            # Write to file with pretty formatting
            with open("tool_registry.json", "w") as f:
                json.dump(tools_state, f, indent=2)
                
            print(f"Successfully saved {len(tools_state)} tools to registry")
            return True
        except Exception as e:
            print(f"Error saving tool registry state: {str(e)}")
            return False
    
# Initialize a global tool registry instance

tool_registry = ToolRegistry()
def register_built_in_tools(registry):
        """Register all built-in tools with the tool registry.
        
        This function creates instances of all available tool classes
        defined in the tools.py file and registers them with the provided registry.
        
        Args:
            registry: The ToolRegistry instance to register tools with
        
        Returns:
            List of names of all registered tools
        """
        # List of all available tool classes
        tool_classes = [
            CalculateTool,
            WikipediaTool,
            FileReadTool,
            FileWriteTool,
            FileAppendTool,
            FileSearchTool,
            FileListTool,
            FileDeleteTool,
            DirectoryCreateTool,
            DirectoryDeleteTool,
            CommandExecutionTool,
            PythonContainerTool
        ]
        
        registered_tools = []
        
        # Create and register an instance of each tool class
        for tool_class in tool_classes:
            try:
                tool = tool_class()
                registry.register(tool)
                registered_tools.append(tool.name)
                print(f"Registered tool: {tool.name}")
            except Exception as e:
                print(f"Failed to register {tool_class.__name__}: {str(e)}")
        
        return registered_tools
register_built_in_tools(registry=tool_registry)
def some_tool_function() -> str:
    # Dummy implementation for the /tools/function endpoint
    return "Tool function result"