import json
from collections import Counter
from src.llm_inference import gpt_query
from prompts.monitor_prompt import clarify_process_schema, clarify_process_prompt
from prompts.monitor_prompt import take_action_process_schema, take_action_process_prompt
from prompts.monitor_prompt import clarify_skills_schema, clarify_skills_prompt
from prompts.monitor_prompt import take_action_skills_schema, take_action_skills_prompt
from src.utils.io import load_evaluation_criterion_from_yaml


class Monitor(object):
    def __init__(
            self,
            product='司美格鲁肽注射液(诺和泰)',
            llm='gpt-4-0125-preview',
            llm_params={},
            clarify_criterion=None,
            take_action_criterion=None
    ):
        self.product = product
        self.llm = llm
        self.llm_params = llm_params
        self.clarify_criterion = clarify_criterion
        self.take_action_criterion = take_action_criterion

        self.c_num_queries = 0
        self.t_num_queries = 0

        self.c_process_seq = []
        self.t_process_seq = []
        self.c_skills_seq = []
        self.t_skills_seq = []
        self.c_query_seq = []
        self.t_query_seq = []
        self.t_query_in_standard_answer_seq = []
        self.label_list = self.clarify_criterion['dimensions']['process'] + ['无关询问']
        self.label_list_t = self.take_action_criterion['dimensions']['process'] + ["无关内容"]
        self.objection = None
        self.is_confirmed = False
        self.confirming_query = None

    def set_objection(self, objection):
        self.objection = objection

    def c_process(self, chat_history, input):
        self.c_num_queries += 1
        # 判断现在的问题是哪个流程模块
        tool = {
            "type": "function",
            "function": {
                "name": "clarify_process",
                "description": '''请将给定输入根据语义，分类到对应的询问流程中，如果不属于["询问指向","询问来源","询问治疗理念","询问治疗经验"]中的任何一项，则输出"无关询问"。
                               Classify which inquiry process category for a given text''',
                "parameters": clarify_process_schema
            }
        }
        self.llm_params['tools'] = [tool]
        self.llm_params['tool_choice'] = tool
        prompt = clarify_process_prompt.format(
            product=self.product,
            definition=json.dumps(
                self.clarify_criterion['definitions']['process'],
                indent=4,
                ensure_ascii=False
            ),
            few_shots_examples=json.dumps(
                self.clarify_criterion['few_shots_examples']['process'],
                indent=4,
                ensure_ascii=False
            ),
            chat_history=chat_history,
            input=input,
            real_objection=self.objection.real_objection
        )
        res, cost = gpt_query([{'role': 'user', 'content': prompt}], self.llm, **self.llm_params)
        res = res.choices[0].message.tool_calls[0].function.arguments

        stage_type = json.loads(res)['stage_type']
        process_type = json.loads(res)['process_type']
        is_confirmation = json.loads(res)['is_confirmation']
        if is_confirmation != '是':
            self.c_process_seq.append(process_type)
            self.c_query_seq.append(input)
        else:
            self.confirming_query = input
        return stage_type, process_type, is_confirmation

    def t_process(self, chat_history, input):
        tool = {
            "type": "function",
            "function": {
                "name": "take_action_process",
                "description": '''请将给定输入根据语义，分类到对应的解决流程中，如果不属于["提供证据","传达FB","传达整体优势及利益","传达专家建议和经验案例"]中的任何一项，则输出"无关内容"。
                               Classify which inquiry process category for a given text''',
                "parameters": take_action_process_schema
            }
        }
        self.llm_params['tools'] = [tool]
        self.llm_params['tool_choice'] = tool
        prompt = take_action_process_prompt.format(
            product=self.product,
            definition=json.dumps(
                self.take_action_criterion['definitions']['process'],
                indent=4,
                ensure_ascii=False
            ),
            few_shots_examples=json.dumps(
                self.take_action_criterion['few_shots_examples']['process'],
                indent=4,
                ensure_ascii=False
            ),
            chat_history=chat_history,
            input=input,
            real_objection=self.objection.real_objection,
            standard_answer=json.dumps(
                self.objection.standard_answer,
                indent=4,
                ensure_ascii=False
            )
        )
        res, cost = gpt_query([{'role': 'user', 'content': prompt}], self.llm, **self.llm_params)
        res = res.choices[0].message.tool_calls[0].function.arguments
        stage_type = json.loads(res)['stage_type']
        process_type = json.loads(res)['process_type']
        is_in_standard_answer = json.loads(res)['is_in_standard_answer']
        self.t_process_seq.append(process_type)
        self.t_query_seq.append(input)
        self.t_query_in_standard_answer_seq.append(is_in_standard_answer)
        return stage_type, process_type, is_in_standard_answer

    def c_guide_process(self, stage_type, process_type, is_confirmation):
        # 若出现无关问题，则提示
        # 若累计出现无关问题达3个，则严重提示
        # 5轮若覆盖小于两个点，则提示
        # 10轮若覆盖小于三个点，则提示
        # 15轮若覆盖小于四个点，则提示
        if stage_type in ['澄清异议', '无关输入']:
            label_count = Counter(self.c_process_seq)
            label_not_touched = [x for x in self.label_list if x not in label_count and x != '无关询问']
            if is_confirmation == '是':
                self.is_confirmed = True
                output = [f"**[Hint]**", f'Monitor监控到您正在向医生确认异议，澄清阶段结束，请开始解决阶段']
                if len(label_not_touched) >= 1:
                    output.append(f'本次对话共计{self.c_num_queries}轮，您尚未询问{label_not_touched}方面，下次请加油')
                else:
                    output.append(f'本次对话共计{self.c_num_queries}轮，您询问了所有流程要点，真棒！下次请保持')
                if self.c_process_seq.count('无关询问') >= 3:
                    output.append(f'本次对话中，你曾{self.c_process_seq.count("无关询问")}次询问与{self.product}无关的问题，下次请注意避免')
            elif not self.is_confirmed:
                output = [f"**[Hint]**", f"Monitor监控到您正在{process_type}"]
                # 统计无关询问的个数
                if self.c_process_seq.count('无关询问') >= 3:
                    output.append(f'注意整个进程中，你已经{self.c_process_seq.count("无关询问")}次询问与{self.product}无关的问题，请注意避免')
                elif '无关询问' == process_type:
                    output.append(f'请尽量避免询问与{self.product}无关的问题')
                if self.c_num_queries >= 5 and len(label_not_touched) >= 3:
                    output.append(f'注意当前进程已经经过5轮对话，您尚未询问{label_not_touched}方面，请加速')
                if self.c_num_queries >= 10 and len(label_not_touched) >= 2:
                    output.append(f'注意当前进程已经经过10轮对话，您尚未询问{label_not_touched}方面，请加速')
                if self.c_num_queries >= 15 and len(label_not_touched) >= 1:
                    output.append(f'注意当前进程已经经过15轮对话，您尚未询问{label_not_touched}方面，请加速')
                output.append(f"当前是第{self.c_num_queries}轮问题，"+"您做的非常好！"*(len(output) == 2)+"请继续")
            else:
                output = [f"**[Hint]**", f"Monitor监控到您已经向医生确认异议，澄清阶段已结束，请尽快开始解决阶段"]
            output.append(f"当前对话的踩点进程为")
            output.append(label_count)
        else:
            output = [f"**[Hint]**", f'Monitor监控到您正在向医生解决异议，但澄清阶段尚未结束，请先进行异议的澄清']
        return output

    def t_guide_process(self, stage_type, process_type, is_in_standard_answer):
        label_count = Counter(self.t_process_seq)
        if stage_type in ['解决异议', '无关输入']:
            output = [f"**[Hint]**", f"Monitor监控到您正在{process_type}"]
            correct_ratio = len([1 for x in self.t_query_in_standard_answer_seq if x == '是']) / len(self.t_query_in_standard_answer_seq)
            if is_in_standard_answer == '是':
                output.append(f"您的回答在标准答案中，恭喜！当前传达信息正确率为 {correct_ratio}")
            else:
                output.append(f"您的回答不在标准答案中，当前传达信息正确率为 {correct_ratio}")
        else:
            output = [f"**[Hint]**", f"Monitor监控到您正在向医生澄清异议，但澄清阶段已经结束，请进行异议的解决"]
        output.append(f"当前对话的踩点进程为")
        output.append(label_count)
        return output

    def c_skills(self, chat_history, input):
        # 判断现在的问题是哪个流程模块
        tool = {
            "type": "function",
            "function": {
                "name": "skills_process",
                "description": f'''请根据定义为医药代表当前的问题({input})评分''',
                "parameters": clarify_skills_schema
            }
        }
        self.llm_params['tools'] = [tool]
        self.llm_params['tool_choice'] = tool
        prompt = clarify_skills_prompt.format(
            product=self.product,
            preset_objection=self.objection.preset_objection,
            real_objection=self.objection.real_objection,
            definition=json.dumps(
                self.clarify_criterion['definitions']['skills'],
                indent=4,
                ensure_ascii=False),
            few_shots_examples=json.dumps(
                self.clarify_criterion['few_shots_examples']['skills'],
                indent=4,
                ensure_ascii=False),
            chat_history=chat_history,
            input=input
        )
        res, cost = gpt_query([{'role': 'user', 'content': prompt}], self.llm, **self.llm_params)
        res = res.choices[0].message.tool_calls[0].function.arguments
        self.c_skills_seq.append(json.loads(res))

    def t_skills(self, chat_history, input):
        tool = {
            "type": "function",
            "function": {
                "name": "take_action_skills",
                "description": f'''请根据定义为医药代表当前的问题({input})评分''',
                "parameters": take_action_skills_schema
            }
        }
        self.llm_params['tools'] = [tool]
        self.llm_params['tool_choice'] = tool
        prompt = take_action_skills_prompt.format(
            product=self.product,
            preset_objection=self.objection.preset_objection,
            real_objection=self.objection.real_objection,
            definition=json.dumps(
                self.clarify_criterion['definitions']['skills'],
                indent=4,
                ensure_ascii=False),
            few_shots_examples=json.dumps(
                self.clarify_criterion['few_shots_examples']['skills'],
                indent=4,
                ensure_ascii=False),
            chat_history=chat_history,
            input=input
        )
        res, cost = gpt_query([{'role': 'user', 'content': prompt}], self.llm, **self.llm_params)
        res = res.choices[0].message.tool_calls[0].function.arguments
        self.t_skills_seq.append(json.loads(res))