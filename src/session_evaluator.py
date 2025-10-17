from src.llm_inference import gpt_query
from src.session import Session
import os
import pickle
import json
from collections import Counter
from collections import defaultdict
from prompts.evaluator_prompt import clarify_skill_prompt, take_action_skill_prompt, skill_schema
from src.utils.io import load_evaluation_criterion_from_yaml


class Evaluator(object):
    def __init__(self,
                 knowledge=False,
                 product_name='司美格鲁肽注射液（诺和泰）',
                 llm='gpt-4-0125-preview',
                 llm_params={}
                 ):
        self.product_name = product_name
        self.knowledge = knowledge
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.clarify_score = {}
        self.take_action_score = {}
        self.clarify_criterion = load_evaluation_criterion_from_yaml('../data/criterions/clarify_criterion.yml')
        self.take_action_criterion = load_evaluation_criterion_from_yaml('../data/criterions/take_action_criterion.yml')
        self.session = None
        self.llm = llm
        self.llm_params = llm_params
        self.chat_history = ''

    def set_session(self, session):
        # supports Session and str type input
        if isinstance(Session, type(session)):
            self.session = session
        elif isinstance(str, type(session)):
            self.session = pickle.load(open(session, 'rb'))
        else:
            self.session = pickle.load(session)
        self.chat_history = ''
        for each in self.session.chat_history:
            if each['role'] == 'user':
                self.chat_history += f"医药代表：{each['content']}\n"
            if each['role'] == 'assistant':
                self.chat_history += f"医生：{each['content']}\n"

    def evaluate_clarify(self):
        # self.get_monitor_correctness()
        # self.get_monitor_process()
        self.evaluate_clarify_skills()
        # self.clarify_score['avg'] = sum([]+[])/len()

    def evaluate_clarify_skills(self):
        '''取平均'''
        score_list = self.session.session_monitor.c_skills_seq
        total_score = defaultdict(int)
        for score in score_list:
            for key, value in score.items():
                total_score[key] += value
        avg_scores = {key: round(total / len(score_list), 2) for key, total in total_score.items()}
        self.clarify_score['skills'] = {}
        for each in self.clarify_criterion.dimensions['skills']:
            full_key = f'{each}的得分'
            if each == '提问有逻辑性得分':
                jump_deduction = self.evaluate_clarify_skills_logic()
                logic_score = self.clarify_score['skills'][each]
                logic_score = logic_score - 1 / 2
                self.clarify_score['skills'][each] = {
                    "score": logic_score + 3 - jump_deduction,
                    "reasons": []
                }
            else:
                self.clarify_score['skills'][each] = {
                    "score": avg_scores[full_key],
                    "reasons": []
                }
        mapper = dict(zip(self.session.session_monitor.c_query_seq, self.session.session_monitor.c_skills_seq))
        # if score < 5:
        low_score_dimension = []
        for i in range(len(avg_scores)):
            if list(avg_scores.values())[i] < 5:
                low_score_dimension.append(list(avg_scores.keys())[i])
        results = {dimension: [] for dimension in low_score_dimension}

        # 遍历每个维度
        for dimension in low_score_dimension:
            # 排序并取得分最低的三个原文
            sorted_queries = sorted(mapper.items(), key=lambda item: item[1][dimension])
            lowest_queries = sorted_queries[:min(3, len(sorted_queries))]
            results[dimension] = [(query, details[dimension]) for query, details in lowest_queries]
            detail_list = []
            for query, score in results[dimension]:
                detail_list.append({
                    "原文": query,
                    "得分": score
                })
                self.clarify_score['skills'][dimension.replace('的得分', '')]['reasons'] = detail_list
        
        

    def evaluate_clarify_skills_logic(self):
        # pass
        c_process_seq = self.session.session_monitor.c_process_seq
        last_seen = {}
        previous_item = None
        jump = 0  # deduction_score

        #检查横跳
        for index, item in enumerate(c_process_seq):
            if item in last_seen:
                # 如果item已经出现过，并且current位置与prev不连续，即为横跳
                if item != previous_item and last_seen[item] != index - 1:
                    jump += 0.5
            if item != previous_item:
                previous_item = item
            # update
            last_seen[item] = index
        return jump

    def evaluate_clarify_correctness(self):
        res = []
        if self.session.session_monitor.is_confirmed:
            res.append(f'成功揭示谜底 - {self.session.objection.real_objection}')
            res.append(f'{self.session.session_monitor.confirming_query}')
            score = 5
        else:
            res.append(f'并未揭示谜底 - {self.session.objection.real_objection}')
            score = 1
        #todo
        # print(f'##### :green[**准确性**]')
        # print(f':blue[**{res}**] - {self.session.objection.real_objection}')
        # print(f'询问原文依据: {self.session.session_monitor.confirming_query}')
        self.clarify_score['correctness'] = {
            "score": score,
            "reasons": {
                '是否揭示谜底': res[0],
                '原文依据': res[1],
            }}

    def evaluate_clarify_process(self):
        # print(f'##### :green[**流程**]')

        c_process_seq = self.session.session_monitor.c_process_seq
        
        # 检查是否四个方面都问到
        label_count = Counter(c_process_seq)
        label_not_touched = [x for x in self.session.session_monitor.label_list if x not in label_count and x != '无关询问']
        
        # 无关询问的扣分判断
        irrelevant_inquiry_deduction = int("无关询问" in c_process_seq)
        
        # 检查问题顺序：先“指向/来源”，后“观念/经验”
        clarify_type = self.session.objection.clarify_type
        directional_question = any(item in c_process_seq for item in ["询问指向", "询问来源"])
        conceptual_question = any(item in c_process_seq for item in ["询问治疗理念", "询问治疗经验"])

        # 判断是否先“指向/来源”，后“观念/经验”
        order_deduction = 0
        if conceptual_question and directional_question:
            valid_process_seq = [x for x in c_process_seq if x != '无关询问']
            if valid_process_seq[0] in ["询问治疗理念", "询问治疗经验"]:
                order_deduction = 2

        # by 澄清类型计算流程得分
        if clarify_type == "安全性":
            if "询问治疗理念" in label_not_touched:
                label_not_touched.remove("询问治疗理念")
            
        # 根据未询问的标签和无关询问扣分
        initial_score = 5 - len(label_not_touched) - irrelevant_inquiry_deduction - order_deduction
        score = max(0, initial_score)    

        # self.clarify_score['process'] = score
        # yield f':blue[ **得分: {score}**]'
        # yield '**理由**'
        # print(f':blue[ **得分: {score}**]')
        # print('**理由**')
        
        reasons, detail_list = [], []
        if len(label_not_touched) > 0:
            reasons.append(f'您未询问以下方面 - {label_not_touched}，扣{len(label_not_touched)}分')
        if irrelevant_inquiry_deduction:
            reasons.append('您有无关询问，再扣1分')
        if order_deduction:
            reasons.append('您的问题顺序错误，先应询问“指向/来源”，后问“观念/经验”，扣2分')
            
        if reasons:
            pass
            # for x in reasons:
            #     print(x)
        else:
            # print('您所有方面都已询问，得5分')
            reasons.append('您所有方面都已询问，得5分')
        
        mapper = dict(zip(self.session.session_monitor.c_query_seq, self.session.session_monitor.c_process_seq))
        if score < 5:
            for each in set(self.session.session_monitor.c_process_seq):
                res = ('**' + each + '原文**')
                sel = [x for x in mapper if mapper[x] == each]
                for item in sel:
                    res = res + ('- ' + item)
                detail_list.append(res)

        self.clarify_score['process'] = {
            "score": score,
            "reasons": {
                'desc': reasons,
                'detail': detail_list
            }
        }

    def evaluate_take_action_skills(self):
        # todo @HEATHER
        # 用self.t_skills_seq来算，不调大模型了
        # print("@@@@@", len(self.session.session_monitor.t_skills_seq), self.session.session_monitor.t_skills_seq)
        '''取平均'''
        score_list = self.session.session_monitor.t_skills_seq
        total_score = defaultdict(int)
        for score in score_list:
            for key, value in score.items():
                total_score[key] += value
        avg_scores = {key: total / len(score_list) for key, total in total_score.items()}
        # print(avg_scores)
        # yield '##### :green[**技巧**]'
        # print('##### :green[**技巧**]')
        self.take_action_score['skills'] = {}
        for each in self.take_action_criterion.dimensions['skills']:
            full_key = f'{each}的得分'
            self.take_action_score['skills'][each] = {
                "score": avg_scores[full_key],
                "reasons": []
            }


        mapper = dict(zip(self.session.session_monitor.t_query_seq, self.session.session_monitor.t_skills_seq))
        # 查找得分低于5的维度
        low_score_dimensions = [key for key, value in avg_scores.items() if value < 5]
        results = {dimension: [] for dimension in low_score_dimensions}
        
        # 对每个得分低于5的维度找到得分最低的三个原文
        for dimension in low_score_dimensions:
            sorted_queries = sorted(mapper.items(), key=lambda item: item[1][dimension])
            lowest_queries = sorted_queries[:min(3, len(sorted_queries))]
            results[dimension] = [(query, details[dimension]) for query, details in lowest_queries]
            detail_list = []
            for query, score in results[dimension]:
                detail_list.append({
                    "原文": query,
                    "得分": score
                })
                self.take_action_score['skills'][dimension.replace('的得分', '')]['reasons'] = detail_list

        # 添加原文到原因中
        # for dimension, entries in results.items():
        #     for query, score in entries:
        #         detail_list.append({
        #             "原文": query,
        #             "得分": score
        #         })
        #     self.take_action_score['skills'][dimension.replace('的得分', '')]['reasons'] = detail_list

            

    def evaluate_take_action_correctness(self):
        correct_ratio = len([1 for x in self.session.session_monitor.t_query_in_standard_answer_seq if x == '是']) / len(self.session.session_monitor.t_query_in_standard_answer_seq)
        if correct_ratio < 0.2:
            score = 0
        elif correct_ratio < 0.4:
            score = 1
        elif correct_ratio < 0.6:
            score = 2
        elif correct_ratio < 0.85:
            score = 3
        elif correct_ratio < 1:
            score = 4
        else:
            score = 5
        # self.take_action_score['correctness'] = f'传达信息正确率为 {correct_ratio}，准确性得分为 {score}'
        # yield f'##### :green[**准确性**]'
        # yield self.take_action_score['correctness']
        # print(f'##### :green[**准确性**]')
        # print(self.take_action_score['correctness'])

        detail_list = []
        assert(len(self.session.session_monitor.t_query_in_standard_answer_seq)==len(self.session.session_monitor.t_query_seq))
        for idx, each in enumerate(self.session.session_monitor.t_query_in_standard_answer_seq):
            if each == '否':
                detail_list.append(self.session.session_monitor.t_query_seq[idx])

        self.take_action_score['correctness'] = {
            "score": score,
            "reasons": {
                'desc': f'传达信息正确率为 {correct_ratio}，准确性得分为 {score}',
                'details': detail_list
            }
        }

    def evaluate_take_action_process(self):
        label_count = Counter(self.session.session_monitor.t_process_seq)
        self.take_action_score['process'] = label_count
        # yield f'##### :green[**流程**]'
        # yield self.take_action_score['process']
        # print(f'##### :green[**流程**]')
        # print(self.take_action_score['process'])
        
        label_not_touched = [x for x in self.session.session_monitor.label_list_t if x not in label_count and x != '无关内容']
        irrelevant_content_deduction = int("无关内容" in self.session.session_monitor.t_process_seq)
        take_action_type = self.session.objection.take_action_type
        
        # 根据不同的反对类型，调整未触及的标签列表
        if take_action_type == "误解型":
            label_not_touched = [x for x in label_not_touched if x == "提供证据"]
        elif take_action_type == "怀疑型":
            label_not_touched = [x for x in label_not_touched if x != "传达整体优势及利益"]
        elif take_action_type == "缺陷型":
            label_not_touched = [x for x in label_not_touched if x not in ["传达FB", "传达专家建议和经验案例"]]
        
        # 计算得分
        score = 5 - len(label_not_touched) - irrelevant_content_deduction
        # self.take_action_score['process'] = score
        # yield f':blue[ **得分: {score}**]'
        # yield '**理由**'
        reasons, detail_list = [], []
        if len(label_not_touched) > 0:
            reasons.append(f'未解决以下方面 - {label_not_touched}，扣{len(label_not_touched)}分')
        if irrelevant_content_deduction:
            reasons.append('同时有无关内容，再扣1分')
        if score >= 5:
            reasons.append('所有方面都已提供解决，得5分')
        mapper = dict(zip(self.session.session_monitor.t_query_seq, self.session.session_monitor.t_process_seq))
        if score < 5:
            for each in set(self.session.session_monitor.t_process_seq):
                res = ('**' + each + '原文**')
                sel = [x for x in mapper if mapper[x] == each]
                for item in sel:
                    res = res + ('- ' + item)
                detail_list.append(res)

        self.take_action_score['process'] = {
            "score": score,
            "reasons": {
                'desc': reasons,
                'detail': detail_list
            }
        }
        # print(f':blue[ **得分: {score}**]')
        # print('**理由**')

        # 输出理由
        # if len(label_not_touched) > 0:
        #     yield f'您未解决以下方面 - {label_not_touched}，扣{len(label_not_touched)}分' + '，同时有无关内容，再扣1分' * irrelevant_content_deduction
        # else:
        #     yield f'您所有方面都已提供解决，得5分' + '，但有无关内容，扣1分' * irrelevant_content_deduction
        

    def save(self, path):
        pickle.dump(self, open(os.path.join(path, f'{self.session.rep.name}_{self.session.hcp.hcp_name}_{self.session.objection.preset_objection}_{self.session.create_time}'), 'wb'))