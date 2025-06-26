import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from config import system_prompt, ai_model, max_iters
from call_function import call_function, available_functions


def main():
    verbose = "--verbose" in sys.argv
    args = [arg for arg in sys.argv[1:] if not arg.startswith("--")]

    if not args:
        print("Please supply a prompt.")
        sys.exit(1)

    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    prompt = " ".join(args)
    messages = [
        types.Content(role="user", parts=[types.Part(text=prompt)]),
    ]

    iters = 0
    while True:
        iters += 1
        if iters > max_iters:
            print(messages[2].parts[0])
            print("Maximum iterations reached")
            sys.exit(1)

        try:
            response = generate_content(client, messages, verbose)
            if response:
                print("Final response:")
                print(response)
                break
        except Exception as e:
            print(f"Error in generated content: {e}")


def generate_content(client, messages, verbose):
    response = client.models.generate_content(
        model=ai_model,
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions],
            system_instruction=system_prompt),
    )

    if verbose:
        print("Prompt tokens:", response.usage_metadata.prompt_token_count)
        print("Response tokens:", response.usage_metadata.candidates_token_count)

    if not response.function_calls:
        return response.text

    for candidate in response.candidates:
        messages.append(candidate.content)

    function_responses = []
    for function_call in response.function_calls:
        function_call_result = call_function(function_call, verbose)
        if (
            not function_call_result.parts
            or not function_call_result.parts[0].function_response
        ):
            raise Exception("empty function call result")
        if verbose:
            print(f" -> {function_call_result.parts[0].function_response.response}")
        function_responses.append(function_call_result.parts[0])

    if not function_responses:
        raise Exception("no function responses generated, exiting")

    messages.append(types.Content(role="tool", parts=function_responses))


if __name__ == "__main__":
    main()
