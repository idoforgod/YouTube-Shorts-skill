#!/bin/bash
# 쇼츠만들기 — 장면 JSON 하나로: 녹음 → 영상 뽑기 → 시각 게이트 → 보기용 사본
# 실행: bash 뽑기.sh <장면.json>   (사진은 먼저 사진찾기.py 로 영상틀/public/사진/<이름>/ 에)
# 자리: 기본 = 압축 푼 폴더(쇼츠만들기·영상틀·수퍼토닉이 있는 곳) · 바꾸려면 환경변수 SHORTS_HOME
# bash 변수 이름은 영문만(한글 이름은 조용히 깨짐)
set -e
J="$1"; NAME=$(basename "$J" .json)
HERE=$(cd -P "$(dirname "$0")" && pwd)
HOME_DIR="${SHORTS_HOME:-$(cd "$HERE/../.." && pwd)}"
R="$HOME_DIR/영상틀"
PY="$HOME_DIR/수퍼토닉/.venv/bin/python"; [ -x "$PY" ] || PY="$HOME_DIR/수퍼토닉/.venv/Scripts/python.exe"; [ -x "$PY" ] || PY=python3
export SHORTS_HOME="$HOME_DIR"
export PYTHONUTF8=1   # 윈도우 기본 코드페이지(cp949 등)에서 한글 파일·이모지 입출력이 깨지지 않게
J=$(cd "$(dirname "$J")" && pwd)/$(basename "$J")
"$PY" "$HERE/음성짓기.py" "$J"
BROWSER=()
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
[ "$(uname)" = "Darwin" ] && [ -x "$CHROME" ] && BROWSER=(--browser-executable="$CHROME")   # 맥이면 구글 크롬 · 아니면 리모션 기본 브라우저
cd "$R"
mkdir -p out
nice -n 15 npx remotion render src/index.ts Shorts "out/$NAME.mp4" --props="{\"name\":\"$NAME\",\"pan\":null}" \
  --video-bitrate=8M --codec=h264 --concurrency=1 --gl=angle --audio-bitrate=192k --timeout=90000 "${BROWSER[@]}" > "out/$NAME.render.log" 2>&1 \
  || { grep -m3 -E "Error" "out/$NAME.render.log"; exit 2; }
cd out
"$PY" "$HERE/시각게이트.py" "$NAME.mp4"   # 불통이면 여기서 멈춤(내보내지 않음)
nice -n 15 ffmpeg -v error -y -i "$NAME.mp4" -c:v libx264 -b:v 4M -maxrate 4.5M -bufsize 8M -c:a copy "${NAME}_보기용.mp4"
echo "✅ 원본 $R/out/$NAME.mp4 · 보기용 $R/out/${NAME}_보기용.mp4 · 사진 출처 $R/public/사진/$NAME/출처.txt"
