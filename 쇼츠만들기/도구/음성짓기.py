"""장면 JSON의 «말»을(숫자·영어는 읽기 꼴로 바꿔) 장면마다 녹음 + 낱말 시각 → 영상틀/public/
기본 목소리 = 수퍼토닉 M1(남자) · 빠르기 1.3
 목소리 엔진 고르기: JSON 맨 위 "목소리": {"엔진": "일레븐랩스", "이름": "<목소리 ID>"} 로 적으면 유료 일레븐랩스(환경변수 ELEVENLABS_API_KEY 필요)
  · 수퍼토닉 = 무료 CPU 모델(F1~F5 여성 · M1~M5 남성) · 일레븐랩스 = 유료(고를 때만)
  · 수퍼토닉은 낱말 시각을 안 줘서 말한 구간(앞뒤 무음 뺌)을 낱말 글자 수 비율로 나눔 · 소리 크기는 −14 LUFS로 맞춤(안 맞추면 −24.5로 게이트 불통)
 실행: python3 음성짓기.py <장면.json>"""
import os, sys, json, base64, re, time, subprocess, tempfile, urllib.request
from pathlib import Path
from 읽기바꿈 import 읽기, 남은것   # 녹음 전 읽기 꼴 바꾸기·검수(근거 youtu.be/upJhz8I40b0)
from 자리 import 공개, 파이썬 as 수퍼토닉


def 녹음(글):
    열쇠 = os.environ.get('ELEVENLABS_API_KEY') or sys.exit('일레븐랩스를 쓰려면 환경변수 ELEVENLABS_API_KEY 에 열쇠를 넣으세요')
    요청 = urllib.request.Request(
        'https://api.elevenlabs.io/v1/text-to-speech/%s/with-timestamps' % 목소리,
        data=json.dumps({'text': 글, 'model_id': 'eleven_multilingual_v2',
                         'voice_settings': {'stability': 0.5, 'similarity_boost': 0.75, 'speed': 빠르기}}).encode(),
        headers={'xi-api-key': 열쇠, 'Content-Type': 'application/json'})
    return json.load(urllib.request.urlopen(요청, timeout=120))


def 수퍼토닉녹음(일, 목소리=None, 빠르기=None):
    목소리 = 목소리 or globals()['목소리']; 빠르기 = 빠르기 if 빠르기 is not None else globals()['빠르기']
    """일 = [(번호, 읽기 글)] → {번호: (mp3 저장 · 낱말 목록)} · wav는 임시 폴더(저절로 사라짐)"""
    with tempfile.TemporaryDirectory() as 임시:
        목록 = [[글, '%s/%d.wav' % (임시, i)] for i, 글 in 일]
        Path(임시, '일.json').write_text(json.dumps(목록, ensure_ascii=False))
        r = subprocess.run(['nice', '-n', '15', str(수퍼토닉), str(Path(__file__).parent / '수퍼토닉녹음.py'), 목소리, str(빠르기), 임시 + '/일.json'],
                           capture_output=True, text=True)
        구간 = {json.loads(l[3:])[0]: json.loads(l[3:])[1:] for l in r.stdout.splitlines() if l.startswith('구간 ')}
        if r.returncode or len(구간) != len(목록):
            sys.exit('수퍼토닉 녹음 실패: ' + r.stderr[-400:])
        out = {}
        for i, 글 in 일:
            wav = '%s/%d.wav' % (임시, i)
            시작, 끝, _ = 구간[wav]
            앞 = max(시작 - 0.08, 0)   # 앞 무음은 0.08초만 남기고 자름(장면 사이 빈 소리 줄임)
            subprocess.run(['nice', '-n', '15', 'ffmpeg', '-v', 'error', '-y', '-ss', str(앞), '-i', wav, '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-codec:a', 'libmp3lame', '-b:a', '192k',
                            str(공개 / 이름 / ('%d.mp3' % i))], check=True)
            시작, 끝 = 시작 - 앞, 끝 - 앞
            낱 = 글.split(' ')
            전체, 쌓 = sum(len(x) for x in 낱), 0
            out[i] = []
            for x in 낱:   # 말한 구간을 낱말 글자 수 비율로 나눔
                out[i].append({'글': x, '시작': round(시작 + (끝 - 시작) * 쌓 / 전체, 3), '끝': round(시작 + (끝 - 시작) * (쌓 + len(x)) / 전체, 3)})
                쌓 += len(x)
        return out


