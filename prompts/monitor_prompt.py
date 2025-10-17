from langchain.prompts import PromptTemplate


clarify_process_schema = {
    "type": "object",
    "properties": {
        "stage_type": {
            "type": "string",
            "enum": [
                "Clarify Objection",
                "Resolve Objection",
                "Irrelevant Input"
            ],
            "description": "Stage classification"
        },
        "process_type": {
            "type": "string",
            "enum": [
                "Ask About Focus",
                "Ask Source",
                "Ask Treatment Philosophy",
                "Ask Treatment Experience",
                "Irrelevant Inquiry"
            ],
            "description": "Motivation type of the inquiry"
        },
        "is_confirmation": {
            "type": "string",
            "enum": [
                "Yes",
                "No"
            ],
            "description": "Whether the semantics are exactly the same"
        }
    },
    "required": ["stage_type", "process_type", "is_confirmation"]
}

clarify_process_prompt = PromptTemplate.from_template('''
<Background>
You are a sales conversation trainer for medical representatives, training sales reps for {product}.
1. You are good at judging whether the rep is clarifying questions with the doctor or conveying product information.
2. You are good at judging whether the rep is confirming the doctor’s objection to {product}.
3. You are good at identifying the motivation type of the rep’s inquiry: "Ask About Focus", "Ask Source", "Ask Treatment Philosophy", "Ask Treatment Experience".
</Background>
-----------------------------

<Dialogue Context>
{chat_history}
</Dialogue Context>

<Inquiry>
{input}
</Inquiry>
-----------------------------

<Your Task>
1. Determine whether “{input}” is asking/clarifying with the doctor (i.e., “Clarify Objection”), or conveying product information to the doctor (i.e., “Resolve Objection”). Answer with “Clarify Objection” or “Resolve Objection”.
- “Clarify Objection” clarifies specifics of the doctor’s objection through questions. Typical examples:
    example 1: Between cardiovascular benefit and mode of administration, which do you care more about?
    example 2: Which specific aspect of cardiovascular benefit are you referring to?
    example 3: For patients combined with T2DM, which changes do you most hope to see?
    example 4: For patients with cardiometabolic risk factors, how would you choose between these two products?
    example 5: Do you think the intervention timing for these two products is the same?
    example 6: Is this situation common?
    example 7: What kind of patients usually find it hard to persist?
    example 8: When you encounter this situation, how do you usually handle it?
    example 9: For which patients do you pay particular attention to the occurrence of cardiovascular endpoints?
    example 10: When they use {product}, do they understand the possible GI side effects and related dietary precautions?
- “Resolve Objection” is one-way delivery of product information or guidance on using {product}. Typical examples:
    example 1: Meta-analyses of GLP-1RA vs SGLT-2i CVOTs show GLP-1RA reduces risks of MI and stroke (ASCVD endpoints), suggesting an anti-atherosclerotic effect; SGLT-2i do not reduce stroke risk, mainly lowering heart failure events.
    example 2: Thus, the 2019 ESC/EASD cardiovascular guidelines indicate GLP-1RA benefits mainly come from reductions in atherosclerosis-related events, while SGLT-2i benefits mainly come from reductions in heart failure–related events.
    example 3: Although {product} is injectable, the device is very easy to use, and the needle is thinner than a phlebotomy needle. Most patients report almost no pain, so they can self-inject long term to sustain benefit.
    example 4: For T2DM with coronary disease or cardiometabolic risk factors, you can recommend early use of {product} to improve cardiometabolic health and achieve CV benefit.
    example 5: The GI adverse reactions of {product} are usually transient; the label states they are generally mild to moderate and short in duration.
    example 6: Also advise light meals and small, frequent meals early on to mitigate side effects.
    example 7: Your approach is excellent—dose titration can improve GI tolerability.
    example 8: As symptoms decrease in severity and frequency over time, encourage patients to avoid stopping therapy to prevent delaying disease management and achieve optimal outcomes.
    example 9: You can enroll patients in the {product}-care program for related resources, which can help patients and reduce your communication burden—does that work for you?
    example 10: Since you recognize the CV benefit of {product}, helping patients better understand and adhere will benefit more patients; you can continue to confidently use semaglutide therapy for those with CAD or cardiometabolic risk.
- If it is neither “Clarify Objection” nor “Resolve Objection,” answer “Irrelevant Input,” e.g., content entirely unrelated to {product}.
    
2. Identify the motivation type that best matches “{input}” based on the definitions:
- Choose the closest from ["Ask About Focus","Ask Source","Ask Treatment Philosophy","Ask Treatment Experience"].
- Definitions: {definition}
- Example sets: {few_shots_examples}
- If none fit, output "Irrelevant Inquiry".
- If you cannot clearly determine the meaning of the inquiry, classify it as "Irrelevant Inquiry" (e.g., “process_type”, gibberish, etc.).
- let's think step by step
- do not make up an answer

3. Determine whether “{input}” asks/expresses semantics strictly identical to “your {real_objection}”. Answer “Yes” or “No”.
</Your Task>
-----------------------------

<Inquiry>
{input}
''')

