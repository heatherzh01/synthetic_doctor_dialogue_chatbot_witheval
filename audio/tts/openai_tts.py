from src.llm_init import init_openai
import datetime


def tts_openai(text, model='tts-1', mp3_path='./openai_test.mp3', voice="男", speed=5):
    assert(model in ['tts-1', 'tts-1-hd'])
    voice_mapper = {
        "女": 'shimmer',
        "男": 'onyx'
    }
    now = datetime.datetime.now()
    client = init_openai()
    response = client.audio.speech.create(
        model=model,
        voice=voice_mapper[voice],
        input=text
    )
    response.stream_to_file(mp3_path[:64])
    time_cost = (datetime.datetime.now() - now).total_seconds()
    return mp3_path, time_cost
