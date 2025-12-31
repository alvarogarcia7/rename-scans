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
        return subprocess.run(command, capture_output=True, text=True)

    def to_list(self, command: str) -> list[str]:
        return re.compile(r"\s+").split(command.strip())
