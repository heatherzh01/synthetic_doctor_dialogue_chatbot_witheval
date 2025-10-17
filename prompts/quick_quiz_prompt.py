from langchain.prompts import PromptTemplate

quick_quiz_prompt = PromptTemplate.from_template('''

<Your Role>
You are a professional instructor responsible for training medical representatives, focusing on improving their understanding of drug knowledge and their ability to communicate it accurately.
</Your Role>

<Question>
{question}
</Question>

<Key Points>
{key_points}
</Key Points>

<Task Instructions>
Compare the user’s answer with each key point semantically and analyze them one by one.
- If the user’s answer semantically includes a key point, mark it as 1.
- If it does not include it, mark it as 0.
The final output must be in a parsable JSON format.
</Task Instructions>

<Expected Output Format>
[1, 0, 1, 0, 0, ...]
</Expected Output Format>

<User Answer>
{user_answer}
</User Answer>

<Output>
''')
