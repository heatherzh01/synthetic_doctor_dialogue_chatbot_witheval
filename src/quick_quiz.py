import numpy as np
import json
from prompts.quick_quiz_prompt import quick_quiz_prompt
from src.llm_inference import gpt_query

class Quiz(object):
    def __init__(self,
                 questions_list=None,
                 product='司美格鲁肽注射液(诺和泰)',
                 llm='gpt-4-0125-preview', llm_params={}):
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.questions_list = questions_list
        self.product = product
        self.llm = llm
        self.llm_params = llm_params
        self.sel_question = None
        self.result = []

    def get_question(self, index=None):
        if index is None:
            self.sel_question = np.random.choice(self.questions_list)
        else:
            self.sel_question = self.questions_list[index]

    def evaluate_question(self, question=None, key_points=None, user_answer=None):
        prompt = quick_quiz_prompt.format(
            question=question,
            key_points=key_points,
            user_answer=user_answer
            # comparison_result = [None] * len(self.sel_question.key_points)
        )
        response, cost = gpt_query([{'role': 'user', 'content': prompt}], self.llm,
                                   **self.llm_params)
        res = response.choices[0].message.content
        if res.startswith("```json"):
            ans = json.loads(res.strip("```json").strip("```").strip())
        else:
            ans = json.loads(res)
        weight_score = "得分为： " + format(sum(ans) / len(ans), ".2f")
        self.result.append({
            'question': question,
            'user_answer': user_answer,
            'evaluation': weight_score,
            'hit_key_points': [key_points.split('|')[idx] for idx, x in enumerate(ans) if x == 1],
            'missed_key_points': [key_points.split('|')[idx] for idx, x in enumerate(ans) if x == 0]
        })

    def evaluate(self, user_answer):
        print(self.sel_question)
        prompt = quick_quiz_prompt.format(
            question=self.sel_question.question,
            key_points=self.sel_question.key_points,
            user_answer=user_answer
            # comparison_result = [None] * len(self.sel_question.key_points)
        )
        response, cost = gpt_query([{'role': 'user', 'content': prompt}], self.llm,
                                   **self.llm_params)
        res = response.choices[0].message.content
        if res.startswith("```json"):
            ans = json.loads(res.strip("```json").strip("```").strip())
        else:
            ans = json.loads(res)
        weight_score = "得分为： "+format(sum(ans)/len(ans), ".2f")
        self.result.append({
            'question': self.sel_question,
            'user_answer': user_answer,
            'evaluation': weight_score,
            'hit_key_points': [self.sel_question.key_points[idx] for idx, x in enumerate(ans) if x == 1],
            'missed_key_points': [self.sel_question.key_points[idx] for idx, x in enumerate(ans) if x == 0]
        })
