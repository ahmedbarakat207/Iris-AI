import os
import subprocess
import glob
import re
import json
from typing import Any

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "run_command",
            "description": "Execute a shell command on the user's local machine.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The exact shell command to run.",
                    }
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a local file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "Absolute or relative path to the file.",
                    }
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write or overwrite a file with new content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to the file."},
                    "content": {
                        "type": "string",
                        "description": "The full content to write.",
                    },
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "list_dir",
            "description": "List contents of a directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path to the directory."}
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "grep_search",
            "description": "Search for a string pattern within files.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The string or regex pattern to search for.",
                    },
                    "path": {
                        "type": "string",
                        "description": "Directory or file to search in.",
                    },
                },
                "required": ["query", "path"],
            },
        },
    },
]


def execute_tool(name: str, args: dict, workspace_root: str) -> str:
    if not workspace_root or workspace_root == "none":
        workspace_root = os.getcwd()

    try:
        if name == "run_command":
            cmd = args.get("command", "")
            if not cmd:
                return "Error: No command provided."
            result = subprocess.run(
                cmd,
                shell=True,
                cwd=workspace_root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=60,
            )
            output = result.stdout.strip()
            return (
                output
                if output
                else f"Command executed successfully with exit code {result.returncode} (no output)."
            )

        elif name == "read_file":
            filepath = args.get("path", "")
            abs_path = (
                filepath
                if os.path.isabs(filepath)
                else os.path.join(workspace_root, filepath)
            )
            with open(abs_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            return content

        elif name == "write_file":
            filepath = args.get("path", "")
            content = args.get("content", "")
            abs_path = (
                filepath
                if os.path.isabs(filepath)
                else os.path.join(workspace_root, filepath)
            )
            os.makedirs(os.path.dirname(abs_path), exist_ok=True)
            with open(abs_path, "w", encoding="utf-8") as f:
                f.write(content)
            return f"Successfully wrote to {filepath}"

        elif name == "list_dir":
            dirpath = args.get("path", ".")
            abs_path = (
                dirpath
                if os.path.isabs(dirpath)
                else os.path.join(workspace_root, dirpath)
            )
            if not os.path.isdir(abs_path):
                return f"Error: {dirpath} is not a directory."
            items = os.listdir(abs_path)
            res = []
            for item in items:
                p = os.path.join(abs_path, item)
                size = os.path.getsize(p) if os.path.isfile(p) else "-"
                res.append(
                    f"{item} ({'DIR' if os.path.isdir(p) else 'FILE'}) - {size} bytes"
                )
            return "\n".join(res) if res else "Directory is empty."

        elif name == "grep_search":
            query = args.get("query", "")
            search_path = args.get("path", ".")
            abs_path = (
                search_path
                if os.path.isabs(search_path)
                else os.path.join(workspace_root, search_path)
            )
            cmd = ["grep", "-rnIE", query, abs_path]
            result = subprocess.run(
                cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
            )
            output = result.stdout.strip()
            return output if output else "No matches found."

        else:
            return f"Error: Unknown tool {name}"

    except Exception as e:
        return f"Error executing {name}: {str(e)}"
