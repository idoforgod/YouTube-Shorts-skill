"""도구들이 함께 쓰는 자리. 기본 = 압축 푼 폴더(쇼츠만들기·영상틀·수퍼토닉이 들어 있는 곳) · 바꾸려면 환경변수 SHORTS_HOME."""
import os
from pathlib import Path

홈 = Path(os.environ.get('SHORTS_HOME') or Path(__file__).resolve().parents[2]).resolve()
공개 = 홈 / '영상틀' / 'public'
수퍼토닉 = 홈 / '수퍼토닉' / '코드'
파이썬 = next((p for p in (홈 / '수퍼토닉' / '.venv' / 'bin' / 'python', 홈 / '수퍼토닉' / '.venv' / 'Scripts' / 'python.exe') if p.exists()), Path('python3'))
