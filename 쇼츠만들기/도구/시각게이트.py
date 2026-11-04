"""시각 게이트 — 쇼츠를 남에게 보내거나 올리기 전에 반드시 통과해야 하는 관문.
역할: 디자인 틀(검정 위·아래 띠 · 고정 2줄 제목 흰·노랑 · 가운데 그림 띠 · 테두리 자막 · 마지막 줄 빨강)과
화질·길이·소리 규격을 «기계로» 재서, 하나라도 어기면 «불통»으로 막는다. 통과해도 이어붙인 판(PNG)을 눈으로 한 번 더 본다.
 실행: python3 시각게이트.py 영상.mp4  → 같은 폴더에 «게이트_<이름>.md»와 «게이트_<이름>.png»(1초 간격 이어붙인 판)"""
import sys, json, subprocess, re
from pathlib import Path
from PIL import Image, ImageChops, ImageStat

영상 = Path(sys.argv[1])
일 = 영상.parent / ('_게이트_' + 영상.stem)
일.mkdir(exist_ok=True)


def 돌림(*a):
    return subprocess.run(a, capture_output=True, text=True).stdout + subprocess.run(a, capture_output=True, text=True).stderr


정보 = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_type,width,height,r_frame_rate,bit_rate:format=duration', '-of', 'json', str(영상)], capture_output=True, text=True).stdout)
비디오 = next(s for s in 정보['streams'] if s['codec_type'] == 'video')
소리있음 = any(s['codec_type'] == 'audio' for s in 정보['streams'])
길이 = float(정보['format']['duration'])
비트 = int(비디오.get('bit_rate', 0)) / 1e6
소리크기 = re.findall(r'I:\s+(-?[\d.]+) LUFS', 돌림('ffmpeg', '-v', 'info', '-i', str(영상), '-af', 'ebur128', '-f', 'null', '-'))
LUFS = float(소리크기[-1]) if 소리크기 else None

# 0.5초마다 화면 뜨기
for f in 일.glob('*.png'):
    f.unlink()
subprocess.run(['ffmpeg', '-v', 'error', '-i', str(영상), '-vf', 'fps=2', str(일 / 'f%04d.png')])
틀 = sorted(일.glob('f*.png'))


def 몫(im, box, 조건):
    x0, y0, x1, y1 = box
    n = hit = 0
    for y in range(y0, y1, 4):
        for x in range(x0, x1, 4):
            p = im.getpixel((x, y))
            n += 1
            hit += 조건(p)
    return hit / n


검정 = lambda p: sum(p) < 40
흰 = lambda p: min(p) > 200
노랑 = lambda p: p[0] > 200 and p[1] > 160 and p[2] < 90
빨강 = lambda p: p[0] > 200 and p[1] < 90 and p[2] < 90
밝음 = lambda p: sum(p) > 120

줄 = []
바뀜 = []
앞 = None
for i, f in enumerate(틀):
    im = Image.open(f).convert('RGB')
    띠 = im.crop((0, 430, 1080, 1500)).resize((108, 107))
    if 앞 is not None:
        바뀜.append(ImageStat.Stat(ImageChops.difference(띠, 앞)).mean[0] > 6)
    앞 = 띠
    줄.append({'초': i / 2,
              '위띠검정': 몫(im, (0, 0, 1080, 140), 검정) > 0.97 and 몫(im, (0, 405, 1080, 428), 검정) > 0.97,
              '제목흰': 몫(im, (60, 150, 1020, 262), 흰) > 0.04,
              '제목노랑': 몫(im, (60, 288, 1020, 400), 노랑) > 0.04,
              '아래띠비움': 몫(im, (0, 1590, 1080, 1920), 밝음) < 0.003,
              '자막': 몫(im, (40, 1330, 1040, 1460), lambda p: 흰(p) or 빨강(p)) > 0.02,
              '빨강자막': 몫(im, (40, 1330, 1040, 1460), 빨강) > 0.01})

