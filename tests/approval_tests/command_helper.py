import os
import re
import subprocess
import sys


class CommandHelper:

    @staticmethod
    def return_command_of(command: list[str]) -> int:
        return CommandHelper._run_command(command).returncode

    @staticmethod
    def invoke_command(command: list[str]) -> str:
        print(os.getcwd())


        result = CommandHelper._run_command(command)
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        print(f"Result code: {result.returncode}")

        return f"""\
Executed command: {' '.join(command)}
Result code: {result.returncode}
Standard Output (starting on the new line):
{result.stdout}
Standard Error (starting on the new line):
{result.stderr}"""

    @staticmethod
    def _run_command(command: list[str]) -> subprocess.CompletedProcess[str]:
        # Change to project root directory
        # Get the directory of this file (tests/approval_tests/command_helper.py)
        # Go up two levels to reach project root
        current_file = os.path.abspath(__file__)
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_file)))
        return subprocess.run(command, capture_output=True, text=True, cwd=project_root)

    def to_list(self, command: str) -> list[str]:
        return re.compile(r"\s+").split(command.strip())