def 낱말(정렬):
    out, 지금 = [], None
    for c, s, e in zip(정렬['characters'], 정렬['character_start_times_seconds'], 정렬['character_end_times_seconds']):
        if c.isspace():
            지금 = None
            continue
        if 지금 is None:
            지금 = {'글': '', '시작': s}
            out.append(지금)
        지금['글'] += c
        지금['끝'] = e
    return out


판 = json.load(open(sys.argv[1]))
# 배경음악은 기본으로 깐다 · JSON에 «음악»이 없으면 차분한 곡 · 꼬리에 곡 출처를 저절로 붙임
판.setdefault('음악', {'파일': '차분한.mp3', '크기': 0.187})
for 줄 in (공개 / '음악' / '출처.txt').read_text().splitlines():
    파일, 곡, 판허락 = [x.strip() for x in 줄.split('|')[:3]]
    if 파일 == 판['음악']['파일'] and 곡.split('.')[0][:20] not in 판.get('꼬리', ''):
        판['꼬리'] = (판.get('꼬리', '') + ' · 음악 %s(%s)' % (re.sub(r'\.(ogg|mp3|wav|oga)$', '', 곡)[:40], 판허락)).strip(' ·')
# 녹음 전 검수: 숫자·영어·한자가 남은 낱말이 있으면 녹음하지 않고 멈춤(끝코드 3)
막힘 = False
for i, 장 in enumerate(판['장면']):
    장['읽기'] = 읽기(장['말'])
    남 = 남은것(장['읽기'])
    if 남:
        막힘 = True
        print('장면 %d 읽기 꼴로 못 바꾼 낱말: %s' % (i, 남))
if 막힘:
    print('읽기사전.json에 더하거나 대본을 고친 뒤 다시 하세요(녹음 안 함).')
    sys.exit(3)
이름 = Path(sys.argv[1]).stem
(공개 / 이름).mkdir(parents=True, exist_ok=True)
엔진 = 판.get('목소리', {}).get('엔진', '수퍼토닉')
목소리 = 판.get('목소리', {}).get('이름', 'EST9Ui6982FZPSi7gCHi' if 엔진 == '일레븐랩스' else 'M1')
빠르기 = 판.get('목소리', {}).get('빠르기', 1.3 if 엔진 == '수퍼토닉' else 1.0)
표 = '%s:%s:%s' % (엔진, 목소리, 빠르기)   # 캐시 열쇠 = 읽기 꼴 + 엔진·목소리·빠르기 (바뀌면 다시 녹음)
옛 = {}
if (공개 / ('%s.json' % 이름)).exists():   # 같은 읽기 꼴·같은 목소리는 다시 녹음하지 않음(일레븐랩스 글자 수 아낌) · «읽기»·«표»가 없는 옛 JSON이면 다시 녹음
    옛 = {(s['읽기'], s.get('표')): s for s in json.load(open(공개 / ('%s.json' % 이름)))['장면'] if s.get('낱말') and s.get('읽기')}
시작 = time.time()
새 = {}
# ★장면별 목소리(2026-11-05 오너 지시 — 남녀 교대 나레이션): 장면에 "목소리"가 있으면 그것을 쓴다.
def 장면표(장):
    v = 장.get('목소리') or {}
    return '%s:%s:%s' % (v.get('엔진', 엔진), v.get('이름', 목소리), v.get('빠르기', 빠르기))
for 장 in 판['장면']:
    장['_표'] = 장면표(장)