take_action_process_schema = {
    "type": "object",
    "properties": {
        "stage_type": {
            "type": "string",
            "enum": [
                "Clarify Objection",
                "Resolve Objection",
                "Irrelevant Input"
            ],
            "description": "Stage classification"
        },
        "process_type": {
            "type": "string",
            "enum": [
                "Provide Evidence",
                "Deliver FB",
                "Convey Overall Advantages and Benefits",
                "Convey Expert Advice and Case Experience",
                "Unable to Determine"
            ],
            "description": "Type of content conveyed by the representative"
        },
        "is_in_standard_answer": {
            "type": "string",
            "enum": [
                "Yes",
                "No"
            ],
            "description": "Whether the conveyed content appears in the standard answers"
        }
    },
    "required": ["stage_type", "process_type", "is_in_standard_answer"]
}

take_action_process_prompt = PromptTemplate.from_template('''
<Background>
You are a sales conversation trainer for medical representatives, training sales reps for {product}.
1. You are good at judging whether the rep is clarifying questions with the doctor or conveying product information.
2. You are good at identifying the type of information conveyed: "Provide Evidence", "Deliver FB", "Convey Overall Advantages and Benefits", "Convey Expert Advice and Case Experience".
</Background>
-----------------------------

<Dialogue Context>
{chat_history}
</Dialogue Context>

<Input>
{input}
</Input>
-----------------------------

<Your Task>
1. Determine whether “{input}” is asking/clarifying with the doctor (i.e., “Clarify Objection”), or conveying product information (i.e., “Resolve Objection”). Answer with “Clarify Objection” or “Resolve Objection”.
- “Clarify Objection” clarifies specifics of the doctor’s objection through questions. Typical examples:
    example 1: Between cardiovascular benefit and mode of administration, which do you care more about?
    example 2: Which specific aspect of cardiovascular benefit are you referring to?
    example 3: For patients combined with T2DM, which changes do you most hope to see?
    example 4: For patients with cardiometabolic risk factors, how would you choose between these two products?
    example 5: Do you think the intervention timing for these two products is the same?
    example 6: Is this situation common?
    example 7: What kind of patients usually find it hard to persist?
    example 8: When you encounter this situation, how do you usually handle it?
    example 9: For which patients do you pay particular attention to the occurrence of cardiovascular endpoints?
    example 10: When they use {product}, do they understand the possible GI side effects and related dietary precautions?
- “Resolve Objection” is one-way delivery of product information or guidance on using {product}. Typical examples:
    example 1: Meta-analyses of GLP-1RA vs SGLT-2i CVOTs show GLP-1RA reduces risks of MI and stroke (ASCVD endpoints), suggesting an anti-atherosclerotic effect; SGLT-2i do not reduce stroke risk, mainly lowering heart failure events.
    example 2: Thus, the 2019 ESC/EASD cardiovascular guidelines indicate GLP-1RA benefits mainly come from reductions in atherosclerosis-related events, while SGLT-2i benefits mainly come from reductions in heart failure–related events.
    example 3: Although {product} is injectable, the device is very easy to use, and the needle is thinner than a phlebotomy needle. Most patients report almost no pain, so they can self-inject long term to sustain benefit.
    example 4: For T2DM with coronary disease or cardiometabolic risk factors, you can recommend early use of {product} to improve cardiometabolic health and achieve CV benefit.
    example 5: The GI adverse reactions of {product} are usually transient; the label states they are generally mild to moderate and short in duration.
    example 6: Also advise light meals and small, frequent meals early on to mitigate side effects.
    example 7: Your approach is excellent—dose titration can improve GI tolerability.
    example 8: As symptoms decrease in severity and frequency over time, encourage patients to avoid stopping therapy to prevent delaying disease management and achieve optimal outcomes.
    example 9: You can enroll patients in the {product}-care program for related resources, which can help patients and reduce your communication burden—does that work for you?
    example 10: Since you recognize the CV benefit of {product}, helping patients better understand and adhere will benefit more patients; you can continue to confidently use semaglutide therapy for those with CAD or cardiometabolic risk.
- If it is neither “Clarify Objection” nor “Resolve Objection,” answer “Irrelevant Input,” e.g., content entirely unrelated to {product}.

2. Identify the motivation type that best matches “{input}” based on the definitions:
- Choose the closest from ["Ask About Focus","Ask Source","Ask Treatment Philosophy","Ask Treatment Experience"].
- Definitions: {definition}
- Example sets: {few_shots_examples}
- If none fit, output "Irrelevant Inquiry".
- If you cannot clearly determine the meaning, classify it as "Irrelevant Inquiry" (e.g., “process_type”, gibberish, etc.).
- let's think step by step
- do not make up an answer

3. Using semantics and specific metric numbers/details, determine whether “{input}” conveys exactly the same meaning as any item in the standard answers.
- Answer “Yes” or “No” only; do not output your reasoning.
- Standard answers: {standard_answer}
</Your Task>
-----------------------------

<Input>
{input}
''')

