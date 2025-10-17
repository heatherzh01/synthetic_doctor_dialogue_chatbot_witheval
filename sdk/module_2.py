from src.session import Session
from src.session_monitor import Monitor
from src.static_classes import ObjectionInstance
import json
from sdk.input_mapper import *


class Module_2(object):
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
            clarifyCriterion:
                dimensions
                    process
                    skills
                    correctness
                definitions
                    process
                    skills
                few_shots_examples
                    process
                    skills
            takeActionCriterion:
                dimensions
                    process
                    skills
                    correctness
                definitions
                    process
                    skills
                    correctness
                few_shots_examples
                    process
                    skills
            sessionStatus:
                chatHistory                     # 聊天记录
                monitorRes:                     # 监视器监控结果
                    cNumQueries                 # int 澄清阶段 - 提问数量
                    cQuerySeq                   # list[str] 澄清阶段 - 每一次提问原文
                    cProcessSeq                 # list[enum('询问指向','询问来源','询问治疗理念','询问治疗经验','无关询问')] 澄清阶段 - 每一次提问被分类的流程类型
                    cSkillsSeq                  # list[dict{'从关心患者/医生角度出发来设计提问':int,'提问有逻辑性':int,'询问客户关心的并聚焦的异议相关问题':int,'澄清和追问细节':int}] 澄清阶段 - 每一次提问被分类的四个技巧维度打分
                    tNumQueries                 # int 解决阶段 - 输入数量
                    tQuerySeq                   # list[str] 解决阶段 - 每一次输入原文
                    tProcessSeq                 # list[enum("提供证据","传达FB","传达整体优势及利益","传达专家建议和经验案例",'无关询问')] 解决阶段 - 每一次输入被分类的流程类型
                    tSkillsSeq                  # list[dict{'围绕关键信息传递FB':int,'逻辑清晰':int,'语言表达清晰流畅':int}] 澄清阶段 - 每一次提问被分类的三个技巧维度打分
                    tQueryInStandardAnswerSeq   # list(enum('是','否')) 解决阶段 - 每一次输入传达的知识是否在标准回答以内
                repName
                startTime
                stage
        :return:
            sessionStatus:
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
                stage
        '''

        input_json = json.loads(input)

        # 组装objection
        objection = ObjectionInstance(
            preset_objection=input_json['objection']['presetObjection'],
            real_objection=input_json['objection']['realObjection'],
            clarify_type=ObjectionClarifyTypeEnumMapper[input_json['objection']['clarifyType']],
            take_action_type=ObjectionTakeActionTypeEnumMapper[input_json['objection']['takeActionType']],
            visible_background=input_json['objection']['visibleBackground'],
            invisible_background=input_json['objection']['invisibleBackground'],
            standard_answer=input_json['objection']['standardAnswer']
        )

        # 组装criterion
        clarify_criterion = input_json['clarifyCriterion']
        take_action_criterion = input_json['takeActionCriterion']

        # 组装monitor
        session_monitor = Monitor(
            product=input_json['product']['productName'],
            clarify_criterion=clarify_criterion,
            take_action_criterion=take_action_criterion
        )
        session_monitor.set_objection(objection)
        session_monitor.c_num_queries = input_json['sessionStatus']['monitorRes']['cNumQueries']
        session_monitor.c_query_seq = input_json['sessionStatus']['monitorRes']['cQuerySeq']
        session_monitor.c_process_seq = input_json['sessionStatus']['monitorRes']['cProcessSeq']
        session_monitor.c_skills_seq = input_json['sessionStatus']['monitorRes']['cSkillsSeq']
        session_monitor.t_num_queries = input_json['sessionStatus']['monitorRes']['tNumQueries']
        session_monitor.t_query_seq = input_json['sessionStatus']['monitorRes']['tQuerySeq']
        session_monitor.t_process_seq = input_json['sessionStatus']['monitorRes']['tProcessSeq']
        session_monitor.t_skills_seq = input_json['sessionStatus']['monitorRes']['tSkillsSeq']
        session_monitor.t_query_in_standard_answer_seq = input_json['sessionStatus']['monitorRes']['tQueryInStandardAnswerSeq']

        # 监控
        if input_json['sessionStatus']['stage'] == 'CLARIFY':
            # 澄清阶段
            stage = 'CLARIFY'
            _, _, is_confirmation = session_monitor.c_process(
                input_json['sessionStatus']['chatHistory'],
                input_json['repInput']
            )
            session_monitor.c_skills(
                input_json['sessionStatus']['chatHistory'],
                input_json['repInput']
            )
            if is_confirmation == '是':
                stage = 'TAKEACTION'
            print(json.dumps({
                'status': 0,
                'content': {
                    'sessionStatus': {
                        'stage': stage,
                        'is_confirmation': is_confirmation,
                        'monitorRes': {
                            'cNumQueries': session_monitor.c_num_queries,
                            'cQuerySeq': session_monitor.c_query_seq,
                            'cProcessSeq': session_monitor.c_process_seq,
                            'cSkillsSeq': session_monitor.c_skills_seq,
                            'tNumQueries': session_monitor.t_num_queries,
                            'tQuerySeq': session_monitor.t_query_seq,
                            'tProcessSeq': session_monitor.t_process_seq,
                            'tSkillsSeq': session_monitor.t_skills_seq,
                            'tQueryInStandardAnswerSeq': session_monitor.t_query_in_standard_answer_seq
                        }
                    }
                },
                'index': -1
            }, ensure_ascii=False))
        else:
            # 解决阶段
            stage = 'TAKEACTION'
            _, _, is_confirmation = session_monitor.t_process(
                input_json['sessionStatus']['chatHistory'],
                input_json['repInput']
            )
            session_monitor.t_skills(
                input_json['sessionStatus']['chatHistory'],
                input_json['repInput']
            )
            print(json.dumps({
                'status': 0,
                'content': {
                    'sessionStatus': {
                        'stage': stage,
                        'is_confirmation': is_confirmation,
                        'monitorRes': {
                            'cNumQueries': session_monitor.c_num_queries,
                            'cQuerySeq': session_monitor.c_query_seq,
                            'cProcessSeq': session_monitor.c_process_seq,
                            'cSkillsSeq': session_monitor.c_skills_seq,
                            'tNumQueries': session_monitor.t_num_queries,
                            'tQuerySeq': session_monitor.t_query_seq,
                            'tProcessSeq': session_monitor.t_process_seq,
                            'tSkillsSeq': session_monitor.t_skills_seq,
                            'tQueryInStandardAnswerSeq': session_monitor.t_query_in_standard_answer_seq
                        }
                    }
                },
                'index': -1
            }, ensure_ascii=False))