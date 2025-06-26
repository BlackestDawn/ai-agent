import os
from google.genai import types
from config import max_content_size


def get_file_content(working_directory, file_path):
    abs_working_directory = os.path.abspath(working_directory)
    if not file_path.startswith('/'):
        abs_file_path = os.path.abspath(os.path.join(abs_working_directory, file_path))
    else:
        abs_file_path = os.path.abspath(file_path)

    try:
        if not abs_file_path.startswith(abs_working_directory):
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

        if not os.path.isfile(abs_file_path):
            return f'Error: File not found or is not a regular file: "{file_path}"'

        with open(abs_file_path, 'r') as file:
            content = file.read(max_content_size)
            if os.path.getsize(abs_file_path) > max_content_size:
                content += f'[...File "{file_path}" truncated at {max_content_size} characters]'
            return content
    except Exception as e:
        return f'Error reading file: {e}'


schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Reads and returns the contents of a file up to 10000 characters within the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file to show the contents of, relative to the working directory.",
            ),
        },
        required=[
            "file_path"
        ],
    ),
)
