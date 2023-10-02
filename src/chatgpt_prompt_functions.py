import ast
import time

MAX_RETRIES = 3
RETRY_DELAY = 5  # in seconds

def create_related_concepts(openai, concept, nro):
    text = 'Return a python array that contains ' + str(nro) + ' concepts related to """' + concept + '""" Just return the array, do now write anything else.' 

    message_log = [
    {"role": "system", "content": text}
    ]
    response_content = chat_completion_create(openai, message_log)

    return eval(response_content.lower())



def create_definition(openai, concept, nro_words):
    text = 'Return a python string array that explains: """' + concept + '""" in ' + str(nro_words) + ' words' 
    message_log = [
    {"role": "system", "content": text}
    ]
    response_content = chat_completion_create(openai, message_log)

    return response_content




def sort_concepts_along_dimension(openai, concept_array, dimension):
    for _ in range(MAX_RETRIES + 1):
        text = 'Sort these concepts """' + str(concept_array) + '""" from ' + str(dimension[0]) + ' to ' + str(dimension[1]) + ' Return a python array that contains the sorted concepts, do now write anything else.'

        message_log = [
            {"role": "system", "content": text}
        ]

        response_content = chat_completion_create(openai, message_log)

        if is_valid_array_expression(response_content):
            return eval(response_content)
        else:
            print("Invalid or unsafe Python array expression in the response. Retrying...")
            print(concept_array)
            print(response_content)
            time.sleep(RETRY_DELAY)
    
    print("Failed after maximum retries. Returning an empty array.")
    return []






def is_valid_array_expression(expr):
    try:
        parsed_expr = ast.parse(expr, mode='eval')
        return isinstance(parsed_expr.body, ast.List)
    except SyntaxError:
        return False
    
def chat_completion_create(openai, message_log):
    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",  # The name of the OpenAI chatbot model to use
    messages=message_log,   # The conversation history up to this point, as a list of dictionaries
    max_tokens=980,        # The maximum number of tokens (words or subwords) in the generated response
    stop=None,              # The stopping sequence for the generated response, if any (not used here)
    temperature=0.0,        # The "creativity" of the generated response (higher temperature = more creative)
    )
    return response.choices[0].message.content