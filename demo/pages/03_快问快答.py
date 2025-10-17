import streamlit as st
from src.utils.io import load_quick_quiz_questions_from_excel, load_rep_from_yaml
from src.quick_quiz import Quiz
import json
import sys
sys.path.append('..')


st.set_page_config(
    page_title="Welcome to NovoNordisk Quick Quiz",
    page_icon="👋",
)
st.markdown('''### :green[快问快答]''')

rep_file = st.sidebar.selectbox('请登录您的账户', options=['001_EdgarCao', '002_AndrewYu'])
rep = load_rep_from_yaml(f'../data/reps/{rep_file}.yml')

questions_list = load_quick_quiz_questions_from_excel(f'../data/quick_quiz/questions.xlsx')
quiz = Quiz(
    questions_list=questions_list
)
sel_index = st.number_input("请选择题号", value=1, min_value=1, max_value=len(questions_list))
quiz.get_question(sel_index-1)

st.markdown(f'''##### :green[第{sel_index}题] {quiz.sel_question.question}''')

# user_answer = st.text_area('请回答', value="", placeholder=quiz.sel_question.answer, height=200)
user_answer = st.text_area('请回答', value=quiz.sel_question.answer, height=200)

if st.button('提交'):
    quiz.evaluate(user_answer)
    st.markdown(f''':blue[**{quiz.result[-1]['evaluation']}**]''')
    st.markdown(f'''**您的答案**：{quiz.result[-1]['user_answer']}''')
    st.markdown(f'''**标准答案**：{quiz.result[-1]['question'].answer}''')
    st.markdown(f'''**命中要点**：{quiz.result[-1]['hit_key_points']}''')
    st.markdown(f'''**错失要点**：{quiz.result[-1]['missed_key_points']}''')
