from dataclasses import dataclass


@dataclass
class ObjectionCase:
    id: int
    version: str
    preset_objection: str
    real_objection: list
    selected_real_objection: dict
    hcp_space: dict
    clinic_cases: list


@dataclass
class ObjectionInstance:
    preset_objection: str       # 谜面
    real_objection: str         # 谜底
    clarify_type: str           # 澄清类型
    take_action_type: str       # 解决类型
    visible_background: str     # 可见背景信息
    invisible_background: str   # 不可见背景信息
    standard_answer: list       # 解决阶段要点


@dataclass
class VirtualHcp:
    hcp_name: str               # 医生姓氏，随机生成
    hcp_gender: str             # 性别，男/女
    hsp_tier_1: str             # 医院等级，一二三级
    hsp_tier_2: str             # 医院等级，甲乙丙等
    hsp_type: str               # 医院类型，公立/私立/部队
    hcp_position: str           # 医生职级，主任/副主任/主治/普通
    hcp_study_aboard: str       # 是否留学，是/否
    hcp_personality: str        # 医生个性，严厉/友善
    hcp_personality_desc: str   # 医生个性描述，预设string
    hcp_dept: str               # 改为让用户free text输入
    hcp_scene: str              # 改为让用户free text输入
    hcp_type: str               # 改为让用户free text输入
    # hcp_patients: list          # 改为让用户free text输入
    # hcp_opinion: str            # 改为让用户free text输入
    hcp_knowledge_stage: str    # 改为让用户free text输入


@dataclass
class EvaluateCriterion:
    evaluation_type: str
    version: str
    dimensions: list
    definitions: dict
    few_shots_examples: dict


@dataclass
class Representative:
    id: int
    name: str


@dataclass
class QuickQuestion:
    id: int
    question: str
    answer: str
    key_points: list