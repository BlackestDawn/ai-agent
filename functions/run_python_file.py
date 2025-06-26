import os
import subprocess
from google.genai import types


def run_python_file(working_directory, file_path, args=None):
    abs_working_directory = os.path.abspath(working_directory)
    if not file_path.startswith('/'):
        abs_file_path = os.path.abspath(os.path.join(abs_working_directory, file_path))
    else:
        abs_file_path = os.path.abspath(file_path)

    if not abs_file_path.startswith(abs_working_directory):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

    if not os.path.exists(abs_file_path):
        return f'Error: File "{file_path}" not found.'

    if not os.path.isfile(abs_file_path) or not file_path.endswith('.py'):
        return f'Error: "{file_path}" is not a Python file.'

    try:
        run_args = ['python', abs_file_path]
        if args is not None:
            run_args.extend(args)

        result = subprocess.run(run_args, capture_output=True, text=True, timeout=30, cwd=working_directory)
        if result.stdout is None or len(result.stdout) == 0:
            return "no output produced"

        output = f'Running Python file "{file_path}":\n\nSTDOUT: {result.stdout}\nSTDERR: {result.stderr}'
        if result.returncode != 0:
            output += f'\nProcess exited with code {result.returncode}'

        return output

    except Exception as e:
        return f'Error: executing Python file: {e}'


schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Runs a Python file within the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The Python file to run, relative to the working directory.",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(
                    type=types.Type.STRING,
                    description="Optional arguments to pass to the Python file. If not provided should be ommited.",
                ),
            ),
        },
        required=[
            "file_path"
        ],
    ),
)
