# DA 릴스 상세 규칙

## A. 디자인 금지·원칙
- **금지**: 알약(둥근 캡슐) 라벨, 흰색 둥근 네모 배경에 검정 글씨, 모든 장면에 "혜택 1/2/3" 번호 붙이기, 같은 틀(라벨+2줄+큰 글씨)을 장면마다 반복, 남색+금색, 영어 이탤릭 소제목, 이모지 아이콘, 감성·추상 카피
- **가독성**: 글씨는 배경 없이 흰색/노랑 + 진한 그림자. 글씨 뒤에는 테두리 없이 번지는 어둠(`softDark`, 생성기에 기본 포함)과 위쪽 그라데이션. 첫 장면·엔딩은 특히 크게 (본문 100px 안팎)
- **안전 영역**: 글씨는 y 250~1250 안 (위는 인스타 상단바, 아래 35%는 광고 버튼·캡션)
- **색**: 흰 글씨 + 노랑 #FFE100 강조, 포인트 핑크 #FF3B5C(점·작은 표시만)
- **글씨체**(피그마 연동에서 불러와지는 것만): Black Han Sans(큰 글씨), Noto Sans KR Black/Bold(본문), Nanum Pen(손글씨), Jua, Do Hyeon, Gothic A1. Pretendard·지마켓산스 등은 연동에서 못 불러옴 → 사용자가 피그마에서 직접 바꾸는 건 괜찮음(내보내기는 됨)
- 컷 속도: 1.2~1.4초는 "전환이 빠르다"는 피드백 → 1.5초 이상

## B. 아이디어 창고 (고르는 용도. 순서대로 쓰지 말 것, 새로 만들어도 됨)
**USP 종류별 연출 예시** — 연출은 상품·혜택의 특성에서 나와야 함
| USP 종류 | 핵심 | 연출 예시 |
|---|---|---|
| 여러 장소를 한 번에 (핑세치·시티투어) | 장소 개수·이름 | 컷마다 장소 위치 태그, "3곳" 숫자, 장소 첫 글자 하나씩 크게 |
| 할인·쿠폰·가격 | 숫자 | 숫자를 화면 가득, 정가→할인가(확인된 가격만) |
| 걱정 해결 (최소인원·픽업·언어) | 걱정→안심 | 걱정 문장 먼저 → 0.8초 뒤 해결 문장, 말하는 자막 |
| 이동·거리 (호텔존 출발·공항 픽업) | 시간·경로 | 지도 핀 + 이동 시간, 출발→도착 화살표 |
| 체험 자체가 강함 (스노클링·스카이다이빙) | 장면 | 글씨 최소화, 손글씨 한 줄, 영상이 주인공 |
| 타겟 맞춤 (가족·커플) | 누구에게 | "가족이라면 / 커플이라면" 갈림, 타겟 장면 컷 |
| 기간 한정 (사실일 때만) | 마감 | 날짜 크게, 엔딩에 기간 |

**후킹(첫 2~3초)**
1. 저장형: "○○ 가기 전에 이 영상 저장하세요"
2. 금지형: "이거 모르고 ○○ 가지 마세요"
3. 질문형: "○○ 투어, 아직 예약 안 했다면"
4. POV형: "POV: 가족이랑 ○○ 첫날"
5. 숫자형: "○○에서 꼭 해야 할 3가지"
6. 반전형: "○○ 투어 비쌀 줄 알았는데…"
7. 비교형: "혼자 알아보기 vs 여기서 한 번에" (사실만)

**흐름**
1. 혜택 나열 → 정리  2. 하루 일정(아침→밤)  3. 문제→해결(이동 걱정→픽업)  4. 랭킹 TOP3  5. 퀴즈(맞혀보세요→정답)  6. 타겟별(가족이라면/커플이라면)

