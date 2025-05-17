def base_instruction():
    return """You are a helpful assistant with access to shell commands.

You can use the following tools:
1. **execute_shell_command**: Executes any shell command and return status, stdout, stderr and returncode.

"""