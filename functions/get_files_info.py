import os
from google.genai import types


def get_files_info(working_directory, directory=None):
    abs_working_directory = os.path.abspath(working_directory)
    if directory is not None:
        if not directory.startswith('/'):
            abs_directory = os.path.abspath(os.path.join(abs_working_directory, directory))
        else:
            abs_directory = os.path.abspath(directory)
    else:
        abs_directory = abs_working_directory

    try:
        if not abs_directory.startswith(abs_working_directory):
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

        if not os.path.isdir(abs_directory):
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

        dir_entries = os.listdir(abs_directory)
        result = []
        for entry in dir_entries:
            result.append(f'{entry}: {os.path.getsize(os.path.join(abs_directory, entry))} bytes, is_dir={os.path.isdir(os.path.join(abs_directory, entry))}')
    except Exception as e:
        return f'Error listing files: {e}'

    return '\n'.join(result)


schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)
