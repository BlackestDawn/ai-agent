import os


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
            content = file.read(10001)
            if len(content) <= 10000:
                return content
            else:
                return content[:10000] + f'[...File "{file_path}" truncated at 10000 characters]'
    except Exception as e:
        return f'Error: {e}'
