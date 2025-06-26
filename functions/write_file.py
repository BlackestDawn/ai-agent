import os
from google.genai import types


def write_file(working_directory, file_path, content):
    abs_working_directory = os.path.abspath(working_directory)
    if not file_path.startswith('/'):
        abs_file_path = os.path.abspath(os.path.join(abs_working_directory, file_path))
    else:
        abs_file_path = os.path.abspath(file_path)

    try:
        if not abs_file_path.startswith(abs_working_directory):
            return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'

        if not os.path.exists(os.path.dirname(abs_file_path)):
            os.makedirs(os.path.dirname(abs_file_path))

        with open(abs_file_path, 'w') as f:
            f.write(content)

        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'

    except Exception as e:
        return f'Error writing file: {e}'


schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes contents to a file replacing any existing contents within the working directory, creates new directories if necessary.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file to write to, relative to the working directory.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The contents to write to the file.",
            ),
        },
        required=[
            "file_path",
            "content"
        ],
    ),
)
