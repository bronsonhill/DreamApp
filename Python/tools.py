import json
from os.path import isfile
import openai
from datetime import datetime


# gpt-3.5-turbo 4k context
MODEL_3_4K = "gpt-3.5-turbo-0613"
INPUT_COST_P_1000 = 0.0015
OUTPUT_COST_P_1000 = 0.002
MODEL_THRESHOLD = 4000
EXPECTED_COMPLETION_TOKENS = 1200

# gpt-3.5-turbo 16k context
MODEL_3_16K = "gpt-3.5-turbo-16k"
INPUT_COST_P_1000_16K = 0.003
OUTPUT_COST_P_1000_16K = 0.004

LINE_BREAK = "--------------------------------------------------------------"

# gpt-4 8k context
# MODEL = "gpt-4"
# INPUT_COST_P_1000 = 0.03
# OUTPUT_COST_P_1000 = 0.06

# gpt-4 32k context
# MODEL = "gpt-4"
# INPUT_COST_P_1000 = 0.06
# OUTPUT_COST_P_1000 = 0.12

USER_ROLE = "user"
AI_ROLE = "assistant"


# open key.txt and save the key
with open("../key.txt", "r") as fp:
    key = fp.read()

# open messages.txt and save the messages
with open("Python/data/messages.json", "r") as fp:
    messages = json.load(fp)



openai.api_key = key
requests = []


def log_dream_data(data, filename: str):
    """
    logs data
    """
    dir = "Python/data/"+filename
    with open(dir, "r") as fp:
        load = json.load(fp)

    load[""] = data

    with open(dir, "w") as fp:
        json.dump(load, fp, indent=4)

    return


def chat_completion(messages: list, function = None, description = "", model = None, expected_length=EXPECTED_COMPLETION_TOKENS) -> dict:
    """
    completes the chat
    :param messages: messages list of openai format
    :param max_tokens: max tokens to be used for completion
    :param stop: stop list of openai format
    """
    if model is None:
        model = get_model(messages, expected_length)

    if not function:
    
        completion = openai.ChatCompletion.create(
            model=model,
            messages=messages,
        )

        print(completion["choices"][0]["message"]["content"])

        return (completion["choices"][0]["message"]["content"], 
            cost_calculation(completion["usage"], description))
    
    else:
        completion = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            functions=[function],
            function_call="auto"
        )

        return (json.loads(completion["choices"][0]["message"].to_dict()["function_call"]["arguments"]),
                cost_calculation(completion["usage"], description))


def append_message(messages: list, content: str, role: str):
    """
    appends message to messages list
    :param messages: messages list of openai format
    :param message: a message of string format
    :param role: ie. assistant or user
    """

    messages.append(
        {
        "role": role,
        "content": content
        }
    )

    return


def cost_calculation(usage: dict, description: str) -> float:
    """
    calculates the cost of the request
    :param usage: usage dict of openai format
    """

    if usage["total_tokens"] > MODEL_THRESHOLD:
        output_cost = OUTPUT_COST_P_1000_16K
        input_cost = INPUT_COST_P_1000_16K
    else: 
        output_cost = OUTPUT_COST_P_1000
        input_cost = INPUT_COST_P_1000

    usage["completion_cost"] = usage["completion_tokens"] * output_cost / 1000
    usage["prompt_cost"] = usage["prompt_tokens"] * input_cost / 1000
    usage["cost"] = usage["completion_cost"] + usage["prompt_cost"]
    usage["datetime"] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    usage["description"] = description

    requests.append(usage)
    

    return usage["cost"]


def log_requests():
    """
    logs requests and prints details
    """

    print("Total requests: ", len(requests))
    print("Total cost: $", sum([request["cost"] for request in requests]))
    print("Total completion tokens: ", sum([request["completion_tokens"] 
                                            for request in requests]))
    print("Total prompt tokens: ", sum([request["prompt_tokens"] 
                                        for request in requests]))
    

    with open("Python/data/request_log.json", "r") as fp:
        load = json.load(fp)
        
    load += requests

    json.dump(load, open("Python/data/request_log.json", "w"), indent=4)


    return


def dict_to_str(dict: dict) -> str:
    """
    converts dict to str
    """
    str = ""
    for key, value in dict.items():
        str += key + ": " + value + "\n\n"

    return str


def get_model(messages: list, expected_completion_tokens = EXPECTED_COMPLETION_TOKENS):
    """
    estimates tokens
    """
    estimate = 0

    for message in messages:
        estimate += len(message["content"].split(" "))
    
    print("Estimated tokens: ", estimate)

    # model threshold by two to leave tokens for the completion
    if estimate < (MODEL_THRESHOLD - expected_completion_tokens):
        print("Using ", MODEL_3_4K)
        return MODEL_3_4K
    else:
        print("Using ", MODEL_3_16K)
        return MODEL_3_16K
    
    return


def dream_to_txt(dream: dict, depth = 0) -> str:
    """
    converts dream to txt. Recurses when value is of type dict
    """
    txt = ""
    if type(dream) == dict:
        for key, value in dream.items():
            txt += key + ":\n" + dream_to_txt(value, depth+1)
    elif type(dream) == list:
        for item in dream:
            txt += dream_to_txt(item, depth) + "\n"
    else:
        txt += dream + "\n"

    if depth == 0:
        # tests if file already exists with os.path.isfile
        if not isfile("output.txt"):
            with open("output.txt", "w") as fp:
                fp.write(txt)
        else:
            print("Error. Filename already exists")


    return txt


def dream_to_md(dream, depth = 1):
    """
    converts dream to md
    """
    header = "#" * depth + " "
    txt = ""
    if type(dream) == dict:
        for key, value in dream.items():
            txt += header + key + ":\n" + dream_to_md(value, depth+1)
    elif type(dream) == list:
        for item in dream:
            txt += dream_to_md(item, depth) + "\n"
    else:
        txt += dream + "\n"

    if depth == 1:
        # tests if file already exists with os.path.isfile
        if not isfile("output.md"):
            with open("output.md", "w") as fp:
                fp.write(txt)
        else:
            print("Error. Filename already exists")


    return

