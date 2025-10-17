from src.llm_init import init_openai, init_azure
import time
import json
import re


def gpt_query(messages, model, **args):
    client = init_openai()
    now = time.time()
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=args.get('temperature', 0),
        max_tokens=args.get('max_tokens', 4095),
        top_p=args.get('top_p', 0),
        frequency_penalty=args.get('frequency_penalty', 0),
        presence_penalty=args.get('presence_penalty', 0),
        seed=args.get('seed', 1000),
        tools=args.get('tools', None),
        tool_choice=args.get('tool_choice', None),
    )
    cost = {
        'time': time.time() - now,
        'prompt_tokens': response.usage.prompt_tokens,
        'completion_tokens': response.usage.completion_tokens
    }
    return response, cost


def gpt_query_stream(messages, model, **args):
    client = init_openai()
    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=args.get('temperature', 0),
        max_tokens=args.get('max_tokens', 4095),
        top_p=args.get('top_p', 0),
        frequency_penalty=args.get('frequency_penalty', 0),
        presence_penalty=args.get('presence_penalty', 0),
        seed=args.get('seed', 1000),
        stream=True
    )
    return stream


def get_embedding(text, model='text-embedding-3-large'):
    client = init_openai()
    return client.embeddings.create(input=[text], model=model).data[0].embedding


def clean_gpt_answers(res: str) -> (dict, str, int):
    """

    :param res:
    :return:
    """

    res_full = res[0].choices[0].message.content

    # 去除不想要的除JSON以外的内容
    res_comment = re.findall(r"\/\/([^\/\n]+)\n", res_full)
    for c in res_comment:
        res_full = res_full.replace(c, "")

    res_full = res_full.replace("//", "")
    res_full = res_full.replace("output:", "")

    if '```json' in res_full:
        res_str_list = re.findall(r"```json([^\`]+)```", res_full)
    else:
        res_str_list = [res_full]

    # 转换成JSON格式
    is_successful = 0
    if len(res_str_list) > 0:
        res_str = res_str_list[0]
        try:
            res_dict = json.loads(res_str)
            is_successful = 1
        except:
            res_dict = {}
    else:
        res_dict = {}
        res_str = res_full

    return res_dict, res_str, is_successful
