from langchain.prompts import PromptTemplate


skill_schema = {
    "type": "object",
    "properties": {
        "reasons": {
            "type": "string",
            "description": "理由/判断依据"
        },
        "evidence": {
            "type": "string",
            "description": "支持理由/判断依据的“提问-回答”的原文Pair，仅需要输出原文即可",
        },
        "score": {
            "type": "string",
            "description": "5分制得分"
        }
    },
    "required": ["reasons", "evidence", "score"]
}

clarify_skill_prompt = PromptTemplate.from_template('''
<背景>
你是一家国际制药大厂的医药代表销售话术培训师，目前在培训关于{product}产品异议处理的"澄清部分(Clarify)"
</背景>

<名词解释>
“异议”：指的是医生对于药品{product}的某种认知
“预设异议”：是在对话开始前，医生对药品{product}的最初/浅层认知。在本例中，预设异议为{preset_objection}
“真实异议”：是随着对话的进行，所揭示出来的医生对药品{product}的底层用药习惯或认知。是医生关于{product}真正的异议。在本例中，真实异议为{real_objection}
“异议处理的澄清部分”：指的是医药代表通过与医生的多轮对话、问答，逐步揭示并确认医生的真实异议的过程
</名词解释>
-----------------------------

<评价维度背景>
{all_definition}
</评价维度背景>

<你的任务>
请你从“{dimension}(1-5分)”的维度，评价医药代表“澄清部分(Clarify)”的能力
- 请你为医药代表在1-5分之间打上最合适的分数（5分最优，1分最差）
- 请说明你评分的1个最合理的理由/推断逻辑(opinions)
- 请为你的理由/推断逻辑，找到1对医药代表提问/医生回答的Pair的原文依据(sources)
- let's think step by step
- do not make up an answer
</你的任务>

<{dimension}维度下的评价标准>
{definition}
</{dimension}维度下的评价标准>
-----------------------------

<请给评价以下对话中医药代表的{dimension}维度评分>
{chat_history}
''')

take_action_skill_prompt = PromptTemplate.from_template('''
<背景>
你是一家国际制药大厂的医药代表销售话术培训师，目前在培训关于{product}产品异议处理的"解决部分(Take Action)"
</背景>

<名词解释>
“真实异议”：即确认后的异议，是医生关于药品{product}的某种认知。在本例中，真实异议为{real_objection}
</名词解释>
-----------------------------

<你的任务>
请你按照以下标准，在每个维度上为医药代表的话术评分
评价医药代表“异议的处理”能力，可以从多个维度来评价，评价维度如下
请你在子每个维度上，为医药代表在1-5分之间选择最合适的分数，5分最高，1分最低，并说明理由，最好有医药代表提问的原文依据支持你的理由
</你的任务>

<评价维度>
1. 知识
    - 医药代表是否准确传达了{product}的关键信息
    - 表达是否简洁
2. FB
    - 医药代表是否能准确的抓住异议处理的机会传递产品信息
    - 是否可以准确结合异议的核心点
3. 逻辑性
    - 阐述过程是否逻辑清晰，主次分明
4. 流畅性
    - 语言表达是否流畅
</评价维度>
-----------------------------
    
<example of output>
医药代表异议处理的细分维度评价：

1. 知识
- x/5
- 理由：xxx
- 原文依据：xxx

2. FB
- x/5
- 理由：xxx
- 原文依据：xxx

3. 逻辑性
- x/5
- 理由：xxx
- 原文依据：xxx

4. 流畅性
- x/5
- 理由：xxx
- 原文依据：xxx

综上，医药代表异议处理的整体评价：x/5
''')
