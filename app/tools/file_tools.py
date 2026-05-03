# app/tools/file_tools.py

import os
from .base_tool import BaseTool
from app.schema.tools_response import build_response


class FileTools(BaseTool):

    failed_sanity_check_response = build_response(
        tool="file_operation",
        stderr="Error: File path failed sanity check.",
        input_data={},
        exit_code=1
    )

    def __init__(self):
        self.allowed_directory = os.path.join(os.getcwd(), "workspace")

        if not os.path.exists(self.allowed_directory):
            os.makedirs(self.allowed_directory)
            os.chmod(self.allowed_directory, 0o700)

    # =========================
    # 🔧 INTERNAL HELPERS
    # =========================

    def _resolve_path(self, path: str) -> str:
        if not os.path.isabs(path):
            path = os.path.join(self.allowed_directory, path)

        path = os.path.abspath(path)

        if not path.startswith(self.allowed_directory):
            raise ValueError("Path escapes workspace")

        return path

    # =========================
    # 📁 FILE OPERATIONS
    # =========================

    def write_to_file(self, file_path, data):
        try:
            file_path = self._resolve_path(file_path)

            with open(file_path, "w") as file:
                file.write(data)

            return build_response(
                tool="write_to_file",
                input_data={"file_path": file_path, "data": data},
                stdout=f"Data written to {file_path} successfully.",
                exit_code=0
            )

        except Exception as e:
            return build_response(
                tool="write_to_file",
                input_data={"file_path": file_path},
                stderr=str(e),
                exit_code=1,
                error_type=type(e).__name__,
                error_message=str(e)
            )

    def read_from_file(self, file_path):
        try:
            file_path = self._resolve_path(file_path)

            with open(file_path, "r") as file:
                data = file.read()

            return build_response(
                tool="read_from_file",
                input_data={"file_path": file_path},
                stdout=data,
                exit_code=0
            )

        except Exception as e:
            return build_response(
                tool="read_from_file",
                input_data={"file_path": file_path},
                stderr=str(e),
                exit_code=1,
                error_type=type(e).__name__,
                error_message=str(e)
            )

    def append_to_file(self, file_path, data):
        try:
            file_path = self._resolve_path(file_path)

            with open(file_path, "a") as file:
                file.write(data)

            return build_response(
                tool="append_to_file",
                input_data={"file_path": file_path, "data": data},
                stdout=f"Data appended to {file_path} successfully.",
                exit_code=0
            )

        except Exception as e:
            return build_response(
                tool="append_to_file",
                input_data={"file_path": file_path},
                stderr=str(e),
                exit_code=1,
                error_type=type(e).__name__,
                error_message=str(e)
            )

    def delete_file(self, file_path):
        try:
            file_path = self._resolve_path(file_path)

            if not os.path.exists(file_path):
                raise FileNotFoundError("File does not exist")

            os.remove(file_path)

            return build_response(
                tool="delete_file",
                input_data={"file_path": file_path},
                stdout=f"File {file_path} deleted successfully.",
                exit_code=0
            )

        except Exception as e:
            return build_response(
                tool="delete_file",
                input_data={"file_path": file_path},
                stderr=str(e),
                exit_code=1,
                error_type=type(e).__name__,
                error_message=str(e)
            )

    def list_files_in_directory(self, directory_path):
        try:
            directory_path = self._resolve_path(directory_path)

            if not os.path.isdir(directory_path):
                raise NotADirectoryError("Invalid directory")

            return build_response(
                tool="list_files_in_directory",
                input_data={"directory_path": directory_path},
                stdout=str(os.listdir(directory_path)),
                exit_code=0
            )

        except Exception as e:
            return build_response(
                tool="list_files_in_directory",
                input_data={"directory_path": directory_path},
                stderr=str(e),
                exit_code=1,
                error_type=type(e).__name__,
                error_message=str(e)
            )

    def create_directory(self, directory_path):
        try:
            directory_path = self._resolve_path(directory_path)

            os.makedirs(directory_path, exist_ok=True)

            return build_response(
                tool="create_directory",
                input_data={"directory_path": directory_path},
                stdout=f"Directory created at {directory_path}",
                exit_code=0
            )

        except Exception as e:
            return build_response(
                tool="create_directory",
                input_data={"directory_path": directory_path},
                stderr=str(e),
                exit_code=1,
                error_type=type(e).__name__,
                error_message=str(e)
            )

    def delete_directory(self, directory_path):
        try:
            directory_path = self._resolve_path(directory_path)

            if not os.path.isdir(directory_path):
                raise NotADirectoryError("Directory does not exist")

            os.rmdir(directory_path)

            return build_response(
                tool="delete_directory",
                input_data={"directory_path": directory_path},
                stdout=f"Directory {directory_path} deleted successfully.",
                exit_code=0
            )

        except Exception as e:
            return build_response(
                tool="delete_directory",
                input_data={"directory_path": directory_path},
                stderr=str(e),
                exit_code=1,
                error_type=type(e).__name__,
                error_message=str(e)
            )

    def copy_file(self, source_path, destination_path):
        try:
            source_path = self._resolve_path(source_path)
            destination_path = self._resolve_path(destination_path)

            if not os.path.exists(source_path):
                raise FileNotFoundError("Source file does not exist")

            with open(source_path, "r") as src:
                data = src.read()

            with open(destination_path, "w") as dst:
                dst.write(data)

            return build_response(
                tool="copy_file",
                input_data={
                    "source_path": source_path,
                    "destination_path": destination_path
                },
                stdout=f"File copied successfully",
                exit_code=0
            )

        except Exception as e:
            return build_response(
                tool="copy_file",
                input_data={
                    "source_path": source_path,
                    "destination_path": destination_path
                },
                stderr=str(e),
                exit_code=1,
                error_type=type(e).__name__,
                error_message=str(e)
            )

    def move_file(self, source_path, destination_path):
        try:
            source_path = self._resolve_path(source_path)
            destination_path = self._resolve_path(destination_path)

            os.rename(source_path, destination_path)

            return build_response(
                tool="move_file",
                input_data={
                    "source_path": source_path,
                    "destination_path": destination_path
                },
                stdout="File moved successfully",
                exit_code=0
            )

        except Exception as e:
            return build_response(
                tool="move_file",
                input_data={
                    "source_path": source_path,
                    "destination_path": destination_path
                },
                stderr=str(e),
                exit_code=1,
                error_type=type(e).__name__,
                error_message=str(e)
            )
