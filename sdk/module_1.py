from src.session import Session
from src.static_classes import ObjectionInstance
from src.utils.io import load_hcp_from_dict
import json
from sdk.input_mapper import *


class Module_1(object):
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
                monitorRes
                repName
                startTime
                stage
        :return:
            sessionStatus:
                chatHistory
        '''

        input_json = json.loads(input)

        # 组装hcp
        hcp_attr = {
            'hcp_name': input_json['hcp']['hcpName'],
            'hcp_gender': HcpGenderEnum[input_json['hcp']['hcpGender']],
            'hsp_tier_1': HspTier1EnumMapper[input_json['hcp']['hspTier'].split('_')[0]],
            'hsp_tier_2': HspTier2EnumMapper[input_json['hcp']['hspTier'].split('_')[1]],
            'hcp_position': HcpPositionEnumMapper[input_json['hcp']['hcpPosition']],
            'hcp_personality': HcpPersonalityEnum[input_json['hcp']['hcpPersonality']]
        }
        hcp = load_hcp_from_dict(**hcp_attr)
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
        # 组装session
        session = Session(
            hcp=hcp,
            objection=objection,
            res_style='混合模式',
            use_dept_knowledge=False,
            use_product_knowledge=True,
            monitor=False,                                                       # 无论是练习还是测试模式都需要跑
            product=input_json['product']['productName'],
            llm='gpt-4-0125-preview',
            llm_params={},
            rep=input_json['sessionStatus']['repName'],
            prompt_tokens=input_json['sessionStatus']['promptTokens'],
            completion_tokens=input_json['sessionStatus']['completionTokens'],
            start_time=input_json['sessionStatus']['startTime'],
            stage=input_json['sessionStatus']['stage'],
            chat_history=input_json['sessionStatus']['chatHistory']
        )
        # 生成回复
        try:
            res = session.chat_stream(input_json['repInput'])
            index = 0
            for stream in res:
                print(json.dumps({'status': 1, 'content': stream, 'index': index}, ensure_ascii=False))
                index += 1
            print(json.dumps({'status': 0, 'content': session.chat_history, 'index': -1}, ensure_ascii=False))
        except Exception as e:
            print(e)
            raise SystemExit(json.dumps({'status': -1, 'content': e, 'index': -1}, ensure_ascii=False))
