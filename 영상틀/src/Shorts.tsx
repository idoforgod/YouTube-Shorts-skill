// 쇼츠만들기 스킬 화면 틀 — 내용과 상관없는 부품 조립식
// 틀(경제스타 쇼츠 역설계): 검정 위·아래 띠 · 고정 2줄 제목(흰·노랑) · 가운데 1080×1070 그림 띠 · 두꺼운 테두리 자막 · 끝 떡밥 빨강 · 3~4초마다 컷 · 첫 화면으로 되감기
import React, {useEffect, useState} from 'react';
import {AbsoluteFill, Audio, Img, Sequence, continueRender, delayRender, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';

type Word = {글: string; 시작: number; 끝: number};
type Shot = {때?: string | number; 꼴: string; [k: string]: any};
type Scene = {말: string; 컷: Shot[]; 빨강?: string; 소리: string; 낱말: Word[]; 길이: number};
export type ShortsPan = {제목: [string, string]; 꼬리: string; 장면: Scene[]; 음악?: {파일: string; 크기?: number}};

const 띠 = {위: 430, 높이: 1070};
const 색표: Record<string, string> = {흰: '#F2F2F2', 노랑: '#F5C400', 빨강: '#FF3B30', 오름: '#FF4646', 내림: '#2F7BFF', 초록: '#7FE3D0', 회색: '#9AA3B5'};
const c = (k?: string) => 색표[k ?? '흰'] ?? k ?? '#F2F2F2';
const 큰글 = 'BlackHan, Pretendard';
const 숫자글 = 'Pretendard';
const 흐림 = 'rgba(255,255,255,0.6)';
// 큰 글자 폭 맞춤 — 글이 길면 크기를 줄여 화면 폭(폭 px)을 넘지 않게(«700~1000m» 잘림 방지)
const 맞춤 = (글: string, 크기: number, 폭 = 900) => Math.min(크기, Math.floor(폭 / Math.max(1, [...String(글)].reduce((a, ch) => a + (/[\u3131-\uD7A3\u4E00-\u9FFF]/.test(ch) ? 1 : 0.74), 0))));
const 테두리 = (w: number): React.CSSProperties => ({WebkitTextStroke: `${w}px #000`, paintOrder: 'stroke fill'});

const useFonts = () => {
  const [h] = useState(() => delayRender('font'));
  useEffect(() => {
    const 면 = [
      new FontFace('BlackHan', `url(${staticFile('글꼴/BlackHanSans-ko.woff2')})`, {unicodeRange: 'U+1100-11FF, U+3130-318F, U+AC00-D7A3'}),
      new FontFace('BlackHan', `url(${staticFile('글꼴/BlackHanSans-latin.woff2')})`, {unicodeRange: 'U+0000-00FF, U+2010-2027'}),
      ...[['Medium', 500], ['Bold', 700], ['ExtraBold', 800], ['Black', 900]].map(([n, w]) => new FontFace('Pretendard', `url(${staticFile(`글꼴/Pretendard-${n}.woff2`)})`, {weight: String(w)})),
    ];
    Promise.all(면.map((f) => f.load().then((x) => document.fonts.add(x)))).then(() => continueRender(h));
  }, [h]);
};

// «때» = 낱말(그 낱말을 말하기 시작한 초) 또는 숫자(초)
const 때초 = (s: Scene, 때?: string | number) => (typeof 때 === 'number' ? 때 : 때 ? s.낱말.find((w) => w.글.includes(때))?.시작 ?? 0 : 0);
const useT = () => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  return f / fps;
};
const useIn = (at: number) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  return spring({frame: f - Math.round(at * fps), fps, config: {damping: 15, mass: 0.6}});
};
const 나타남 = (at: number) => useIn(at);

const 판바탕: React.FC<{children: React.ReactNode; 색조?: string}> = ({children, 색조 = '#0E3B3A'}) => (
  <AbsoluteFill style={{background: `radial-gradient(120% 90% at 30% 20%, ${색조}, #071A1F)`}}>
    <AbsoluteFill style={{backgroundImage: 'linear-gradient(rgba(255,255,255,0.05) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.05) 1px, transparent 1px)', backgroundSize: '60px 60px'}} />
    {children}
  </AbsoluteFill>
);
const 제목줄: React.FC<{글?: string; 색?: string}> = ({글, 색}) => (글 ? <div style={{position: 'absolute', top: 70, width: '100%', textAlign: 'center', fontFamily: 큰글, fontSize: 70, color: c(색 ?? '노랑')}}>{글}</div> : null);

