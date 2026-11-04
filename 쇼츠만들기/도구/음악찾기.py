"""배경음악을 위키미디어 공용에서 찾아 받는다(퍼블릭 도메인·CC0·CC BY만 · SA/NC/ND 제외) → mp3로 바꿔 영상틀/public/음악/<저장이름>.mp3 + 출처.txt 한 줄.
 실행: python3 음악찾기.py <저장이름> "<영어 검색어>"   (CC BY면 설명란에 출처를 적는다)"""
import json, re, subprocess, sys, urllib.parse, urllib.request
from pathlib import Path
from 자리 import 공개

이름, 검색 = sys.argv[1], sys.argv[2]
자리 = 공개 / '음악'
자리.mkdir(parents=True, exist_ok=True)
머리 = {'User-Agent': 'ShortsMaker/1.0 (personal use)'}
허락 = re.compile(r'^(Public domain|CC0|CC BY \d(\.\d)?)$', re.I)

u = 'https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode({
    'action': 'query', 'format': 'json', 'generator': 'search', 'gsrsearch': 검색 + ' filetype:audio', 'gsrnamespace': 6,
    'gsrlimit': 20, 'prop': 'imageinfo', 'iiprop': 'url|extmetadata'})
쪽 = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=머리), timeout=30)).get('query', {}).get('pages', {})
for p in sorted(쪽.values(), key=lambda p: p.get('index', 0)):
    ii = p['imageinfo'][0]
    판 = ii.get('extmetadata', {}).get('LicenseShortName', {}).get('value', '').strip()
    if not 허락.match(판):
        continue
    원본 = 자리 / ('_' + 이름 + Path(urllib.parse.urlparse(ii['url']).path).suffix)
    원본.write_bytes(urllib.request.urlopen(urllib.request.Request(ii['url'], headers=머리), timeout=120).read())
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(원본), '-ac', '2', '-ar', '44100', '-b:a', '192k', str(자리 / (이름 + '.mp3'))], check=True)
    원본.unlink()
    줄 = '%s.mp3 | %s | %s | %s' % (이름, p['title'].removeprefix('File:'), 판, ii['descriptionurl'])
    with open(자리 / '출처.txt', 'a') as f:
        f.write(줄 + '\n')
    print('✅', 줄, '· 설명란에 출처 표기' if 판.upper().startswith('CC BY') else '')
    break
else:
    print('❌ 써도 되는 음악 없음 — 검색어를 바꿔 다시', file=sys.stderr)
    sys.exit(1)