# 가장 긴 «그림 띠 안 바뀜» 구간(초)
최장, 지금 = 0, 0
for b in 바뀜:
    지금 = 0 if b else 지금 + 0.5
    최장 = max(최장, 지금)
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-sseof', '-0.2', '-i', str(영상), '-frames:v', '1', str(일 / '끝.png')])
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(영상), '-frames:v', '1', str(일 / '첫.png')])
첫끝 = ImageStat.Stat(ImageChops.difference(Image.open(일 / '첫.png').convert('RGB').crop((0, 430, 1080, 1300)), Image.open(일 / '끝.png').convert('RGB').crop((0, 430, 1080, 1300)))).mean
끝장면빨강 = any(r['빨강자막'] for r in 줄[-8:])

검사 = [
    ('규격 1080×1920', 비디오['width'] == 1080 and 비디오['height'] == 1920, f"{비디오['width']}×{비디오['height']}"),
    ('길이 45~60초', 45 <= 길이 <= 60, f'{길이:.1f}초'),
    ('화질 초당 6메가 이상', 비트 >= 6, f'{비트:.1f}메가'),
    ('소리 있음 · 크기 -18~-10 LUFS', 소리있음 and LUFS is not None and -18 <= LUFS <= -10, f'{LUFS} LUFS'),
    ('위 검정 띠 모든 화면', all(r['위띠검정'] for r in 줄), f"{sum(r['위띠검정'] for r in 줄)}/{len(줄)}"),
    ('제목 1줄 흰 모든 화면', all(r['제목흰'] for r in 줄), f"{sum(r['제목흰'] for r in 줄)}/{len(줄)}"),
    ('제목 2줄 노랑 모든 화면', all(r['제목노랑'] for r in 줄), f"{sum(r['제목노랑'] for r in 줄)}/{len(줄)}"),
    ('아래 330px 비움(유튜브 버튼 자리)', all(r['아래띠비움'] for r in 줄), f"{sum(r['아래띠비움'] for r in 줄)}/{len(줄)}"),
    ('자막 있음 90% 이상', sum(r['자막'] for r in 줄) >= 0.9 * len(줄), f"{sum(r['자막'] for r in 줄)}/{len(줄)}"),
    ('그림 띠 4.5초 넘게 안 멈춤', 최장 <= 4.5, f'가장 긴 멈춤 {최장}초'),
    ('마지막 줄 빨강 자막', 끝장면빨강, '있음' if 끝장면빨강 else '없음'),
    ('끝 화면 = 첫 화면(되감기 고리 · 자막 줄 빼고)', max(첫끝) < 25, f'차이 {max(첫끝):.0f}'),
]
통과 = all(c[1] for c in 검사)

# 1초 간격 이어붙인 판(눈 검사용)
골라 = 틀[::2]
작 = [Image.open(f).convert('RGB').resize((216, 384)) for f in 골라]
열 = 10
판 = Image.new('RGB', (열 * 216, ((len(작) + 열 - 1) // 열) * 384))
for i, im in enumerate(작):
    판.paste(im, ((i % 열) * 216, (i // 열) * 384))
판.save(영상.parent / f'게이트_{영상.stem}.png')

글 = [f'# 시각 게이트 — {영상.name}', '', f"**판정: {'✅ 통과' if 통과 else '❌ 불통 — 보내지 않음'}**", '', '| 검사 | 결과 | 잰 값 |', '|---|---|---|']
글 += [f"| {n} | {'✅' if ok else '❌'} | {v} |" for n, ok, v in 검사]
글 += ['', f'눈 검사 판: 게이트_{영상.stem}.png (1초 간격) — 눈으로 직접 본다(글자 잘림·겹침·빈 화면·깨진 장면).']
(영상.parent / f'게이트_{영상.stem}.md').write_text('\n'.join(글))
print('\n'.join(글))
sys.exit(0 if 통과 else 1)
