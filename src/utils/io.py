from src.static_classes import ObjectionCase, VirtualHcp, EvaluateCriterion, Representative, QuickQuestion
from src.utils.generate_hcp import *
from docx import Document
import yaml
import pandas as pd


def load_objection_case_from_yaml(path):
    with open(path) as stream:
        res = yaml.safe_load(stream)
    objection = ObjectionCase(
        id=res['objection']['id'],
        version=res['objection']['version'],
        preset_objection=res['objection']['preset_objection'],
        real_objection=res['objection']['real_objection'],
        selected_real_objection=None,
        hcp_space=res['objection']['hcp_space'],
        clinic_cases=res['objection']['clinic_cases']
    )
    return objection


def load_hcp_from_dict(**args):
    sel_personality = args.get('hcp_personality', np.random.choice(PERSONALITY))
    hcp = VirtualHcp(
        hcp_name=args.get('name', np.random.choice(NAME)),
        hcp_gender=args.get('gender', np.random.choice(GENDER)),
        hsp_tier_1=args.get('hsp_tier_1', np.random.choice(HOSPITAL_TIER_1)),
        hsp_tier_2=args.get('hsp_tier_2', np.random.choice(HOSPITAL_TIER_2)),
        hsp_type=args.get('hsp_type', np.random.choice(HOSPITAL_TYPE)),
        hcp_position=args.get('hcp_position', np.random.choice(POSITION)),
        hcp_study_aboard=args.get('hcp_study_aboard', np.random.choice(STUDY_ABOARD)),
        hcp_personality=sel_personality,
        hcp_personality_desc=[x['personality_desc'] for x in PERSONALITY if x['personality_type'] == sel_personality][0],
        hcp_dept=args.get('hcp_dept', np.random.choice(DEPT)),
        hcp_scene=args['hcp_scene'],
        hcp_type=args['hcp_type'],
        # hcp_patients=args['hcp_patients'],
        # hcp_opinion=args['hcp_opinion'],
        hcp_knowledge_stage=args['hcp_knowledge_stage']
    )
    return hcp


def load_evaluation_criterion_from_yaml(path):
    with open(path) as stream:
        res = yaml.safe_load(stream)
    criterion = EvaluateCriterion(
        evaluation_type=res['criterion']['evaluation_type'],
        version=res['criterion']['version'],
        dimensions=res['criterion']['dimensions'],
        definitions=res['criterion']['definitions'],
        few_shots_examples=res['criterion']['few_shots_examples']
    )
    return criterion


def load_rep_from_yaml(path):
    with open(path) as stream:
        res = yaml.safe_load(stream)
    rep = Representative(
        id=res['rep']['id'],
        name=res['rep']['name']
    )
    return rep

def load_quick_quiz_questions_df_from_docx(path):
    doc = Document(path)
    questions = []
    answers = []
    score_points = []

    current_question = None
    current_answer = []
    current_score_points = []

    in_score_points = False
    for para in doc.paragraphs:
        text = para.text.strip()
        if text.endswith('？'):
            if current_question:
                # 保存前一个问题的数据
                questions.append(current_question)
                answers.append("\n".join(current_answer))
                score_points.append(current_score_points)
            current_question = text
            current_answer = []
            current_score_points = []
            in_score_points = False
        elif text.startswith('得分点：') or text.startswith('要点:'):
            in_score_points = True
        elif in_score_points:
            if text:
                current_score_points.append(text)
        else:
            current_answer.append(text)
    if current_question:
        questions.append(current_question)
        answers.append("\n".join(current_answer))
        score_points.append(current_score_points)
    df = pd.DataFrame({
        '问题': questions,
        '标准答案': answers,
        '得分点': score_points
    })
    df['id'] = range(3, len(df) + 3)
    return df

def load_quick_quiz_questions_from_excel(path):
    df = pd.read_excel(path)
    questions = []
    for _, row in df.iterrows():
        questions.append(
            QuickQuestion(
                id=row['id'],
                question=row['question'],
                answer=row['answer'],
                key_points=row['key_points'].split('|')
            )
        )
    return questions