clarify_skills_schema = {
    "type": "object",
    "properties": {
        "从关心患者/医生角度出发来设计提问的得分": {
            "type": "number",
            "description": "Score for designing questions from the perspective of caring about patients/doctors",
        },
        "提问有逻辑性的得分": {
            "type": "number",
            "description": "Score for logical questioning",
        },
        "询问客户关心的并聚焦的异议相关问题的得分": {
            "type": "number",
            "description": "Score for asking objection-related questions that the customer cares about and are focused",
        },
        "澄清和追问细节的得分": {
            "type": "number",
            "description": "Score for clarifying and probing into details",
        },
    },
    "required": [
        "从关心患者/医生角度出发来设计提问的得分",
        "提问有逻辑性的得分",
        "询问客户关心的并聚焦的异议相关问题的得分",
        "澄清和追问细节的得分"
    ]
}

clarify_skills_prompt = PromptTemplate.from_template('''
<Background>
You are a sales training coach for medical representatives at a global pharmaceutical company. You are currently training the “Clarify” part of objection handling for product {product}.
</Background>
-----------------------------

<Terminology>
“Objection”: The doctor’s perception regarding the drug {product}.
“Preset objection”: The doctor’s initial/superficial perception of {product} before the conversation begins. In this case: {preset_objection}.
“Real objection”: The underlying prescribing habits or perceptions revealed during the conversation—i.e., the true objection to {product}. In this case: {real_objection}.
“The Clarify part of objection handling”: The process by which the rep, through multiple rounds of Q&A, gradually reveals and confirms the doctor’s real objection.
</Terminology>
-----------------------------

<Evaluation Dimensions>
{definition}
</Evaluation Dimensions>

<Your Task>
Evaluate the rep’s “Clarify” skills across the above dimensions.
- Give the most appropriate score between 1–5 (5 = best, 1 = worst)
- let's think step by step
- do not make up an answer
</Your Task>
-----------------------------

<examples>
{few_shots_examples}
</examples>
-----------------------------

<Chat History>
{chat_history}
</Chat History>

<Please score the following sentence’s skill level>
{input}
''')

take_action_skills_schema = {
    "type": "object",
    "properties": {
        "围绕关键信息传递FB的得分": {
            "type": "number",
            "description": "Score for delivering FB centered on key information",
        },
        "逻辑清晰的得分": {
            "type": "number",
            "description": "Score for clarity of logic",
        },
        "语言表达清晰流畅的得分": {
            "type": "number",
            "description": "Score for clarity and fluency of expression",
        }
    },
    "required": [
        "围绕关键信息传递FB的得分",
        "逻辑清晰的得分",
        "语言表达清晰流畅的得分"
    ]
}

take_action_skills_prompt = PromptTemplate.from_template('''
<Background>
You are a sales training coach for medical representatives at a global pharmaceutical company. You are currently training the “Take Action” part of objection handling for product {product}.
</Background>

<Terminology>
“Real objection”: The confirmed objection—the doctor’s perception regarding {product}. In this case: {real_objection}.
</Terminology>
-----------------------------

<Evaluation Dimensions>
{definition}
</Evaluation Dimensions>

<Your Task>
Evaluate the rep’s “Take Action (Clarify)” skills across the above dimensions.
- Give the most appropriate score between 1–5 (5 = best, 1 = worst)
- let's think step by step
- do not make up an answer
</Your Task>
-----------------------------

<examples>
{few_shots_examples}
</examples>
-----------------------------

<Chat History>
{chat_history}
</Chat History>

<Please score the following sentence’s skill level>
{input}
''')
