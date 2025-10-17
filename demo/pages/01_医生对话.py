import json
import streamlit as st
import numpy as np
from src.session import Session
from src.utils.io import load_objection_case_from_yaml, load_rep_from_yaml, load_hcp_from_dict
from src.static_classes import VirtualHcp, ObjectionInstance
from audio.tts.openai_tts import tts_openai
import sys
sys.path.append('..')


st.set_page_config(
    page_title="Welcome to NovoNordisk ChatHCP",
    page_icon="👋",
)

MAX_LEN_FILENAME = 64
st.markdown('''### :green[虚拟医生对话]''')
col1, col2, col3, col4 = st.columns(4)
with col1:
    use_monitor = st.toggle('练习模式')
if use_monitor:
    with col2:
        select_hcp = st.toggle('指定虚拟医生')
    with col3:
        select_real = st.toggle('指定真实异议')
with col4:
    open_voice = st.toggle('语音模式')

rep_file = st.sidebar.selectbox('请登录您的账户', options=['001_EdgarCao', '002_AndrewYu'])
objection_file = st.sidebar.selectbox('请选择异议题目', options=[
    '001_SGLT-2i和诺和泰都是有心血管获益的药物',
    '002_诺和泰有胃肠道反应大，处理起来麻烦',
    '003_患者HbA1c已经达标，没必要再去调整原来的降糖方案了',
    '004_患者目前的降糖方案复杂，再加用诺和泰，调整起来很麻烦',
    '005_诺和泰需要注射，不好说服患者'
])
rep = load_rep_from_yaml(f'../data/reps/{rep_file}.yml')
objection = load_objection_case_from_yaml(f'../data/objections/{objection_file}.yml')

if use_monitor and select_real:
    selected_real_objection_name = st.selectbox('请选择真实异议(谜底)', options=[x['name'] for x in objection.real_objection])
    selected_real_objection = [x for x in objection.real_objection if x['name'] == selected_real_objection_name][0]
else:
    selected_real_objection = np.random.choice(objection.real_objection)
objection.selected_real_objection = selected_real_objection

objection_instance = ObjectionInstance(
    preset_objection=objection.preset_objection,
    real_objection=objection.selected_real_objection['name'],
    clarify_type=objection.selected_real_objection['clarify_type'],
    take_action_type=objection.selected_real_objection['take_action_type'],
    visible_background=objection.selected_real_objection['visible_extra_info'],         # 可见背景信息
    invisible_background=objection.selected_real_objection['invisible_extra_info'],     # 不可见背景信息
    standard_answer=objection.selected_real_objection['standard_answer']                # 解决阶段要点
)

hcp_attr = {}
if use_monitor and select_hcp:
    col1, col2, col3 = st.columns(3)
    with col1:
        hcp_attr['hcp_dept'] = st.selectbox('请选择虚拟医生科室', options=objection.hcp_space['hcp_dept'])
        hcp_attr['hcp_type'] = st.selectbox('请选择虚拟医生类型', options=objection.hcp_space['hcp_type'])
    with col2:
        hcp_attr['hcp_scene'] = st.selectbox('请选择虚拟对话场景', options=objection.hcp_space['hcp_scene'])
        hcp_attr['hcp_personality'] = st.selectbox('请选择虚拟医生性格', options=objection.hcp_space['hcp_personality'])
    with col3:
        hcp_attr['hcp_knowledge_stage'] = st.selectbox('请选择虚拟医生认知阶梯', options=objection.hcp_space['hcp_knowledge_stage'])
else:
    hcp_attr['hcp_dept'] = np.random.choice(objection.hcp_space['hcp_dept'])
    hcp_attr['hcp_type'] = np.random.choice(objection.hcp_space['hcp_type'])
    hcp_attr['hcp_scene'] = np.random.choice(objection.hcp_space['hcp_scene'])
    hcp_attr['hcp_personality'] = np.random.choice(objection.hcp_space['hcp_personality'])
    hcp_attr['hcp_knowledge_stage'] = np.random.choice(objection.hcp_space['hcp_knowledge_stage'])
    # hcp_attr['hcp_opinion'] = np.random.choice(objection.hcp_space['hcp_opinion'])
    # hcp_attr['hcp_patients'] = objection.hcp_space['hcp_patients']
objection_instance.visible_background = f'''注意你是一名{hcp_attr['hcp_dept']}医生，一名{hcp_attr['hcp_type']}医生。这段对话发生在{hcp_attr['hcp_scene']}场景。您对诺和泰的使用属于{hcp_attr['hcp_knowledge_stage']}'''
hcp = load_hcp_from_dict(**hcp_attr)

# res_style = st.sidebar.selectbox('请选择医生对确认异议的反应模式', options=['大方承认', '支支吾吾', '胡编乱造', '混合模式'])
use_dept_knowledge = st.sidebar.selectbox('虚拟医生是否启用专科知识库', options=[True, False])
use_product_knowledge = st.sidebar.selectbox('虚拟医生是否启用诺和泰知识库', options=[True, False])

llm = st.sidebar.selectbox('请选择基座模型', options=['gpt-4-0125-preview', 'gpt-3.5-turbo'])
temp = st.sidebar.slider('请选择生成语言温度', 0.0, 2.0, value=1.2, step=0.05)
frequency_penalty = st.sidebar.slider('frequency_penalty', -2.0, 2.0, value=1.5, step=0.05)
presence_penalty = st.sidebar.slider('presence_penalty', -2.0, 2.0, value=1.5, step=0.05)
llm_params = {'temperature': temp, 'frequency_penalty': frequency_penalty, 'presence_penalty': presence_penalty}

