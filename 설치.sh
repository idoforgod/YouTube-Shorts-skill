#!/bin/bash
# 쇼츠만들기 설치 — 압축 푼 폴더에서 한 번만: bash 설치.sh
# 하는 일: ① 필요한 프로그램 확인 ② 영상틀 npm install ③ 무료 음성(수퍼토닉) 코드·모델 받기 + 파이썬 환경 ④ Claude Code 스킬로 연결
# 처음엔 인터넷으로 약 1GB(영상틀 부품 약 560MB · 음성 모델 약 400MB)를 받는다.
# bash 변수 이름은 영문만(한글 이름은 조용히 깨짐)
set -e
HOME_DIR=$(cd -P "$(dirname "$0")" && pwd)
SUPER="$HOME_DIR/수퍼토닉"
SUPER_REPO="https://github.com/supertone-oss-archive/supertonic.git"
SUPER_COMMIT="1e9799e964ea4c0dad7cde993b65c3c813a7b373"           # 코드 판(보관 저장소)
MODEL_REPO="supertone-oss-archive/supertonic-3"
MODEL_REV="aafc6e32416a594460b32413efc49d7fe4ce6d46"               # 모델 판(코드/README.md 의 Quick Start 가 정한 것)

say() { echo; echo "== $*"; }
need() { command -v "$1" >/dev/null 2>&1 || { echo "❌ $1 이(가) 없습니다. $2"; MISSING=1; }; }

say "1/5 필요한 프로그램 확인"
MISSING=0
need node   "https://nodejs.org 에서 설치(18 이상) — 맥: brew install node"
need npm    "Node.js 와 함께 설치됩니다"
need git    "맥: xcode-select --install"
need ffmpeg "맥: brew install ffmpeg · 윈도우: winget install ffmpeg"
need ffprobe "ffmpeg 와 함께 설치됩니다"
PYBIN=""
for c in python3.12 python3.11 python3.13 python3.10 python3; do
  if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(0 if (3,10)<=sys.version_info[:2]<=(3,13) else 1)' 2>/dev/null; then PYBIN="$c"; break; fi
done
[ -n "$PYBIN" ] || { echo "❌ 파이썬 3.10~3.13 이 없습니다. 맥: brew install python@3.12"; MISSING=1; }
[ "$MISSING" = 0 ] || { echo; echo "위 프로그램을 먼저 설치하고 bash 설치.sh 를 다시 실행하세요."; exit 1; }
echo "✅ node $(node -v) · python $("$PYBIN" -V | cut -d' ' -f2) · ffmpeg 있음"

say "2/5 영상틀 부품 설치(npm install)"
(cd "$HOME_DIR/영상틀" && npm install --no-audit --no-fund)

say "3/5 무료 음성(수퍼토닉) 코드 받기 + 파이썬 환경"
if [ ! -d "$SUPER/코드/.git" ]; then
  git clone "$SUPER_REPO" "$SUPER/코드"
fi
git -C "$SUPER/코드" checkout -q "$SUPER_COMMIT"
if [ ! -x "$SUPER/.venv/bin/python" ] && [ ! -x "$SUPER/.venv/Scripts/python.exe" ]; then
  "$PYBIN" -m venv "$SUPER/.venv"
fi
VPY="$SUPER/.venv/bin/python"; [ -x "$VPY" ] || VPY="$SUPER/.venv/Scripts/python.exe"
"$VPY" -m pip install -q --upgrade pip
"$VPY" -m pip install -q -r "$SUPER/코드/py/requirements.txt" pillow huggingface_hub
echo "✅ 파이썬 환경 준비"

say "4/5 음성 모델 받기(약 400MB · 한 번만)"
if [ -f "$SUPER/코드/assets/voice_styles/M1.json" ] && [ -d "$SUPER/코드/assets/onnx" ]; then
  echo "이미 받아 둠"
else
  "$VPY" -c "from huggingface_hub import snapshot_download; snapshot_download('$MODEL_REPO', revision='$MODEL_REV', local_dir='$SUPER/코드/assets')"
fi
[ -f "$SUPER/코드/assets/voice_styles/M1.json" ] || { echo "❌ 모델 받기 실패 — 인터넷을 확인하고 다시 실행하세요."; exit 1; }
echo "✅ 모델 준비 (라이선스: 코드 MIT · 모델 OpenRAIL-M — 수퍼토닉/문서/OpenRAIL-M_LICENSE.txt)"

say "5/5 Claude Code 스킬로 연결"
SKILLS="$HOME/.claude/skills"
mkdir -p "$SKILLS"
if [ -L "$SKILLS/쇼츠만들기" ]; then
  ln -sfn "$HOME_DIR/쇼츠만들기" "$SKILLS/쇼츠만들기"; echo "✅ 연결 갱신: $SKILLS/쇼츠만들기"
elif [ -e "$SKILLS/쇼츠만들기" ]; then
  echo "⚠ $SKILLS/쇼츠만들기 가 이미 있어 건드리지 않았습니다. 지우거나 이름을 바꾼 뒤 bash 설치.sh 를 다시 실행하세요."
else
  ln -s "$HOME_DIR/쇼츠만들기" "$SKILLS/쇼츠만들기"; echo "✅ 연결: $SKILLS/쇼츠만들기 → $HOME_DIR/쇼츠만들기"
fi

echo
echo "🎬 설치 끝. Claude Code 를 새로 열고 «이 글로 쇼츠 만들어» 라고 말하세요."
echo "   (연결 대신 폴더를 복사해 넣었다면 환경변수 SHORTS_HOME=$HOME_DIR 를 설정하세요)"