**장면 연출** (생성기 type + 직접 그리기)
1. 위쪽 2~3줄 묶음 (`text`, 가운데/왼쪽, order 바꾸기)
2. 화면 가득 큰 글자 하나·숫자 (`bigword`: "10%", "핑/세/치", "3곳")
3. 말하는 자막, 화면 중간 아래 (`caption`)
4. 장소 이름 태그, 왼쪽 아래 (`tag`)
5. 손글씨 메모만 한 줄, 비스듬히 (`text` + hand만)
6. 질문 → 0.8초 뒤 답 (같은 장면을 프레임 2장으로 나눠 spec.txt 에서 시간차)
7. 체크 쌓기: 장면마다 체크 하나씩 늘어남 (프레임을 누적으로 여러 장)
8. 화살표·밑줄 낙서 (vector path, 손으로 그린 느낌으로 약간 비뚤게)
9. 숫자 카운트: "1일 / 3곳 / 0명 걱정" 처럼 숫자만 크게 나열
10. 지도 핀 + 이동 시간 (USP·프모페에 시간이 있을 때만)
11. 비교 2단: 위 "보통은" / 아래 "여기선" (사실만)
12. 퀴즈 보기 2개 → 정답 표시
13. 랭킹 숫자 배지 "1" "2" "3" (원·사각 배경 없이 큰 숫자)
14. 엔딩 변형: 체크리스트 정리 / 큰 한 줄 + CTA(`style:"oneliner"`) / 질문형("여러분은 어디 먼저 가요?") / 저장 유도 / 기간 강조(기간이 사실일 때만)

## B-2. Pexels 크롬 검색 (클로드 크롬이 연결돼 있을 때 — 기본 방식)
Pexels 사이트는 프로그램 직접 접속을 막음 → 사용자 크롬(클로드 크롬 확장)으로 검색 페이지를 열어 결과만 뽑음. 차단 우회(가짜 브라우저 헤더 등)는 하지 않는다.
1. `tabs_context_mcp(createIfEmpty)` → 검색어마다 `navigate` 로 `https://www.pexels.com/search/videos/<영어 검색어>/?orientation=portrait`
2. `javascript_tool` 로 아래 코드 실행 → 결과 JSON 문자열
```js
await new Promise(r=>setTimeout(r,2500));
const out=[];
for(const a of [...document.querySelectorAll('article')].slice(0,14)){
  const page=[...a.querySelectorAll('a[href*="/video/"]')].map(x=>x.href).find(h=>!h.includes('/download/'));
  if(!page) continue;
  const id=page.replace(/\/$/,'').split('-').pop();
  const img=a.querySelector('img');
  const h=await (await fetch(page)).text();
  const files=[...new Set(h.match(new RegExp('video-files/'+id+'/[A-Za-z0-9_.-]+[.]mp4','g'))||[])];
  out.push({id,page,thumb:img?(img.currentSrc||img.src):'',files});
}
JSON.stringify(out)
```
3. 결과를 작업 폴더 `D/pexels_<검색어>.json` 으로 저장 → `$PY $T/dareels.py --dir D import --json D/pexels_<검색어>.json --q "<검색어>"` (검색어마다 반복, 미리보기판은 누적)
4. 다 끝나면 만든 탭은 `tabs_close_mcp` 로 닫기. 원본 다운로드(`fetch`)는 videos.pexels.com 에서 바로 받아짐(브라우저 불필요)
- 클로드 크롬이 없으면 → `search`(Pixabay 키 방식)

## C. 오버레이 생성기 사용법
1. `tools/overlay_builder.js` 를 Read → `__SPEC__` 를 JSON 으로 바꾼 전체 코드를 use_figma `code` 로 보냄 (fileKey = 사용자가 준 피그마 파일)
2. SPEC 형식
```json
{"title":"칸쿤 DA 릴스","duration":19.5,"scenes":[
 {"id":"01","name":"후킹","t":[0,2.5],"type":"text","align":"left","y":320,"order":["lines","hand"],
  "lines":[{"text":"칸쿤 투어,","size":104},{"text":"아직 예약 안 했다면","size":104,"hl":"예약 안 했다면"}],"hand":"이거 먼저 보고 가요"},
 {"id":"02","name":"쿠폰","t":[2.5,5],"type":"bigword","word":"10%","sub":"칸쿤 투어·티켓 쿠폰","subHl":"쿠폰"},
 {"id":"03","name":"태그","t":[5,6.5],"type":"tag","ko":"핑크라군","en":"LAS COLORADAS"},
 {"id":"04","name":"자막","t":[6.5,9],"type":"caption","lines":[{"text":"인원 안 모여도","hl":null},{"text":"무조건 출발","hl":"무조건 출발"}]},
 {"id":"05","name":"파크","t":[9,12],"type":"text","order":["label","big","lines"],"label":{"text":"스칼렛·셀하","color":"yellow"},
  "big":[["최저가 ",170,"white"],["보장",170,"yellow"]],"lines":[{"text":"아이랑 하루 종일","size":60}]},
 {"id":"07","name":"엔딩","t":[17,19.5],"type":"ending","label":"지금 마이리얼트립에서","title":"칸쿤 필수 투어·티켓\n기획전 혜택 총정리",
  "checks":[{"text":"최대 10% 쿠폰팩","hl":"10%"}],"cta":"쿠폰 받고 예약하기"}
]}
```
   - `text`: label{text,color,size} / lines[{text,size,hl}] / big[[글자,크기,색]] / hand / order / align(center|left) / y / dim(딤 진하기 0~1)
   - `bigword`: word,size(기본 420),color,sub,subHl,y / `caption`: lines,y(기본 980) / `tag`: ko,en,y / `ending`: label,title,titleHl,checks,cta,style("oneliner"면 큰 한 줄형)
   - 위 예시는 **형식 설명용**. 문구·구성은 매번 새로 쓸 것
