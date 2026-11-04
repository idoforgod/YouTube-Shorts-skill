"""수퍼토닉 3(무료 · CPU) 녹음 — 음성짓기.py가 수퍼토닉 전용 파이썬 환경으로 부른다.
 실행: 수퍼토닉/.venv/bin/python 수퍼토닉녹음.py 목소리 빠르기 <일.json>   일.json = [[글, 저장할.wav], …]  (모델은 한 번만 불러옴)
 출력 «구간 [wav, 말시작초, 말끝초, 전체초]» 한 줄씩"""
import sys, json
import numpy as np
from 자리 import 수퍼토닉 as 기본
sys.path.insert(0, str(기본 / 'py'))
import soundfile as sf
from helper import load_text_to_speech, load_voice_style

목소리, 빠르기, 일 = sys.argv[1], float(sys.argv[2]), json.load(open(sys.argv[3]))
tts = load_text_to_speech(str(기본 / 'assets/onnx'), False)
스타일 = load_voice_style([str(기본 / 'assets/voice_styles' / (목소리 + '.json'))])
for 글, 경로 in 일:
    wav, 길이 = tts(글, 'ko', 스타일, 8, 빠르기)
    소리 = wav[0, :int(tts.sample_rate * 길이[0].item())]
    sf.write(경로, 소리, tts.sample_rate)
    창 = tts.sample_rate // 100   # 10ms 칸마다 크기를 재서 −40dB(가장 큰 칸 기준)보다 큰 첫·끝 칸 = 실제 말한 구간(앞뒤 무음 뺌)
    크기 = np.sqrt((소리[:len(소리) // 창 * 창].reshape(-1, 창) ** 2).mean(1))
    말 = np.where(크기 > 크기.max() * 0.01)[0]
    print('구간', json.dumps([경로, round(float(말[0]) / 100, 3), round(float(말[-1] + 1) / 100, 3), round(float(길이[0]), 2)]), flush=True)
