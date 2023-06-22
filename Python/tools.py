import json
import openai
from datetime import datetime


# gpt-3.5-turbo 4k context
MODEL_3_4K = "gpt-3.5-turbo-0613"
INPUT_COST_P_1000 = 0.0015
OUTPUT_COST_P_1000 = 0.002
CONTEXT_THRESHOLD = 4000

# gpt-3.5-turbo 16k context
MODEL_3_16K = "gpt-3.5-turbo-16k"
INPUT_COST_P_1000_16K = 0.003
OUTPUT_COST_P_1000_16K = 0.004

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


def chat_completion(messages: list, function = None, description = "", model = MODEL_3_4K) -> dict:
    """
    completes the chat
    :param messages: messages list of openai format
    :param max_tokens: max tokens to be used for completion
    :param stop: stop list of openai format
    """

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

    if usage["total_tokens"] > CONTEXT_THRESHOLD:
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

    request_log.append(usage)
    

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