3. 반환값 `bgs` 에 `upload_assets(count=N, nodeIds=bgs)` → 반환된 submitUrl 에 `curl -X POST -F "file=@still/cK.jpg;type=image/jpeg"` (장면의 첫 컷 사진)
4. 반환 `warn` 이 있으면 글씨 위치·폭 고치기

## D. 내보내기 순서 (투명 PNG 만들기)
피그마 연동 스크린샷은 투명 배경이 안 됨 → 검정·흰 배경 두 장의 차이로 투명도 계산
1. use_figma:
```js
const ids=[/* 장면 프레임 id, spec 순서대로 */];
const tmp=figma.createFrame();tmp.name='EXPORT_TMP';tmp.resize(1080*ids.length,1920);tmp.x=0;tmp.y=2600;
tmp.fills=[{type:'SOLID',color:{r:0,g:0,b:0}}];tmp.clipsContent=true;
for(let i=0;i<ids.length;i++){const c=(await figma.getNodeByIdAsync(ids[i])).clone();tmp.appendChild(c);c.x=i*1080;c.y=0;
  // 프레임 안에 넣어둔 참고용 배경 사진은 복제본에서만 숨김 (원본은 그대로)
  for(const n of c.findAll(n=>/참고용|내보낼 때 숨김|^BG_/.test(n.name))) n.visible=false;}
return tmp.id;
```
2. `get_screenshot(nodeId=tmp, maxDimension=1080*N, contentsOnly=true)` → curl 로 `black.png`
3. use_figma: `tmp.fills=[{type:'SOLID',color:{r:1,g:1,b:1}}]` → **응답 받은 다음에** 스크린샷 → `white.png`
4. 흰 배경판 아래쪽 픽셀이 (255,255,255) 인지 확인 — 검정판과 같은 색이면 ① 3번이 반영 전에 찍혔거나 ② 프레임 안에 사진·불투명 층이 남은 것(층 이름 확인 후 숨김) (검정이면 3번이 반영 전에 찍힌 것 → 다시 찍기)
5. use_figma 로 tmp 삭제 → `matte --names` (ids 순서와 같게)
- 한 장면만 바뀌었으면 그 프레임만 넣어서 같은 방법

## E. Vrew 목소리
- 목소리는 **사용자가 Vrew에서 직접 고름**. Claude는 추천만 함
- 추천 목소리
  | 이름 | 성별 |
  |---|---|
  | **레다** | 여자 |
  | **태형** | 남자 |
- Vrew 대본을 줄 때 "추천 목소리: 레다(여)·태형(남) — 다른 목소리를 골라도 돼요"라고 함께 적어줌
- 속도·톤: Vrew 기본값
- 대본은 한 줄에 한 문장. 문장 사이 쉼은 Vrew 기본값이면 자동 자르기가 됨 (0.3초 이상)
- 내보내기: 오디오만 mp3

## F. 함정
- Pexels 영상은 장소 태그가 틀린 경우가 많음 → 썸네일·장면판으로 실제 그 장소인지 눈으로 확인
- 얼굴이 크게 나온 영상은 광고에서 초상권 문제 소지 → 뒷모습·원경 위주
- 음악은 Mixkit "Free License"만 (도구가 Restricted 자동 제외). Pexels 영상은 상업적 사용 가능
- ffmpeg 반복문은 도구 안에서 처리됨. 셸 변수명으로 `UID`, `GID` 쓰지 않기(zsh 예약어)
- 피그마 스크린샷 URL·Pexels 키는 출력·저장하지 않기