if 엔진 == '수퍼토닉':   # 새로 녹음할 장면만, «목소리 묶음»별로(모델은 묶음당 한 번)
    남은 = [(i, 장) for i, 장 in enumerate(판['장면'])
            if not ((공개 / 옛[(장['읽기'], 장['_표'])]['소리']).exists() if (장['읽기'], 장['_표']) in 옛 else False)]
    묶음 = {}
    for i, 장 in 남은: 묶음.setdefault(장['_표'], []).append((i, 장['읽기']))
    for 표키, 일 in 묶음.items():
        _, 이름2, 빠2 = 표키.split(':')
        새.update(수퍼토닉녹음(일, 이름2, float(빠2)))
for i, 장 in enumerate(판['장면']):
    장['소리'] = '%s/%d.mp3' % (이름, i)
    장['표'] = 장['_표']
    전 = 옛.get((장['읽기'], 장['_표']))
    if i in 새:
        장['낱말'] = 새[i]
        원 = 장['말'].split(' ')   # 소리는 읽기 꼴, 자막은 원래 글(숫자)로
        if len(원) == len(장['낱말']):
            for 낱, 글 in zip(장['낱말'], 원):
                낱['글'] = 글
        else:
            print('⚠ 장면 %d 낱말 수 다름(원래 %d · 시각 %d) · 자막 글 바꾸지 않음' % (i, len(원), len(장['낱말'])))
    elif 전 and (공개 / 전['소리']).exists():
        if 전['소리'] != 장['소리']:
            (공개 / 장['소리']).write_bytes((공개 / 전['소리']).read_bytes())
        장['낱말'] = 전['낱말']
    else:
        r = 녹음(장['읽기'])
        (공개 / 장['소리']).write_bytes(base64.b64decode(r['audio_base64']))
        장['낱말'] = 낱말(r['alignment'])
        원 = 장['말'].split(' ')   # 소리는 읽기 꼴, 자막은 원래 글(숫자)로
        if len(원) == len(장['낱말']):
            for 낱, 글 in zip(장['낱말'], 원):
                낱['글'] = 글
        else:
            print('⚠ 장면 %d 낱말 수 다름(원래 %d · 시각 %d) · 자막 글 바꾸지 않음' % (i, len(원), len(장['낱말'])))
    장['길이'] = 장['낱말'][-1]['끝'] + 0.35
    # ★가드(2026-11-05): 기록 길이와 실제 오디오 길이가 어긋나면 캐시가 «다른 장면의 파일»을 물린 것이다.
    #   2026-11-05 실측 사고: 장면 13 이 장면 9 의 mp3(10.944초)를 물고 길이는 8.7 로 기록 → 끝이 잘리고 «다른 말»을 했다.
    try:
        실길이 = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                                      '-of', 'csv=p=0', str(공개 / 장['소리'])],
                                     capture_output=True, text=True).stdout.strip())
        if abs(실길이 - 장['길이']) > 0.5:
            sys.exit('⛔장면 %d 길이 어긋남: 기록 %.2f초 vs 실제 오디오 %.3f초 — 캐시가 다른 장면 파일을 물었다. '
                     '영상틀/public/%s.json 과 영상틀/public/%s/ 의 mp3 를 지우고 다시 실행하라.'
                     % (i, 장['길이'], 실길이, 이름, 이름))
    except FileNotFoundError:
        pass   # ffprobe 없으면 가드 생략(설치.sh가 ffprobe를 요구하므로 정상 경로에선 항상 있다)
    print(i, round(장['길이'], 2), '초', 장['_표'].split(':')[1])
for 장 in 판['장면']: 장.pop('_표', None)
json.dump(판, open(공개 / ('%s.json' % 이름), 'w'), ensure_ascii=False)
print('합', round(sum(장['길이'] for 장 in 판['장면']), 1), '초 · 엔진', 표, '· 녹음 걸린 시간', round(time.time() - 시작, 1), '초')
