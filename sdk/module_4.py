
from src.static_classes import QuickQuestion
from src.quick_quiz import Quiz
import json
from sdk.input_mapper import *


class Module_4(object):
    def __init__(self):
        pass

    def get_response(self, input):
        '''
        :param input: Session Instance
            repInput:
            product:
                productName
                productDesc
            question:
            keyPoints:
        :return:
            trueOrFalseList
        '''

        input_json = json.loads(input)

        quiz = Quiz(
            questions_list=None,
            product=input_json['product']['productName'],
            llm='gpt-4-0125-preview',
            llm_params={}
        )
        quiz.evaluate_question(input_json['question'], input_json['keyPoints'], input_json['repInput'])
        #quiz.result['question'] = input_json['question']

        print(json.dumps({
            'status': 0,
            'content': quiz.result
        }, ensure_ascii=False))
