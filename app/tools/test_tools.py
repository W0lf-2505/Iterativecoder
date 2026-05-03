# Our Agent Runs tests on the code it generates. This file contains the tools for running those tests.

import subprocess
from app.schema.tools_response import build_response


def run_tests(cwd=None):

    try:
        result = subprocess.run(
            ["pytest", "-q"],
            cwd=cwd,
            capture_output=True,
            text=True
        )

        stdout = result.stdout or ""
        stderr = result.stderr or ""
        exit_code = result.returncode

        return build_response(
            tool="run_tests",
            input_data={},
            stdout=stdout,
            stderr=stderr,
            exit_code=exit_code
        )

    except Exception as e:
        return build_response(
            tool="run_tests",
            input_data={},
            stderr=str(e),
            exit_code=1
        )