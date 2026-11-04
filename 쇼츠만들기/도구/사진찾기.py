"""말에 맞는 «써도 되는» 실제 사진을 위키미디어 공용에서 찾아 받는다(퍼블릭 도메인·CC0·CC BY만 · SA/NC/ND 제외 · 남의 보도 사진 안 씀).
 실행: python3 사진찾기.py <쇼츠이름> <저장이름> "<영어 검색어>"  → 영상틀/public/사진/<쇼츠이름>/<저장이름>.jpg + 출처.txt 한 줄"""
import json, re, sys, urllib.parse, urllib.request
from 자리 import 공개

쇼츠, 이름, 검색 = sys.argv[1], sys.argv[2], sys.argv[3]
자리 = 공개 / '사진' / 쇼츠
자리.mkdir(parents=True, exist_ok=True)
머리 = {'User-Agent': 'ShortsMaker/1.0 (personal use)'}
허락 = re.compile(r'^(Public domain|CC0|CC BY \d(\.\d)?)$', re.I)

u = 'https://commons.wikimedia.org/w/api.php?' + urllib.parse.urlencode({
    'action': 'query', 'format': 'json', 'generator': 'search', 'gsrsearch': 검색 + ' filetype:bitmap', 'gsrnamespace': 6,
    'gsrlimit': 20, 'prop': 'imageinfo', 'iiprop': 'url|size|extmetadata', 'iiurlwidth': 1920})
쪽 = json.load(urllib.request.urlopen(urllib.request.Request(u, headers=머리), timeout=30)).get('query', {}).get('pages', {})
for p in sorted(쪽.values(), key=lambda p: p.get('index', 0)):
    ii = p['imageinfo'][0]
    판 = ii.get('extmetadata', {}).get('LicenseShortName', {}).get('value', '')
    if ii['width'] < 1200 or not 허락.match(판.strip()):
        continue
    파일 = 자리 / (이름 + '.jpg')
    파일.write_bytes(urllib.request.urlopen(urllib.request.Request(ii['thumburl'], headers=머리), timeout=60).read())
    줄 = '%s.jpg | %s | %s | %s' % (이름, p['title'].removeprefix('File:'), 판, ii['descriptionurl'])
    with open(자리 / '출처.txt', 'a') as f:
        f.write(줄 + '\n')
    print('✅', 줄, '· 출처 표기 필요' if 판.upper().startswith('CC BY') else '')
    break
else:
    print('❌ 써도 되는 사진 없음 — 검색어를 바꿔 다시', file=sys.stderr)
    sys.exit(1)