col1, col2, col3 = st.columns([3, 1, 1])
with col1:
    if use_monitor:
        st.markdown('''#### 练习模式''')
    else:
        st.markdown('''#### 测试模式''')
with col2:
    if st.button('新建聊天对话'):
        del st.session_state['chat_session']
with col3:
    if st.button('保存当前对话'):
        st.session_state.chat_session.save('../output/chat_history')

if 'chat_session' not in st.session_state:
    st.session_state.image_path = f'../data/images/{hcp.hcp_gender}医生.jpg'
    session = Session(
        rep=rep,
        hcp=hcp,
        objection=objection_instance,
        tts='openai',
        use_dept_knowledge=use_dept_knowledge,
        use_product_knowledge=use_product_knowledge,
        monitor=True,
        llm=llm,
        llm_params=llm_params
    )
    st.session_state['chat_session'] = session

with st.expander('点击展开异议背景', expanded=False):

    st.markdown(f'##### 欢迎使用虚拟医生对话机器人 Novo ChatHCP!')
    # st.markdown(f'###### 您好，:green[**{st.session_state.chat_session.rep.name}**] [编号:green[{st.session_state.chat_session.rep.id}]]')
    st.markdown(f'###### 此题的预设异议是 -【{st.session_state.chat_session.objection.preset_objection}】')
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'###### **您面对的虚拟医生是** - {st.session_state.chat_session.hcp.hcp_name}医生')
        st.markdown(f"**性别**:\n{st.session_state.chat_session.hcp.hcp_gender}")
        st.markdown(f"**科室标签**:\n{st.session_state.chat_session.hcp.hcp_dept}")
        st.markdown(f"**拜访场景**:\n{st.session_state.chat_session.hcp.hcp_scene}")
        st.markdown(f"**医生分类**:\n{st.session_state.chat_session.hcp.hcp_type}")
        # st.markdown(f"**治疗观念**:\n{st.session_state.chat_session.hcp.hcp_opinion}")
        st.markdown(f"**认知阶梯**:\n{st.session_state.chat_session.hcp.hcp_knowledge_stage}")
        st.markdown(f"**沟通风格**:\n{st.session_state.chat_session.hcp.hcp_personality}")
        # profile = st.text_area(f'- **他的身份是**', value=st.session_state.chat_session.hcp.profile)
        # opinion = st.text_area(f'- 据您所知**他对诺和泰的态度是**', value=st.session_state.chat_session.hcp.opinion)
        # personality = st.text_area(f'- 据您所知**他的个性是**', value="\n".join(st.session_state.chat_session.hcp.personality))
        # new_hcp = VirtualHcp(
        #     id=st.session_state.chat_session.hcp.id,
        #     name=st.session_state.chat_session.hcp.name,
        #     gender=st.session_state.chat_session.hcp.gender,
        #     version=st.session_state.chat_session.hcp.version,
        #     profile=profile,
        #     opinion=opinion,
        #     personality=personality.split('\n'),
        #     clinic_cases=st.session_state.chat_session.hcp.clinic_cases)
        # st.session_state.chat_session.hcp = new_hcp
    with col2:
        st.image(st.session_state.image_path)

if len(st.session_state.chat_session.chat_history) == 1:
    with st.chat_message('assistant'):
        stream = st.session_state.chat_session.hcp_initiate_direct()
        response = st.write_stream(stream)
        if open_voice:
            st.audio(f'../output/audios/{st.session_state.chat_session.apply_tts}_{response}.mp3'[:MAX_LEN_FILENAME])
else:
    for i in range(len(st.session_state.chat_session.chat_history)):
        if i > 0:
            message = st.session_state.chat_session.chat_history[i]
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if message["role"] == 'assistant':
                    if open_voice:
                        st.audio(f'../output/audios/{st.session_state.chat_session.apply_tts}_{message["content"]}.mp3'[:MAX_LEN_FILENAME])

if input == st.chat_input(f"请与{st.session_state.chat_session.hcp.hcp_name}医生交流，完成异议处理"):
    prompt = input
    with st.chat_message("user"):
        st.markdown(input)

    with st.chat_message("assistant"):
        stream = st.session_state.chat_session.chat_stream(input)
        response = st.write_stream(stream)
        if open_voice:
            mp3_path, time_cost = tts_openai(response)
            st.audio(f'../output/audios/{st.session_state.chat_session.apply_tts}_{response}.mp3'[:MAX_LEN_FILENAME])

        chat_history = ''
        for each in st.session_state.chat_session.chat_history[:-2]:
            if each['role'] == 'user':
                chat_history += f"医药代表：{each['content']}\n"
            if each['role'] == 'assistant':
                chat_history += f"医生：{each['content']}\n"
        if not st.session_state.chat_session.session_monitor.is_confirmed:
            stage_type, process_type, is_confirmation = st.session_state.chat_session.session_monitor.c_process(chat_history, input)
            st.session_state.chat_session.session_monitor.c_skills(chat_history, input)
            print(stage_type, process_type, is_confirmation)
            output = st.session_state.chat_session.session_monitor.c_guide_process(stage_type, process_type, is_confirmation)
            if use_monitor:
                for each in output:
                    st.write(each)
        else:
            stage_type, process_type, is_in_standard_answer = st.session_state.chat_session.session_monitor.t_process(chat_history, input)
            st.session_state.chat_session.session_monitor.t_skills(chat_history, input)
            print(stage_type, process_type, is_in_standard_answer)
            output = st.session_state.chat_session.session_monitor.t_guide_process(stage_type, process_type, is_in_standard_answer)
            if use_monitor:
                for each in output:
                    st.write(each)