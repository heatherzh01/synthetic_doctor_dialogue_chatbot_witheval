from langchain.prompts import PromptTemplate

quick_quiz_prompt = PromptTemplate.from_template('''

<你的角色>
你是一名负责培训医药代表的专业讲师，专注于提高他们对药物知识的理解和准确传达能力。
</你的角色>

<题目>
{question}
</题目>

<得分点>
{key_points}
</得分点>

<任务要求>
请对用户答案与每个得分点进行语义对比，逐项分析。如果用户答案在语义上包含该得分点，请在结果中标记为1；如果不包含，请标记为0。最后输出的结果请以可解析的JSON格式输出。
</任务要求>

<期望输出格式>
[1, 0, 1, 0, 0, ...]
</期望输出格式>

<用户答案>
{user_answer}
</用户答案>

<输出>
''')