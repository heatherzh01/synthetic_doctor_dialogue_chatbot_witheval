from langchain.prompts import PromptTemplate


skill_schema = {
    "type": "object",
    "properties": {
        "reasons": {
            "type": "string",
            "description": "Reason / judgment basis"
        },
        "evidence": {
            "type": "string",
            "description": "The original Q&A pair that supports the reason/judgment. Only output the original text.",
        },
        "score": {
            "type": "string",
            "description": "Score on a 5-point scale"
        }
    },
    "required": ["reasons", "evidence", "score"]
}

clarify_skill_prompt = PromptTemplate.from_template('''
<Background>
You are a sales training coach for medical representatives at a global pharmaceutical company. You are currently training the “Clarify” part of objection handling for product {product}.
</Background>

<Terminology>
“Objection”: Refers to the doctor’s perception of the drug {product}.
“Preset objection”: The doctor’s initial/superficial perception of the drug {product} before the conversation begins. In this case, the preset objection is {preset_objection}.
“Real objection”: The underlying prescribing habits or perceptions of the doctor revealed during the conversation. This is the doctor’s true objection to {product}. In this case, the real objection is {real_objection}.
“The Clarify part of objection handling”: Refers to the process in which the medical representative, through multiple rounds of Q&A with the doctor, gradually reveals and confirms the doctor’s real objection.
</Terminology>
-----------------------------

<Evaluation Dimension Background>
{all_definition}
</Evaluation Dimension Background>

<Your Task>
Please evaluate the medical representative’s ability in the “Clarify” part of objection handling from the “{dimension} (1–5 points)” dimension:
- Give the most appropriate score between 1–5 (5 = best, 1 = worst)
- Provide one clear reason/inference logic (opinions) for your score
- Identify one original Q&A pair from the dialogue that supports your reason (sources)
- let's think step by step
- do not make up an answer
</Your Task>

<Evaluation Standard for {dimension}>
{definition}
</Evaluation Standard for {dimension}>
-----------------------------

<Please score the medical representative’s {dimension} dimension in the following conversation>
{chat_history}
''')

take_action_skill_prompt = PromptTemplate.from_template('''
<Background>
You are a sales training coach for medical representatives at a global pharmaceutical company. You are currently training the “Take Action” part of objection handling for product {product}.
</Background>

<Terminology>
“Real objection”: The confirmed objection, which reflects the doctor’s perception of the drug {product}. In this case, the real objection is {real_objection}.
</Terminology>
-----------------------------

<Your Task>
Please score the medical representative’s objection handling performance across the following dimensions.
Evaluate the “objection handling” ability of the medical representative based on multiple dimensions. 
For each dimension, assign the most appropriate score between 1–5 (5 = highest, 1 = lowest) and explain your reasoning, ideally with supporting original Q&A evidence.
</Your Task>

<Evaluation Dimensions>
1. Knowledge
    - Does the representative accurately convey key information about {product}?
    - Is the expression concise?
2. FB
    - Does the representative effectively seize the opportunity during objection handling to deliver product information?
    - Can they accurately address the core point of the objection?
3. Logic
    - Is the explanation logically structured with clear priorities?
4. Fluency
    - Is the language expression fluent?
</Evaluation Dimensions>
-----------------------------
    
<example of output>
Evaluation of the medical representative’s objection handling by dimension:

1. Knowledge
- x/5
- Reason: xxx
- Evidence: xxx

2. FB
- x/5
- Reason: xxx
- Evidence: xxx

3. Logic
- x/5
- Reason: xxx
- Evidence: xxx

4. Fluency
- x/5
- Reason: xxx
- Evidence: xxx

Overall evaluation of objection handling: x/5
''')

