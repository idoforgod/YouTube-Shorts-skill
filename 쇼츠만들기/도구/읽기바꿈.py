"""대본 → 음성 모델이 그대로 읽을 «읽기 꼴»로 바꾼다(숫자·%·단위·영어 약자 → 한글 소리).
근거: 샘 호트만 «2026 한국어 오픈소스 TTS 5가지 비교»(youtu.be/upJhz8I40b0) — 모든 음성 모델이 금액·날짜·버전·명령어를 자주 틀리게 읽음 →
녹음 직전에 사람이 읽는 꼴로 바꿔 넣고, 바꾸지 못한 것이 남으면 녹음 전에 멈춘다(검수 없이 생성했다가 «아차» 했다는 경험).
낱말 수는 바꾸지 않는다(띄어쓰기 그대로) → 자막은 원래 글(숫자)로, 소리는 읽기 꼴로.
 쓰임: from 읽기바꿈 import 읽기, 남은것   ·   python3 읽기바꿈.py "문장"  (시험)"""
import json, re, sys
from pathlib import Path

자리수 = '영일이삼사오육칠팔구'
고유 = {1: '한', 2: '두', 3: '세', 4: '네', 5: '다섯', 6: '여섯', 7: '일곱', 8: '여덟', 9: '아홉', 10: '열', 20: '스물', 30: '서른', 40: '마흔', 50: '쉰', 60: '예순', 70: '일흔', 80: '여든', 90: '아흔'}
고유단위 = ('개', '번', '살', '명', '가지', '마리', '잔', '시간', '권', '송이', '켤레', '대째')
사전 = json.loads((Path(__file__).parent / '읽기사전.json').read_text())


def 한자수(n: int) -> str:
    if n == 0:
        return '영'
    큰 = ['', '만', '억', '조']
    out, i = '', 0
    while n:
        n, 네 = divmod(n, 10000)
        if 네:
            조각 = ''
            for 값, 이름 in ((1000, '천'), (100, '백'), (10, '십'), (1, '')):
                d, 네 = divmod(네, 값)
                if d:
                    조각 += ('' if d == 1 and 이름 else 자리수[d]) + 이름
            if 조각 == '일' and 큰[i] == '만':
                조각 = ''
            out = 조각 + 큰[i] + out
        i += 1
    return out


def 고유수(n: int) -> str | None:
    if not 0 < n < 100:
        return None
    십, 일 = divmod(n, 10)
    return (고유[십 * 10] if 십 else '') + (고유[일] if 일 else '')


def 수(글: str, 뒤: str) -> str:
    글 = 글.replace(',', '')
    if '.' in 글:
        앞, 소 = 글.split('.')
        return 한자수(int(앞 or 0)) + '점' + ''.join(자리수[int(c)] for c in 소)
    n = int(글)
    if 뒤.startswith('월'):
        return {6: '유', 10: '시'}.get(n, 한자수(n))
    if 뒤.startswith(고유단위) and 고유수(n):
        return 고유수(n)
    return 한자수(n)


def 낱말읽기(t: str) -> str:
    for 원, 소리 in 사전.items():
        t = t.replace(원, 소리)
    t = re.sub(r'(\d[\d,]*(?:\.\d+)?)\s*~\s*(?=\d)', lambda m: m.group(1) + '에서', t)
    t = re.sub(r'^\+(?=\d)', '플러스', t)
    t = re.sub(r'^[−-](?=\d)', '마이너스', t)
    t = re.sub(r'(\d[\d,]*(?:\.\d+)?)(%|m(?![a-z])|km|kg)?', lambda m: 수(m.group(1), t[m.end():]) + {'%': '퍼센트', 'm': '미터', 'km': '킬로미터', 'kg': '킬로그램', None: ''}[m.group(2)], t)
    return t


def 읽기(말: str) -> str:
    return ' '.join(낱말읽기(t) for t in 말.split(' '))


def 남은것(읽기글: str) -> list[str]:
    """녹음 전 검수: 아직 숫자·영어·한자가 남은 낱말(음성 모델이 틀리게 읽을 수 있는 것)."""
    return [t for t in 읽기글.split() if re.search(r'[0-9A-Za-z一-鿿]', t)]


if __name__ == '__main__':
    r = 읽기(sys.argv[1])
    print(r)
    print('남은 것:', 남은것(r) or '없음')
