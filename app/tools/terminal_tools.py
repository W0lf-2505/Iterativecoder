import os
from pydoc import text
import subprocess
from turtle import color
from .base_tool import BaseTool

from app.schema.tools_response import build_response
from app.tools.base_tool import BaseTool

class TerminalTools(BaseTool):
    failed_sanity_check_response = build_response(
        tool="file_operation",
        stderr="Error: File path failed sanity check.",
        input_data={},
        exit_code=1
    )
    def __init__(self):

        if os.name == 'nt':  # Windows
            self.allowed_directory = os.path.join(os.getcwd(), 'workspace')
        else:  # Unix/Linux/Mac
            self.allowed_directory = os.path.join(os.getcwd(), 'workspace')

    def run_command(self, command, cwd=None):
        if self.command_sanity_check(command):
            try:
                result = subprocess.run(
                    command.split(),
                    cwd=cwd,
                    capture_output=True,
                    text=True
                )
                return build_response(
                    tool="run_command",
                    input_data={"command": command},
                    stdout=result.stdout or '',
                    stderr=result.stderr or '',
                    exit_code=result.returncode
                )
            except subprocess.CalledProcessError as e:
                return build_response(
                    tool="run_command",
                    input_data={"command": command},
                    stderr=e.stderr or '',
                    exit_code=e.returncode
                )
        return self.failed_sanity_check_response

    def install_package(self, package_name, cwd=None):
        if not package_name.isidentifier():
            return build_response(
                tool="install_package",
                input_data={"package_name": package_name},
                stderr="Error: Invalid package name.",
                exit_code=1
            )
        if self.command_sanity_check(f"pip install {package_name}"):
            try:
                subprocess.run(
                    f"pip install {package_name}", 
                    cwd=cwd,
                    capture_output=True,
                    shell=True, 
                    check=True)
                return build_response(
                    tool="install_package",
                    input_data={"package_name": package_name},
                    stdout=f"{package_name} installed successfully.",
                    exit_code=0
                )
            except subprocess.CalledProcessError as e:
                return build_response(
                    tool="install_package",
                    input_data={"package_name": package_name},
                    stderr=f"Error installing {package_name}: {e.stderr or ''}",
                    exit_code=e.returncode
                )
        return self.failed_sanity_check_response

    def create_virtual_environment(self, env_name="venv", cwd=None):
        if self.command_sanity_check(f"python -m venv {env_name}"):
            try:
                subprocess.run(f"python -m venv {env_name}", cwd=cwd,
                    capture_output=True,shell=True, check=True)
                return build_response(
                    tool="create_virtual_environment",
                    input_data={"env_name": env_name},
                    stdout=f"Virtual environment '{env_name}' created successfully.",
                    exit_code=0
                )
            except subprocess.CalledProcessError as e:
                return build_response(
                    tool="create_virtual_environment",
                    input_data={"env_name": env_name},
                    stderr=f"Error creating virtual environment '{env_name}': {e.stderr or ''}",
                    exit_code=e.returncode
                )
        return self.failed_sanity_check_response

    def activate_virtual_environment(self, env_name="venv", cwd=None):
        if self.path_sanity_check(env_name):
            if os.name == 'nt':  # Windows
                activate_script = os.path.join(env_name, 'Scripts', 'activate')
            else:  # Unix/Linux/Mac
                activate_script = os.path.join(env_name, 'bin', 'activate')
            
            if os.path.exists(activate_script):
                print(f"To activate the virtual environment, run: source {activate_script}")
                if os.name == 'nt':
                    subprocess.run(f"./{activate_script}", cwd=cwd,
                        capture_output=True,shell=True)
                else:
                    subprocess.run(f"source {activate_script}", cwd=cwd,
                        capture_output=True,shell=True)
                return build_response(
                    tool="activate_virtual_environment",
                    input_data={"env_name": env_name},
                    stdout=f"Virtual environment '{env_name}' activated.",
                    exit_code=0
                )
            else:
                print(f"Virtual environment '{env_name}' does not exist.")
                return build_response(
                    tool="activate_virtual_environment",
                    input_data={"env_name": env_name},
                    stderr=f"Virtual environment '{env_name}' does not exist.",
                    exit_code=1
                )
        return self.failed_sanity_check_response

    def deactivate_virtual_environment(self, cwd=None):
        print("To deactivate the virtual environment, run: deactivate")
        try:
            subprocess.run("deactivate", shell=True, cwd=cwd,
                    capture_output=True,check=True)
            return build_response(
                tool="deactivate_virtual_environment",
                input_data={},
                stdout="Virtual environment deactivated.",
                exit_code=0
            )
        except subprocess.CalledProcessError as e:
            print(f"Error deactivating virtual environment: {e.stderr or ''}")
            return build_response(
                tool="deactivate_virtual_environment",
                input_data={},
                stderr=f"Error deactivating virtual environment: {e.stderr or ''}",
                exit_code=e.returncode
            )

    def run_in_container(self, container_name, command, cwd=None):
        if self.command_sanity_check(f"docker exec {container_name} {command}"):
            try:
                result = subprocess.run(f"docker exec {container_name} {command}", cwd=cwd,shell=True, 
                    capture_output=True,check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                return build_response(
                    tool="run_in_container",
                    input_data={"container_name": container_name, "command": command},
                    stdout=result.stdout or '',
                    exit_code=0
                )
            except subprocess.CalledProcessError as e:
                return build_response(
                    tool="run_in_container",
                    input_data={"container_name": container_name, "command": command},
                    stderr=f"Error running command in container '{container_name}': {e.stderr or ''}",
                    exit_code=e.returncode
                )
        return self.failed_sanity_check_response