// 쾅 — 큰 글자가 떨어져 박힘(크기 대비)
const 쾅: React.FC<{글: string; 색?: string; 크기?: number; 위?: number; 작은?: string; at?: number}> = ({글, 색, 크기 = 190, 위 = 330, 작은, at = 0}) => {
  const p = useIn(at);
  const f = useCurrentFrame();
  const 흔들 = p < 0.98 ? Math.sin(f * 2.3) * (1 - p) * 14 : 0;
  return (
    <div style={{position: 'absolute', top: 위, width: '100%', textAlign: 'center', transform: `scale(${2.2 - 1.2 * Math.min(1, p)}) translateX(${흔들}px)`, opacity: Math.min(1, p * 2)}}>
      {작은 && <div style={{fontFamily: 큰글, fontSize: 64, color: '#FFF', ...테두리(10)}}>{작은}</div>}
      <div style={{fontFamily: 숫자글, fontWeight: 900, fontSize: 맞춤(글, 크기), lineHeight: 1.05, color: c(색), ...테두리(12), textShadow: `0 0 40px ${c(색)}`}}>{글}</div>
    </div>
  );
};

const 선: React.FC<{값: number[]; p: number; 색: string; y?: number; h?: number}> = ({값, p, 색, y = 580, h = 250}) => {
  const lo = Math.min(...값), hi = Math.max(...값);
  const pts = 값.map((v, i) => [60 + (i / (값.length - 1)) * 960, y + h - ((v - lo) / (hi - lo || 1)) * h]);
  const d = pts.map(([a, b], i) => `${i ? 'L' : 'M'}${a},${b}`).join(' ');
  return (
    <svg width={1080} height={띠.높이} style={{position: 'absolute', left: 0, top: 0}}>
      <path d={`${d} L1020,${y + h} L60,${y + h} Z`} fill={색} opacity={0.12 * p} />
      <path d={d} stroke={색} strokeWidth={10} fill="none" strokeLinejoin="round" strokeDasharray={3000} strokeDashoffset={3000 * (1 - p)} style={{filter: `drop-shadow(0 0 14px ${색})`}} />
    </svg>
  );
};

// ── 컷 꼴 여덟(값은 장면 JSON에서) ──
const 사진: React.FC<{k: Shot; 멈춤?: boolean}> = ({k, 멈춤}) => {
  const 지금 = useCurrentFrame();
  const f = 멈춤 ? 0 : 지금;
  return (
    <AbsoluteFill style={{background: '#000'}}>
      <Img src={staticFile(`사진/${k.사진}`)} style={{position: 'absolute', width: '100%', height: '100%', objectFit: 'cover', objectPosition: k.기준 ?? '50% 50%', transform: `scale(${1.08 + f * 0.0012}) translateX(${-f * 0.25}px)`}} />
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(0,0,0,0.35) 0%, rgba(0,0,0,0) 30%, rgba(0,0,0,0) 55%, rgba(0,0,0,0.75) 100%)'}} />
      {!멈춤 && k.큰글 && <쾅 글={k.큰글} 색={k.색} 크기={k.크기} 작은={k.작은글} />}
    </AbsoluteFill>
  );
};

const 막대: React.FC<{k: Shot; s: Scene}> = ({k, s}) => {
  const 큰 = Math.max(...k.항목.map((r: any) => Math.abs(r[1])));
  const 주인공 = k.주인공 ?? k.항목.length - 1;
  return (
    <판바탕 색조="#1B2C46">
      <div style={{position: 'absolute', top: 70, left: 70, fontFamily: 큰글, fontSize: 64, color: c('초록')}}>{k.제목}</div>
      {k.항목.map(([이름, v, 글, 때]: [string, number, string, string?], i: number) => {
        const p = 나타남(때 ? 때초(s, 때) : 0.3 + i * 0.6);
        const 색 = c(k.색 ?? (v >= 0 ? '오름' : '내림'));
        return (
          <div key={이름} style={{position: 'absolute', left: 70, right: 70, top: 180 + i * 220, opacity: Math.min(1, p * 2)}}>
            <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end'}}>
              <span style={{fontFamily: 큰글, fontSize: 맞춤(이름, 62, 380), color: '#F2F2F2', whiteSpace: 'nowrap'}}>{이름}</span>
              <span style={{fontFamily: 숫자글, fontWeight: 900, fontSize: 맞춤(글, i === 주인공 ? 150 : 100, 540), lineHeight: 1, color: 색, textShadow: `0 0 24px ${색}`, whiteSpace: 'nowrap'}}>{글}</span>
            </div>
            <div style={{height: i === 주인공 ? 56 : 40, marginTop: 14, background: 'rgba(255,255,255,0.08)', borderRadius: 28}}>
              <div style={{height: '100%', borderRadius: 28, width: `${(Math.abs(v) / 큰) * 100 * Math.min(1, p)}%`, background: 색}} />
            </div>
          </div>
        );
      })}
    </판바탕>
  );
};

