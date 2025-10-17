# Synthetic Doctor Chatbot for internal training (with eval)


Short summary
- A Streamlit-based virtual HCP (doctor) chatbot for internal sales training with live monitoring, automated evaluation, and multi-provider TTS.
- Central runtime unit: [`Session`](src/session.py) which drives conversation, TTS, monitoring and vector-knowledge lookup.

Quick start
1. Install dependencies:
```sh
pip install -r requirements.txt
```
(see [requirements.txt](requirements.txt))

2. Run the Streamlit demo:
```sh
streamlit run demo/HelloNovo.py
```
Demo pages:
- [demo/HelloNovo.py](demo/HelloNovo.py)
- [demo/pages/01_医生对话.py](demo/pages/01_医生对话.py)
- [demo/pages/02 对话评价.py](demo/pages/02 对话评价.py)
- [demo/pages/03 快问快答.py](demo/pages/03 快问快答.py)

3. Try example notebooks:
- [notebooks/SDKtest.ipynb](notebooks/SDKtest.ipynb)
- [notebooks/TTS_test.ipynb](notebooks/TTS_test.ipynb)

Core modules and main functions (quick reference)
- Session and chat flow
  - Class: [`Session`](src/session.py) — primary session object managing hcp, objection, rep, chat history, tokens and TTS.
    - [`Session.chat`](src/session.py) — single-response LLM call (sync).
    - [`Session.chat_stream`](src/session.py) — streaming LLM call for real-time UI.
    - [`Session.hcp_initiate`](src/session.py) / [`Session.hcp_initiate_direct`](src/session.py) — generate HCP initial turn(s).
    - [`Session.display_tts`](src/session.py) — invoke TTS providers and (in notebooks) play audio.
    - Knowledge helpers: [`Session.get_product_knowledge`](src/session.py), [`Session.get_dept_knowledge`](src/session.py), [`Session.get_sustain_knowledge`](src/session.py)
    - Utility: [`Session.get_task_instruction`](src/session.py), [`Session.append`](src/session.py)

- LLM inference wrappers
  - [`gpt_query`](src/llm_inference.py) — non-streaming call, returns model response & cost.
  - [`gpt_query_stream`](src/llm_inference.py) — streaming call (yields chunks).
  - [`get_embedding`](src/llm_inference.py) — embedding helper.
  - [`clean_gpt_answers`](src/llm_inference.py) — cleans/parses model outputs.

- Vector knowledge (Chroma)
  - [`get_similar_text`](src/llm_vectorstores.py) — query a Chroma vectorstore for relevant chunks.
  - [`build_vectorstores`](src/llm_vectorstores.py) — build indexes from documents.

- Monitoring (real-time feedback)
  - Class: [`Monitor`](src/session_monitor.py)
    - Process classification: [`Monitor.c_process`](src/session_monitor.py), [`Monitor.t_process`](src/session_monitor.py)
    - Skill scoring: [`Monitor.c_skills`](src/session_monitor.py), [`Monitor.t_skills`](src/session_monitor.py)
    - Guidance helpers: [`Monitor.c_guide_process`](src/session_monitor.py), [`Monitor.t_guide_process`](src/session_monitor.py)
  - Prompts & schemas: [prompts/monitor_prompt.py](prompts/monitor_prompt.py)

- Evaluation (post-hoc scoring)
  - Class: [`Evaluator`](src/session_evaluator.py)
    - Clarify & Take-Action evaluations: [`Evaluator.evaluate_clarify_*`](src/session_evaluator.py), [`Evaluator.evaluate_take_action_*`](src/session_evaluator.py)
    - Save results: [`Evaluator.save`](src/session_evaluator.py)
  - Prompts: [prompts/evaluator_prompt.py](prompts/evaluator_prompt.py)

- Quick Quiz
  - Class: [`Quiz`](src/quick_quiz.py)
    - [`Quiz.get_question`](src/quick_quiz.py)
    - [`Quiz.evaluate_question`](src/quick_quiz.py) / [`Quiz.evaluate`](src/quick_quiz.py)
  - Demo page: [demo/pages/03 快问快答.py](demo/pages/03 快问快答.py)
  - SDK usage: [sdk/module_4.py](sdk/module_4.py)

- Static dataclasses & I/O
  - Dataclasses: [`VirtualHcp`](src/static_classes.py), [`ObjectionInstance`](src/static_classes.py), [`QuickQuestion`](src/static_classes.py)
    - File: [src/static_classes.py](src/static_classes.py)
  - I/O helpers: [src/utils/io.py](src/utils/io.py)
    - Key functions: [`load_objection_case_from_yaml`](src/utils/io.py), [`load_rep_from_yaml`](src/utils/io.py), [`load_quick_quiz_questions_from_excel`](src/utils/io.py), [`load_evaluation_criterion_from_yaml`](src/utils/io.py)

