import datetime
import pickle
import os
import yaml
import numpy as np
from src.llm_inference import gpt_query, gpt_query_stream
from src.session_monitor import Monitor
from prompts.hcp_chat_prompt import hcp_setting_prompt, system_prompt, user_prompt, task_instructions
from src.llm_vectorstores import get_similar_text
from audio.tts.baidu_tts import tts_baidu
from audio.tts.openai_tts import tts_openai
from audio.tts.iflytek_tts import tts_iflytek
import IPython


MAX_LEN_FILENAME = 64

class Session(object):
    def __init__(self,
                 hcp,
                 objection,
                 rep,
                 chat_history=None,
                 res_style='混合模式',
                 tts=None,
                 use_dept_knowledge=False,
                 use_product_knowledge=False,
                 monitor=False,
                 product='司美格鲁肽注射液(诺和泰)',
                 llm='gpt-4-0125-preview',
                 llm_params={},
                 prompt_tokens=0,
                 completion_tokens=0,
                 start_time=None,
                 stage='CLARIFY'):
        os.makedirs('../data/audios', exist_ok=True)
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.hcp = hcp
        self.stage = stage
        self.res_style = res_style
        self.objection = objection
        self.rep = rep
        self.product = product
        self.apply_tts = tts
        self.use_dept_knowledge = use_dept_knowledge
        self.use_product_knowledge = use_product_knowledge
        self.llm = llm
        self.llm_params = llm_params
        # 生成医生人设prompt
        self.hcp_setting_prompt = hcp_setting_prompt.format(
            product=self.product,
            hcp_name=self.hcp.hcp_name,
            hcp_gender=self.hcp.hcp_gender,
            hsp_tier_1=self.hcp.hsp_tier_1,
            hsp_tier_2=self.hcp.hsp_tier_2,
            hsp_type=self.hcp.hsp_type,
            hcp_position=self.hcp.hcp_position,
            hcp_study_aboard=self.hcp.hcp_study_aboard,
            # hcp_dept=self.hcp.hcp_dept,
            # hcp_scene=self.hcp.hcp_scene,
            # hcp_type=self.hcp.hcp_type,
            # hcp_opinion=self.hcp.hcp_opinion,
            # hcp_patients=self.hcp.hcp_patients,
            # hcp_knowledge_stage=self.hcp.hcp_knowledge_stage,
            hcp_personality=self.hcp.hcp_personality,
            hcp_personality_desc=self.hcp.hcp_personality_desc
        )
        self.create_time = start_time
        self.is_on = True
        if monitor:
            self.monitor = monitor
            path = '../data/criterions/clarify_criterion.yml'
            with open(path) as stream:
                clarify_criterion = yaml.safe_load(stream)['criterion']
            path = '../data/criterions/take_action_criterion.yml'
            with open(path) as stream:
                take_action_criterion = yaml.safe_load(stream)['criterion']
            self.session_monitor = Monitor(clarify_criterion=clarify_criterion, take_action_criterion=take_action_criterion)
            self.session_monitor.set_objection(self.objection)
        self.system_prompt = system_prompt.format(
            product=self.product,
            hcp_setting_prompt=self.hcp_setting_prompt,
            real_objection=self.objection.real_objection,
            visible_background=self.objection.visible_background,
            invisible_background=self.objection.invisible_background
        )
        if chat_history is None:
            self.chat_history = [{'role': 'system', 'content': self.system_prompt}]
        else:
            self.chat_history = chat_history
        self.chat_history_time = [self.create_time]
        self.assistant_time_spent = []
        self.num_queries = 0

    def append(self, role, message, time=datetime.datetime.now()):
        self.chat_history.append({'role': role, 'content': message})
        self.chat_history_time.append(time)

    def display_tts(self, res):
        assert(self.apply_tts in ['openai', 'iflytek', 'baidu'])
        mp3_path = f'../output/audios/{self.apply_tts}_{res}.mp3'[:MAX_LEN_FILENAME]
        if self.apply_tts == 'openai':
            _ = tts_openai(res, mp3_path=mp3_path, voice=self.hcp.hcp_gender)
        if self.apply_tts == 'iflytek':
            _ = tts_iflytek(res, mp3_path=mp3_path)
        if self.apply_tts == 'baidu':
            _ = tts_baidu(res, mp3_path=mp3_path)
        try:
            IPython.display.display(IPython.display.Audio(mp3_path))
        except:
            pass

    def get_product_knowledge(self, k=5):
        if self.use_product_knowledge:
            materials = get_similar_text(input, vectordb_path='../data/vectorstores/knowledges/chroma_db', k=k)
            materials = '\n'.join([x.page_content for x in materials])
        else:
            materials = f'未接入{self.product}知识库，请根据预训练知识和你的人设回答问题'
        return materials

    def get_dept_knowledge(self, k=5):
        if self.use_dept_knowledge:
            materials = get_similar_text(input, vectordb_path='../data/vectorstores/心内知识库/chroma_db', k=k)
            materials = '<心内科知识库>\n' + '\n'.join([x.page_content for x in materials]) + '</心内科知识库>\n'
        else:
            materials = f'未接入心内科知识库，请根据预训练知识和你的人设回答问题'
        return materials

    def get_sustain_knowledge(self, k=5):
        if self.use_product_knowledge:
            materials = get_similar_text(input, vectordb_path='../data/vectorstores/SUSTAIN知识库/chroma_db', k=k)
            materials = '<SUSTAIN知识库>\n' + '\n'.join([x.page_content for x in materials]) + '</SUSTAIN知识库>\n'
        else:
            materials = f'未接入SUSTAIN知识库，请根据预训练知识和你的人设回答问题'
        return materials

    def get_task_instruction(self):
        if self.res_style == '混合模式':
            task_instruction = task_instructions[np.random.choice(list(task_instructions.keys()))]
        else:
            task_instruction = task_instructions[self.res_style]

        task_instruction_related = task_instruction[0].format(real_objection=self.objection.real_objection)
        task_instruction_confirming = task_instruction[1].format(real_objection=self.objection.real_objection)
        return task_instruction_related, task_instruction_confirming

    def hcp_initiate_direct(self):
        res = self.objection.preset_objection
        self.append('assistant', res)
        for each in res:
            yield each
        if self.apply_tts is not None:
            self.display_tts(res)

    def hcp_initiate(self):
        materials_dept = self.get_dept_knowledge()
        materials_sustain = self.get_sustain_knowledge()
        materials = '\n\n'.join([materials_dept, materials_sustain])
        prompt = initiate_prompt.format(
            product='司美格鲁肽注射液（诺和泰）',
            hcp_setting_prompt=self.hcp_setting_prompt,
            preset_objection=self.objection.preset_objection,
            materials=materials
        )
        stream = gpt_query_stream(self.chat_history + [{'role': 'user', 'content': prompt}], self.llm, **self.llm_params)
        res = ''
        for chunk in stream:
            res_chunk = chunk.choices[0].delta.content
            if res_chunk is not None:
                yield res_chunk
                res += res_chunk
        self.prompt_tokens += 0
        self.completion_tokens += 0
        self.append('assistant', res)
        if self.apply_tts is not None:
            self.display_tts(res)

    def chat(self, input):
        materials_dept = self.get_dept_knowledge()
        materials_product = self.get_product_knowledge()
        materials_sustain = self.get_sustain_knowledge()
        materials = '\n\n'.join([materials_dept, materials_sustain, materials_product])
        task_instruction_related, task_instruction_confirming = self.get_task_instruction()
        prompt = user_prompt.format(
            product='司美格鲁肽注射液（诺和泰）',
            hcp_setting_prompt=self.hcp_setting_prompt,
            preset_objection=self.objection.preset_objection,
            real_objection=self.objection.real_objection,
            visible_background=self.objection.visible_background,
            invisible_background=self.objection.invisible_background,
            materials=materials,
            task_instruction_related=task_instruction_related,
            task_instruction_confirming=task_instruction_confirming,
            input=input
        )
        response, cost = gpt_query(self.chat_history + [{'role': 'user', 'content': prompt}], self.llm, **self.llm_params)
        res = response.choices[0].message.content
        self.prompt_tokens += cost['prompt_tokens']
        self.completion_tokens += cost['completion_tokens']
        self.append('user', input)
        self.append('assistant', res)

        if self.apply_tts is not None:
            assert(self.apply_tts in ['openai', 'iflytek', 'baidu'])
            mp3_path = f'../output/audios/{self.apply_tts}_{res}.mp3'[:MAX_LEN_FILENAME]
            if self.apply_tts == 'openai':
                time_cost = tts_openai(res, mp3_path=mp3_path, voice=self.hcp.hcp_gender)
            if self.apply_tts == 'iflytek':
                time_cost = tts_iflytek(res, mp3_path=mp3_path)
            if self.apply_tts == 'baidu':
                time_cost = tts_baidu(res, mp3_path=mp3_path)
            try:
                IPython.display.display(IPython.display.Audio(mp3_path))
            except:
                pass
        else:
            time_cost = 0
        print(f'[{self.hcp.hcp_name}]', res, f" -- 耗时{(cost['time']+time_cost):.2f}({cost['time']:.2f})")
        print('-'*20)

    def chat_stream(self, input):
        self.num_queries += 1
        materials_dept = self.get_dept_knowledge()
        materials_sustain = self.get_sustain_knowledge()
        materials_product = self.get_product_knowledge()
        materials = '\n\n'.join([materials_dept, materials_sustain, materials_product])
        task_instruction_related, task_instruction_confirming = self.get_task_instruction()
        prompt = user_prompt.format(
            product='司美格鲁肽注射液（诺和泰）',
            hcp_setting_prompt=self.hcp_setting_prompt,
            preset_objection=self.objection.preset_objection,
            real_objection=self.objection.real_objection,
            visible_background=self.objection.visible_background,
            invisible_background=self.objection.invisible_background,
            materials=materials,
            task_instruction_related=task_instruction_related,
            task_instruction_confirming=task_instruction_confirming,
            input=input
        )
        print(prompt)
        stream = gpt_query_stream(self.chat_history + [{'role': 'user', 'content': prompt}], self.llm, **self.llm_params)
        res = ''
        for chunk in stream:
            res_chunk = chunk.choices[0].delta.content
            if res_chunk is not None:
                yield res_chunk
                res += res_chunk
        self.prompt_tokens += 0
        self.completion_tokens += 0
        self.append('user', input)
        self.append('assistant', res)

        if self.apply_tts is not None:
            assert(self.apply_tts in ['openai', 'iflytek', 'baidu'])
            mp3_path = f'../output/audios/{self.apply_tts}_{res}.mp3'[:MAX_LEN_FILENAME]
            if self.apply_tts == 'openai':
                time_cost = tts_openai(res, mp3_path=mp3_path, voice=self.hcp.hcp_gender)
            if self.apply_tts == 'iflytek':
                time_cost = tts_iflytek(res, mp3_path=mp3_path)
            if self.apply_tts == 'baidu':
                time_cost = tts_baidu(res, mp3_path=mp3_path)
            try:
                IPython.display.display(IPython.display.Audio(mp3_path))
            except:
                pass
        else:
            time_cost = 0

    def show_chat_history(self):
        assert(len(self.chat_history) == len(self.chat_history_time))
        for i in range(len(self.chat_history)):
            print(self.chat_history[i]['role'], '@', self.chat_history_time[i])
            print(self.chat_history[i]['content'])
            print('\n')

    def close(self):
        self.close_time = datetime.datetime.now()
        self.is_on = Flase

    def save(self, path):
        pickle.dump(self, open(os.path.join(path, f'{self.rep.name}_{self.hcp.hcp_name}_{self.objection.preset_objection}_{self.create_time}'), 'wb'))
