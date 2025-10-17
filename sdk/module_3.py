from src.session import Session
from src.session_monitor import Monitor
from src.session_evaluator import Evaluator
from src.static_classes import ObjectionInstance
import json
from sdk.input_mapper import *


class Module_3(object):
    def __init__(self):
        pass

    def get_response(self, input):
        '''
        :param input: Session Instance
            repInput:
            product:
                productName
                productDesc
            hcp:
                hcpName
                hcpGender
                hspTier
                hcpPosition
                hcpPersonality
            objection:
                presetObjection
                realObjection
                clarifyType
                takeActionType
                visibleBackground
                invisibleBackground
                standardAnswer
            sessionStatus:
                chatHistory
                monitorRes:
                    cNumQueries
                    cQuerySeq
                    cProcessSeq
                    cSkillsSeq
                    tNumQueries
                    tQuerySeq
                    tProcessSeq
                    tSkillsSeq
                    tQueryInStandardAnswerSeq
                repName
                startTime
                stage
        :return:
            evalRes:
                evalResClarify:
                    correctness
                    process
                    skills
                evalResTakeAction:
                    correctness
                    process
                    skills
        '''

        input_json = json.loads(input)

        # 组装evaluater
        session_evaluator = Evaluator(
            product_name=input_json['product']['productName']
        )
        # session_evaluator.set_session(input_json['chat_history_file'])
        
        file_path = input_json['chat_history_file']
        # file_path = "../output/chat_history/Edgar Cao_陈_SGLT-2i和诺和泰都是有心血管获益的药物_None"
        try:
            with open(file_path, 'rb') as file:
                session_evaluator.set_session(file)
        except FileNotFoundError:
            return json.dumps({
                'status': 1,
                'error': 'Chat history file not found.'
            }, ensure_ascii=False)
        session_evaluator.evaluate_clarify_skills()
        session_evaluator.evaluate_clarify_skills_logic()
        session_evaluator.evaluate_clarify_correctness()
        session_evaluator.evaluate_clarify_process()
        session_evaluator.evaluate_take_action_skills()
        session_evaluator.evaluate_take_action_correctness()
        session_evaluator.evaluate_take_action_process()
        
        evaluation_results = {
            'clarify_scores': session_evaluator.clarify_score,
            'take_action_scores': session_evaluator.take_action_score
        }
        
        print(json.dumps({
            'status': 0,
            'content': evaluation_results
        }, ensure_ascii=False))