- TTS providers
  - OpenAI TTS: [`tts_openai`](audio/tts/openai_tts.py) — [audio/tts/openai_tts.py](audio/tts/openai_tts.py)
  - Baidu TTS: functions in [audio/tts/baidu_tts.py](audio/tts/baidu_tts.py) — e.g. [`tts_baidu_short`](audio/tts/baidu_tts.py), [`tts_baidu_long_create`](audio/tts/baidu_tts.py), [`tts_baidu_long_query`](audio/tts/baidu_tts.py)
  - Iflytek TTS: [`tts_iflytek`](audio/tts/iflytek_tts.py)

SDK entrypoints
- Module 1 (conversation): [sdk/module_1.py](sdk/module_1.py) — builds `Session` and drives chat turns. See class [`Module_1`](sdk/module_1.py).
- Module 2 (monitor): [sdk/module_2.py](sdk/module_2.py) — runs `Monitor` and returns structured monitor results. See class [`Module_2`](sdk/module_2.py).
- Module 3 (evaluator): [sdk/module_3.py](sdk/module_3.py) — loads a saved chat history and returns evaluation results. See class [`Module_3`](sdk/module_3.py).
- Module 4 (quick quiz): [sdk/module_4.py](sdk/module_4.py) — wraps [`Quiz`](src/quick_quiz.py).

Typical workflows / examples
- Interactive demo (Streamlit)
  - Start Streamlit: `streamlit run demo/HelloNovo.py`.
  - Create session: UI calls [`Session`](src/session.py) using data loaded from [src/utils/io.py](src/utils/io.py).

- Notebook / SDK quick test
  - See [notebooks/SDKtest.ipynb](notebooks/SDKtest.ipynb) for examples calling:
    - [`Module_1.get_response`](sdk/module_1.py)
    - [`Module_2.get_response`](sdk/module_2.py)
    - [`Module_3.get_response`](sdk/module_3.py)
    - [`Module_4.get_response`](sdk/module_4.py)

- Save / load sessions and evaluation
  - Sessions are pickled and saved under `../output/chat_history` by `Session.save` ([src/session.py](src/session.py)).
  - Evaluator can load saved sessions in [`Module_3`](sdk/module_3.py) or via [`Evaluator.set_session`](src/session_evaluator.py).

Configuration / credentials
- LLM client initialization and keys: see [src/llm_init.py](src/llm_init.py). Set provider keys as environment variables or in initialization helpers before running demos.
- TTS provider credentials are embedded/expected for Baidu/Iflytek (see [audio/tts/baidu_tts.py](audio/tts/baidu_tts.py) and [audio/tts/iflytek_tts.py](audio/tts/iflytek_tts.py)). Replace keys where necessary.

Where to look (important files)
- Core session & flow: [src/session.py](src/session.py) — see [`Session`](src/session.py)
- LLM helpers: [src/llm_inference.py](src/llm_inference.py) — see [`gpt_query`](src/llm_inference.py), [`gpt_query_stream`](src/llm_inference.py)
- Vectorstore: [src/llm_vectorstores.py](src/llm_vectorstores.py)
- Monitor: [src/session_monitor.py](src/session_monitor.py) — see [`Monitor`](src/session_monitor.py)
- Evaluator: [src/session_evaluator.py](src/session_evaluator.py) — see [`Evaluator`](src/session_evaluator.py)
- Prompts: [prompts/](prompts/) — [`prompts/hcp_chat_prompt.py`](prompts/hcp_chat_prompt.py), [`prompts/monitor_prompt.py`](prompts/monitor_prompt.py), [`prompts/evaluator_prompt.py`](prompts/evaluator_prompt.py)
- TTS: [audio/tts/](audio/tts/) — [`audio/tts/baidu_tts.py`](audio/tts/baidu_tts.py), [`audio/tts/iflytek_tts.py`](audio/tts/iflytek_tts.py), [`audio/tts/openai_tts.py`](audio/tts/openai_tts.py)
- SDK: [sdk/](sdk/) — see each [sdk/module_1.py](sdk/module_1.py), [sdk/module_2.py](sdk/module_2.py), [sdk/module_3.py](sdk/module_3.py), [sdk/module_4.py](sdk/module_4.py)
- Data & assets: [data/](data/) (hcps, objections, criterions, vectorstores, audios)

Small code snippets

- Create a Session (example):
```python
# from sdk/module_1.py usage
from sdk.module_1 import Module_1
mod = Module_1()
resp = mod.get_response(input_json_str)
print(resp)
```

- Run quick quiz via SDK:
```python
# sdk/module_4.py usage
from sdk.module_4 import Module_4
sdk4 = Module_4()
sdk4.get_response(input_json_str)   # prints JSON result for quick quiz
```

Notes & tips
- Use streaming (`Session.chat_stream`, [`gpt_query_stream`](src/llm_inference.py)) for responsive UIs.
- Monitoring is optional — enable via `monitor=True` when creating [`Session`](src/session.py).
- Evaluator uses criteria YAMLs under `data/criterions/` — modify those to change scoring behavior (helpers: [`load_evaluation_criterion_from_yaml`](src/utils/io.py)).
- If a provider key is missing, LLM or TTS calls may fail; check [src/llm_init.py](src/llm_init.py) and TTS files.

