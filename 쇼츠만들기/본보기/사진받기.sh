#!/bin/bash
# 본보기 3편에 쓰는 공개 사진(퍼블릭 도메인·CC0·CC BY)을 위키미디어 공용에서 다시 받는다.
# 실행: bash 사진받기.sh          (그다음 bash ../도구/뽑기.sh 본보기_환율.json)
# 사진은 «파일 이름»으로 찾는다. 같은 사진이 안 나오면 검색어를 바꿔도 된다(JSON의 사진 이름만 같으면 됨).
P="$(cd -P "$(dirname "$0")/../도구" && pwd)/사진찾기.py"
export PYTHONUTF8=1   # 윈도우 기본 코드페이지(cp949 등)에서 한글·이모지 입출력이 깨지지 않게
PYBIN=python3; "$PYBIN" -c "import sys" >/dev/null 2>&1 || PYBIN=python   # 윈도우는 python3 이름이 없을 수 있다
get() {   # 위키미디어가 «너무 많은 요청(429)»이면 20초 쉬고 다시(최대 4번)
  for i in 1 2 3 4; do
    "$PYBIN" "$P" "$1" "$2" "$3" 2>/dev/null && { sleep 3; return 0; }
    sleep 20
  done
  echo "❌ $1/$2 못 받음 — 검색어를 바꿔 사진찾기.py 로 다시"
}
# 본보기_환율
get 본보기_환율 서울   "Seocho-gu Skyline from Han River Dec 2023"
get 본보기_환율 달러   "Cash money 140606-A-CA521-021"
get 본보기_환율 달러2  "Macro dollars bills money stars"
get 본보기_환율 항구   "Container ship being loaded in Long Beach container port"
# 본보기_탈라리코
get 본보기_탈라리코 의사당     "Texas State Capitol Austin Texas DSC07601"
get 본보기_탈라리코 성경       "Holy bible"
get 본보기_탈라리코 유세       "Viva Democracy Awesome turnout James Talarico Rally Backyard"
get 본보기_탈라리코 탈라리코   "James Talarico Texas"     # 같은 인물 사진이 유세와 겹칠 수 있음
get 본보기_탈라리코 트럼프     "January 2025 Official Presidential Portrait of Donald J. Trump"
# 본보기_중국증시
get 본보기_중국증시 상하이야경 "Pudong at Night 10274037574"
get 본보기_중국증시 불꽃놀이   "Fireworks in Kuwait City 24244363641"
get 본보기_중국증시 상하이낮   "Shanghai skyline waterfront pudong 5166168"
get 본보기_중국증시 홍콩       "International Commerce Centre on Victoria Harbour"
