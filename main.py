import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.write_file import write_file
from functions.run_python_file import run_python_file


def main():
    verbose = "--verbose" in sys.argv
    args = [arg for arg in sys.argv[1:] if not arg.startswith("--")]

    if not args:
        print("Please supply a prompt.")
        sys.exit(1)

    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    ai_model = "gemini-2.0-flash-001"
    prompt = " ".join(args)
    messages = [
        types.Content(role="user", parts=[types.Part(text=prompt)]),
    ]

    system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""

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
    schema_get_file_content = types.FunctionDeclaration(
        name="get_file_content",
        description="Shows the contents of a file up to 10000 characters, constrained to the working directory.",
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
    schema_run_python_file = types.FunctionDeclaration(
        name="run_python_file",
        description="Runs a Python file, constrained to the working directory.",
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
    schema_write_file = types.FunctionDeclaration(
        name="write_file",
        description="Writes new contents to a file replacing any existing contents, constrained to the working directory.",
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

    available_functions = types.Tool(
        function_declarations=[
            schema_get_files_info,
            schema_get_file_content,
            schema_run_python_file,
            schema_write_file,
        ]
    )

    response = client.models.generate_content(
        model=ai_model,
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions],
            system_instruction=system_prompt),
    )

    if response.function_calls is not None and len(response.function_calls) > 0:
        for function_call in response.function_calls:
            print(call_function(function_call, verbose=verbose))
    else:
        print(response.text)

    if verbose:
        print("User prompt:", prompt)
        print("Prompt tokens:", response.usage_metadata.prompt_token_count)
        print("Response tokens:", response.usage_metadata.candidates_token_count)


def call_function(function_call_part, verbose=False):
    if verbose:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}")

    function_args = {"working_directory": "./calculator"}
    if function_call_part.args is not None and len(function_call_part.args) > 0:
        function_args.update(function_call_part.args)

    function_name = function_call_part.name
    match function_name:
        case "get_files_info":
            return get_files_info(**function_args)
        case "get_file_content":
            return get_file_content(**function_args)
        case "run_python_file":
            return run_python_file(**function_args)
        case "write_file":
            return write_file(**function_args)
        case _:
            return types.Content(
                role="tool",
                parts=[
                    types.Part.from_function_response(
                        name=function_name,
                        response={"error": f"Unknown function: {function_name}"},
                    )
                ],
            )


if __name__ == "__main__":
    main()
