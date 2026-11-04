import React from 'react';
import {Composition, staticFile} from 'remotion';
import {Shorts, ShortsPan} from './Shorts';

const FPS = 30;

// 쇼츠만들기 스킬 — props.name = public/ 안의 장면 JSON 이름(음성짓기.py 가 낱말 시각·소리를 채운 것)
export const Root: React.FC = () => (
  <Composition
    id="Shorts"
    component={Shorts}
    width={1080}
    height={1920}
    fps={FPS}
    durationInFrames={FPS * 60}
    defaultProps={{name: '본보기', pan: null as ShortsPan | null}}
    calculateMetadata={async ({props}) => {
      const pan: ShortsPan = await (await fetch(staticFile(props.name + '.json'))).json();
      const total = pan.장면.reduce((a, s) => a + Math.ceil(s.길이 * FPS), 0);
      return {durationInFrames: total, props: {...props, pan}};
    }}
  />
);