const 전광판: React.FC<{k: Shot}> = ({k}) => {
  const t = useT();
  const p = interpolate(t, [0.2, 2.2], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const 색 = c(k.방향 === '내림' ? '내림' : '오름');
  return (
    <판바탕>
      <div style={{position: 'absolute', top: 70, left: 70, fontFamily: 숫자글, fontWeight: 800, fontSize: 70, color: '#F2F2F2', letterSpacing: 4}}>{k.이름}</div>
      <div style={{position: 'absolute', top: 170, left: 50, fontFamily: 숫자글, fontWeight: 900, fontSize: 맞춤(k.값, 196, 980), color: '#F2F2F2', letterSpacing: -4, textShadow: '0 0 30px rgba(255,255,255,0.35)'}}>{k.값}</div>
      <div style={{position: 'absolute', top: 420, left: 70, fontFamily: 숫자글, fontWeight: 900, fontSize: 92, color: 색, textShadow: `0 0 20px ${색}`}}>{k.차}</div>
      <선 값={k.방향 === '내림' ? [17, 16, 17, 15, 14, 15, 13, 12, 11] : [10, 9, 11, 12, 11, 13, 15, 14, 17]} p={p} 색={색} />
    </판바탕>
  );
};

const 게이지: React.FC<{k: Shot}> = ({k}) => {
  const a = useIn(0.3);
  return (
    <판바탕 색조="#2E2A0E">
      <제목줄 글={k.제목} />
      <svg width={1080} height={700} style={{position: 'absolute', top: 200}}>
        <path d="M 190 520 A 350 350 0 0 1 890 520" stroke="rgba(255,255,255,0.12)" strokeWidth={60} fill="none" />
        <path d="M 190 520 A 350 350 0 0 1 890 520" stroke={c(k.색 ?? '노랑')} strokeWidth={60} fill="none" strokeDasharray={1100} strokeDashoffset={1100 * (1 - (k.채움 ?? 0.8) * Math.min(1, a))} />
      </svg>
      <div style={{position: 'absolute', top: 480, width: '100%', textAlign: 'center', fontFamily: 숫자글, fontWeight: 900, fontSize: 240, color: '#F2F2F2', lineHeight: 1}}>
        {(k.값 * Math.min(1, a)).toFixed(k.소수 ?? 1)}
        <span style={{fontSize: 110}}>{k.단위}</span>
      </div>
      {k.아래글 && <div style={{position: 'absolute', top: 780, width: '100%', textAlign: 'center', fontFamily: 큰글, fontSize: 60, color: c(k.색 ?? '노랑')}}>{k.아래글}</div>}
    </판바탕>
  );
};

const 범위글 = (k: Shot) => (k.아래 === k.위 ? `${k.아래}${k.단위 ?? '%'}` : `${k.아래}~${k.위}${k.단위 ?? '%'}`);
const 범위: React.FC<{k: Shot}> = ({k}) => {
  const b = useIn(0.2);
  return (
    <판바탕 색조="#2E2A0E">
      <제목줄 글={k.제목} />
      <div style={{position: 'absolute', top: 260, width: '100%', textAlign: 'center', fontFamily: 숫자글, fontWeight: 900, fontSize: 맞춤(범위글(k), 230), color: '#F2F2F2', lineHeight: 1}}>{범위글(k)}</div>
      <div style={{position: 'absolute', top: 600, left: 90, right: 90, height: 80, background: 'rgba(255,255,255,0.1)', borderRadius: 40}}>
        <div style={{position: 'absolute', left: 0, top: 0, bottom: 0, width: `${(k.아래 / (k.최대 ?? 100)) * 100 * Math.min(1, b)}%`, background: 'rgba(245,196,0,0.45)', borderRadius: 40}} />
        <div style={{position: 'absolute', left: `${(k.아래 / (k.최대 ?? 100)) * 100}%`, width: `${Math.max(1.5, ((k.위 - k.아래) / (k.최대 ?? 100)) * 100)}%`, top: -14, bottom: -14, background: c('노랑'), borderRadius: 10, opacity: b}} />
      </div>
      {k.아래글 && <div style={{position: 'absolute', top: 720, left: 90, right: 90, textAlign: 'center', fontFamily: 숫자글, fontWeight: 700, fontSize: 40, color: 흐림}}>{k.아래글}</div>}
    </판바탕>
  );
};

const 갈림길: React.FC<{k: Shot; s: Scene}> = ({k, s}) => {
  const t = useT();
  const 위 = interpolate(t, [때초(s, k.위.때), 때초(s, k.위.때) + 1.2], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const 아래 = interpolate(t, [때초(s, k.아래.때), 때초(s, k.아래.때) + 1.2], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const 시작 = useIn(0.2);
  const 칸 = (y: number, p: number, d: any, 색: string) => (
    <div style={{position: 'absolute', left: 520, top: y, width: 500, opacity: p, transform: `translateX(${(1 - p) * 60}px)`, background: 'rgba(0,0,0,0.45)', border: `5px solid ${색}`, borderRadius: 24, padding: '22px 28px'}}>
      {d.큰 && <div style={{fontFamily: 숫자글, fontWeight: 900, fontSize: 96, color: 색, lineHeight: 1}}>{d.큰}</div>}
      <div style={{fontFamily: 큰글, fontSize: 50, color: '#F2F2F2', marginTop: 8}}>{d.글[0]}</div>
      {d.글[1] && <div style={{fontFamily: 큰글, fontSize: 46, color: 색, marginTop: 6}}>→ {d.글[1]}</div>}
    </div>
  );
  return (
    <판바탕 색조="#1E1B3A">
      <div style={{position: 'absolute', top: 60, width: '100%', textAlign: 'center', fontFamily: 큰글, fontSize: 70, color: '#F2F2F2'}}>{k.제목}</div>
      {k.주석 && <div style={{position: 'absolute', top: 150, width: '100%', textAlign: 'center', fontFamily: 숫자글, fontWeight: 600, fontSize: 30, color: 흐림}}>{k.주석}</div>}
      <svg width={1080} height={띠.높이} style={{position: 'absolute'}}>
        <path d="M 250 520 C 400 520 400 340 520 340" stroke={c(k.위.색 ?? '빨강')} strokeWidth={12} fill="none" strokeDasharray={500} strokeDashoffset={500 * (1 - 위)} />
        <path d="M 250 520 C 400 520 400 730 520 730" stroke={c(k.아래.색 ?? '회색')} strokeWidth={12} fill="none" strokeDasharray={500} strokeDashoffset={500 * (1 - 아래)} />
      </svg>
      <div style={{position: 'absolute', left: 50, top: 450, width: 220, height: 140, borderRadius: 24, background: c('노랑'), display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: 큰글, fontSize: 52, color: '#000', transform: `scale(${시작})`, textAlign: 'center'}}>{k.시작}</div>
      {칸(210, 위, k.위, c(k.위.색 ?? '빨강'))}
      {칸(640, 아래, k.아래, c(k.아래.색 ?? '회색'))}
    </판바탕>
  );
};

const 카드: React.FC<{k: Shot}> = ({k}) => {
  const 도장 = useIn(0.4);
  const 목록 = useIn(1.2);
  return (
    <AbsoluteFill style={{background: `radial-gradient(100% 80% at 50% 30%, ${k.색조 ?? '#3B1414'}, #0A0606)`}}>
      {k.위글 && <div style={{position: 'absolute', top: 70, width: '100%', textAlign: 'center', fontFamily: 큰글, fontSize: 66, color: 흐림, letterSpacing: 4}}>{k.위글}</div>}
      <div style={{position: 'absolute', top: 170, width: '100%', textAlign: 'center', fontFamily: 큰글, fontSize: 맞춤(k.큰글, 210), color: '#F2F2F2', lineHeight: 1}}>{k.큰글}</div>
      {k.도장 && <div style={{position: 'absolute', top: 210, right: 90, fontFamily: 큰글, fontSize: 84, color: c('빨강'), border: `9px solid ${c('빨강')}`, borderRadius: 14, padding: '0 22px', transform: `scale(${1.6 - 0.6 * 도장}) rotate(12deg)`, opacity: 도장}}>{k.도장}</div>}
      {k.값 && <div style={{position: 'absolute', top: 430, width: '100%', textAlign: 'center', fontFamily: 숫자글, fontWeight: 900, fontSize: 240, color: c(k.값색), textShadow: `0 0 34px ${c(k.값색)}`, lineHeight: 1}}>{k.값}</div>}
      <div style={{position: 'absolute', top: k.값 ? 700 : 440, left: 120, right: 120, opacity: 목록}}>
        {(k.목록 ?? []).map((t: string) => (
          <div key={t} style={{fontFamily: 큰글, fontSize: k.값 ? 58 : 76, color: '#F2F2F2', marginBottom: k.값 ? 18 : 30}}>{k.점 ?? '✕'} {t}</div>
        ))}
      </div>
    </AbsoluteFill>
  );
};

const 아이콘: React.FC<{k: Shot; s: Scene}> = ({k, s}) => {
  const p = useIn(0.1);
  const 빨 = useIn(때초(s, s.빨강));
  return (
    <판바탕 색조="#3A1010">
      <div style={{position: 'absolute', top: 120, width: '100%', textAlign: 'center', fontSize: 380, transform: `scale(${0.6 + 0.4 * p}) rotate(${(1 - p) * -20}deg)`}}>{k.아이콘}</div>
      {k.글1 && <div style={{position: 'absolute', top: 620, width: '100%', textAlign: 'center', fontFamily: 큰글, fontSize: 70, color: '#F2F2F2'}}>{k.글1}</div>}
      {k.글2 && <div style={{position: 'absolute', top: 730, width: '100%', textAlign: 'center', fontFamily: 큰글, fontSize: 96, color: c('빨강'), opacity: s.빨강 ? 빨 : 1}}>{k.글2}</div>}
    </판바탕>
  );
};

const 그리기 = (k: Shot, s: Scene) => {
  switch (k.꼴) {
    case '사진': return <사진 k={k} />;
    case '막대': return <막대 k={k} s={s} />;
    case '전광판': return <전광판 k={k} />;
    case '게이지': return <게이지 k={k} />;
    case '범위': return <범위 k={k} />;
    case '갈림길': return <갈림길 k={k} s={s} />;
    case '카드': return <카드 k={k} />;
    case '아이콘': return <아이콘 k={k} s={s} />;
    default: return null;
  }
};

// 컷 바뀜: 번쩍 + 살짝 당김(컷 안 시간은 0부터 다시 → Sequence로 감쌈)
const 컷판: React.FC<{k: Shot; s: Scene; 첫컷: boolean}> = ({k, s, 첫컷}) => {
  const f = useCurrentFrame();
  const 번쩍 = 첫컷 ? 0 : interpolate(f, [0, 4], [0.7, 0], {extrapolateRight: 'clamp'});
  const 당김 = 첫컷 ? 1 : interpolate(f, [0, 8], [1.12, 1], {extrapolateRight: 'clamp'});
  return (
    <AbsoluteFill style={{transform: `scale(${당김})`}}>
      {그리기(k, s)}
      <AbsoluteFill style={{background: '#FFF', opacity: 번쩍}} />
    </AbsoluteFill>
  );
};

const 장면판: React.FC<{s: Scene; 끝장면: boolean; 첫사진?: Shot}> = ({s, 끝장면, 첫사진}) => {
  const f = useCurrentFrame();
  const {fps} = useVideoConfig();
  const 고리 = 끝장면 && !!첫사진 && f / fps > s.길이 - 1.0; // 끝 1초 = 첫 화면 그대로(되감기)
  const 당김 = 고리 ? 1 : 1 + 0.05 * (f / (s.길이 * fps));
  const 시작들 = s.컷.map((k) => Math.round(때초(s, k.때) * fps));
  const 끝프레임 = Math.ceil(s.길이 * fps);
  return (
    <AbsoluteFill>
      <Audio src={staticFile(s.소리)} />
      <div style={{position: 'absolute', top: 띠.위, left: 0, width: 1080, height: 띠.높이, overflow: 'hidden'}}>
        <AbsoluteFill style={{transform: `scale(${당김})`, transformOrigin: '50% 45%'}}>
          {고리 ? (
            <사진 k={첫사진!} 멈춤 />
          ) : (
            s.컷.map((k, i) => {
              const from = 시작들[i];
              const to = i + 1 < 시작들.length ? 시작들[i + 1] : 끝프레임;
              return to > from ? (
                <Sequence key={i} from={from} durationInFrames={to - from} layout="none">
                  <AbsoluteFill>
                    <컷판 k={k} s={{...s, 낱말: s.낱말.map((w) => ({...w, 시작: w.시작 - from / fps, 끝: w.끝 - from / fps}))}} 첫컷={i === 0} />
                  </AbsoluteFill>
                </Sequence>
              ) : null;
            })
          )}
        </AbsoluteFill>
      </div>
      <자막 s={s} />
    </AbsoluteFill>
  );
};

// 자막: 2~3낱말 한 줄 · 흰 글 + 두꺼운 검은 테두리 · «빨강» 낱말부터 빨강(끝 떡밥)
const 자막: React.FC<{s: Scene}> = ({s}) => {
  const t = useT();
  const 묶음: Word[][] = [];
  let 지금: Word[] = [];
  s.낱말.forEach((w) => {
    지금.push(w);
    const 길이 = 지금.reduce((a, x) => a + x.글.length, 0);
    if (길이 >= 9 || 지금.length >= 3 || /[.,?!]$/.test(w.글)) {
      묶음.push(지금);
      지금 = [];
    }
  });
  if (지금.length) 묶음.push(지금);
  const 줄 = 묶음.find((g) => t < g[g.length - 1].끝 + 0.12) ?? 묶음[묶음.length - 1];
  const 빨강 = !!s.빨강 && t >= 때초(s, s.빨강);
  return (
    <div style={{position: 'absolute', top: 띠.위 + 920, width: '100%', textAlign: 'center', fontFamily: 큰글, fontSize: 78, color: 빨강 ? c('빨강') : '#FFFFFF', ...테두리(14)}}>
      {줄.map((w) => w.글.replace(/[.,]$/, '')).join(' ')}
    </div>
  );
};

export const Shorts: React.FC<{name: string; pan: ShortsPan | null}> = ({pan}) => {
  useFonts();
  const {fps} = useVideoConfig();
  if (!pan) return null;
  const 끝프 = pan.장면.reduce((a, s) => a + Math.ceil(s.길이 * fps), 0);
  const 첫 = pan.장면[0]?.컷[0];
  const 첫사진 = 첫?.꼴 === '사진' ? 첫 : undefined;
  let at = 0;
  return (
    <AbsoluteFill style={{background: '#000'}}>
      {pan.음악 && (
        // 배경음악: 목소리보다 훨씬 작게(기본 0.187) · 처음 1초 커지고 끝 1.5초 줄어듦 · 짧으면 되풀이
        <Audio src={staticFile(`음악/${pan.음악.파일}`)} loop volume={(f) => (pan.음악!.크기 ?? 0.187) * interpolate(f, [0, fps, 끝프 - fps * 1.5, 끝프], [0, 1, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'})} />
      )}
      {pan.장면.map((s, i) => {
        const len = Math.ceil(s.길이 * fps);
        const from = at;
        at += len;
        return (
          <Sequence key={i} from={from} durationInFrames={len}>
            <장면판 s={s} 끝장면={i === pan.장면.length - 1} 첫사진={첫사진} />
          </Sequence>
        );
      })}
      <div style={{position: 'absolute', top: 150, width: '100%', textAlign: 'center', fontFamily: 큰글, fontSize: 100, lineHeight: '112px', color: c('흰')}}>{pan.제목[0]}</div>
      <div style={{position: 'absolute', top: 288, width: '100%', textAlign: 'center', fontFamily: 큰글, fontSize: 100, lineHeight: '112px', color: c('노랑')}}>{pan.제목[1]}</div>
      <div style={{position: 'absolute', top: 1516, left: 40, right: 40, textAlign: 'center', fontFamily: 숫자글, fontWeight: 600, fontSize: 25, lineHeight: '31px', color: 'rgba(255,255,255,0.45)'}}>{pan.꼬리}</div>
    </AbsoluteFill>
  );
};
