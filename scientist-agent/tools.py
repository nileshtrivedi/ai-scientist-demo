# from google.adk.agents import Agent
from google.adk.agents.llm_agent import Agent
# from google.adk.code_executors.built_in_code_executor import BuiltInCodeExecutor
# from google.adk.tools import built_in_code_execution
# from google.adk.tools import google_search
from google.adk.tools import ToolContext
from google.genai import types
import os
import pysd
import pandas as pd
import numpy as np
import re
import pathlib
import asyncio
import logging
from typing import List, Dict, Any, Optional

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

READ_ALLOWED_DIRECTORIES = ["source/models"]
WRITE_ALLOWED_DIRECTORIES = ["source/models"]

def read_text_file(path: str) -> Dict[str, Any]:
    """Read the contents of a text file."""
    # Only allow reading from allowed directories
    if not any(path.startswith(allowed_dir) for allowed_dir in READ_ALLOWED_DIRECTORIES):
        raise ValueError(f"Writing to {path} is not allowed. Allowed directories: {READ_ALLOWED_DIRECTORIES}")

    return {
        "status": "success",
        "content": pathlib.Path(path).read_text(),
        "logs": f"Read {path} successfully."
    }


def write_text_file(path: str, content: str) -> Dict[str, Any]:
    """Write content to a text file."""

    # Only allow writing to allowed directories
    if not any(path.startswith(allowed_dir) for allowed_dir in WRITE_ALLOWED_DIRECTORIES):
        raise ValueError(f"Writing to {path} is not allowed. Allowed directories: {WRITE_ALLOWED_DIRECTORIES}")

    return {
        "status": "success",
        "result": pathlib.Path(path).write_text(content),
        "logs": f"Wrote to {path} successfully."
    }


def list_directory(path: str, recursive: bool = False) -> Dict[str, Any]:
            """List contents of a directory.
            
            Args:
                path: The directory path to list
                recursive: If True, recursively list all subdirectories and their contents. Default is False.
            """
            entries = []
            base_path = pathlib.Path(path)
            
            if recursive:
                # Use rglob to recursively list all files and directories
                for entry in base_path.rglob("*"):
                    # Skip the base directory itself
                    if entry == base_path:
                        continue
                    entries.append({
                        "path": str(entry),
                        "type": "file" if entry.is_file() else "directory",
                    })
            else:
                # Original behavior for non-recursive listing
                for entry in base_path.iterdir():
                    entries.append({
                        "path": str(entry),
                        "type": "file" if entry.is_file() else "directory",
                    })
                    
            print(f"Path: {path}, Entries: {entries}")
            
            return {
                "status": "success",
                "entries": entries,
                "logs": f"Listed contents of {path} successfully."
            }


def list_models(topic: str) -> Dict[str, Any]:
    """Lists all system dynamics models in the given topic.
    
    Args:
        topic: The topic to list models from. This will be interpreted as a subdirectory of "source/models/" in the local file system.
        example: "Epidemic"
    
    Returns:
        dict: A dictionary containing the `status` (success/failure), and `files` whose value is an array of strings which are paths to model files (either vensim or xmile) inside `source/models/<topic>`.
        example: {"status": "success", "entries": ["SI.mdl", "SIR.xmile", "SEIR.mdl"], "logs": "Listed models successfully."}
    """
    res = list_directory("source/models/" + topic, recursive=True)
    return {
        "status": res["status"],
        "entries": [e for e in res["entries"] if e["type"] == "file" and (e["path"].endswith(".mdl") or e["path"].endswith(".xmile"))],
        "logs": res["logs"]
    }

async def read_png_file(image_path: str, artifact_name: str, tool_context: "ToolContext") -> dict:
    """Reads an image from the given local path and saves it as an artifact.
    
    Args:
        image_path: The path to the image file.
        artifact_name: The name to save the artifact as. For eg: "simulation_results.png"
    
    Returns:
        dict: A dictionary containing the status (success/failure), artifact_name and message.
    """
    print("Inside read_image.......")
    with open(image_path, "rb") as f:
        image_bytes = f.read()
        artifact_name = artifact_name
        artifact_part = types.Part.from_bytes(
            data=image_bytes,
            mime_type="image/png",
        )
        print("Saving artifact....")
        await tool_context.save_artifact(artifact_name, artifact_part)
        return {
            "status": "success",
            "message": "Image loaded successfully and stored in artifacts.",
            "artifact_name": artifact_name
        }

def execute_python_code_snippet(code: str) -> dict:
    """Executes the given code using Python's `exec` and returns the result.
    No need to import pysd or matplotlib or pandas as they are already imported.
    Never install any new packages or libraries (pip or apt or a manual download from the internet).
    Uses a global variable `output` to store the result of the executed code.
    For logging, code should append messages into another global variable `logs`. For ex: logs += "\n Reading file..."
    
    Args:
        code: The code to execute.
    
    Returns:
        A dict containing `status` (boolean), `output` which will have the value of the variable `output` in the code, and `logs` which will contain messages logged in the `logs` variable in the code.
    """
    # We evaluate the code using exec() to allow for dynamic execution
    exec(f"global output;\nglobal logs;\nlogs = '';\n{code}")
    global output;
    global logs;
    return {
        "status": "success",
        "output": str(output),
        "logs": str(logs),
    }

async def execute_shell_command(command: str, current_working_directory: Optional[str] = None) -> Dict[str, Any]:
    """Executes the given shell command and returns the result.
    
    Args:
        command: The shell command to execute.
    
    Returns:
        A dict containing `status` (boolean), `stdout` and `stderr` as strings, and `returncode` as an integer.
    """
    try:
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=current_working_directory
        )
        
        stdout, stderr = await process.communicate()
        
        return {
            "stdout": stdout.decode() if stdout else "",
            "stderr": stderr.decode() if stderr else "",
            "returncode": process.returncode,
            "status": "success" if process.returncode == 0 else "failure"
        }
    except Exception as e:
        return {
            "stdout": "",
            "stderr": str(e),
            "returncode": 1,
            "status": "failure"
        }