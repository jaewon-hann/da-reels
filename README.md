# DA 릴스 스킬 설치 안내 (맥·윈도우)

프모페 링크와 USP만 주면 Claude가 칸쿤 릴스처럼 9:16 광고 영상을 만들어 줘요.
영상 찾기 → 컷 편집 → 피그마 자막 → 음악까지 자동이고, 목소리만 Vrew에서 직접 뽑아 주면 돼요.

## 1. 처음 한 번만
1. **스킬 넣기**: 터미널에 아래 한 줄 붙여넣기
   ```
   git clone https://github.com/jaewon-hann/da-reels.git ~/.claude/skills/da-reels
   ```
   - 깃이 어렵다면: 이 페이지 초록색 `Code` → `Download ZIP` → 압축 풀고 폴더 이름을 `da-reels` 로 바꿔 `~/.claude/skills/` 안에 복사 (파인더 `Cmd+Shift+G` → `~/.claude/skills`)
   - 업데이트: `git -C ~/.claude/skills/da-reels pull`
2. **Claude Code 재시작** 후 `/da-reels 점검` 입력 → Claude가 필요한 프로그램(ffmpeg 등)을 확인·설치해 줘요
   - Homebrew가 없다고 나오면 https://brew.sh 의 설치 명령을 터미널에 붙여넣고 다시 점검
3. **클로드 크롬 설치 (영상 찾기용)**: 크롬 웹스토어에서 "Claude" 확장 설치 → 로그인 → Claude Code에서 `/chrome` 입력해 연결
   - Claude가 내 크롬에 새 탭을 열어 Pexels에서 영상을 찾아요 (작업 중 그 탭은 건드리지 않기)
   - Pexels 가입·API 키는 필요 없어요
   - 크롬 연결이 끝내 안 되면 대안: pixabay.com 가입 → API 키를 스킬 폴더 `keys/pixabay_key` 파일에 저장
4. **피그마 연결**: Claude Code에서 `/mcp` → figma 로그인 (이미 돼 있으면 생략)
5. **Vrew 가입·로그인**: https://vrew.ai (무료) — 목소리 만들 때 사용

### 윈도우라면 (위 1~2번 대신)
1. Git Bash 에서 `git clone https://github.com/jaewon-hann/da-reels.git ~/.claude/skills/da-reels`
   - 또는 `Download ZIP` → 폴더 이름 `da-reels` 로 `C:\Users\<내 이름>\.claude\skills\` 안에 복사 (탐색기 주소창에 `%USERPROFILE%\.claude\skills`)
2. Claude Code 재시작 후 `/da-reels 점검` → ffmpeg·파이썬을 확인하고 없으면 설치해 줘요
   - ffmpeg 를 새로 깔았다면 Claude Code 를 한 번 더 껐다 켜 주세요
3. 나머지(클로드 크롬, 피그마, Vrew)는 맥과 같아요
- ⚠️ 윈도우는 아직 실제로 돌려본 적이 없어요. 처음 쓰다 막히면 화면 그대로 스킬 공유자에게 알려 주세요

## 2. 쓰는 법
```
/da-reels https://www.myrealtrip.com/promotions/XXXX
USP: (혜택·차별점을 줄줄이)
피그마: (오버레이 만들 피그마 파일 링크)
```
1. Claude가 **장면표·대본**을 보여줘요 → 고칠 것 말하거나 "ㄱㄱ"
2. 영상·피그마 자막이 만들어지면 무음본을 먼저 보여줘요 (피그마에서 직접 고쳐도 돼요)
3. Claude가 준 **Vrew 대본**을 Vrew에 붙여넣고 원하는 목소리로 mp3 내보내기 → 파일 경로를 Claude에게
   - 추천 목소리: **레다**(여), **태형**(남). 다른 목소리를 골라도 돼요
4. 음악 3가지 버전이 나오면 골라서 끝

## 알아둘 것
- 자막 연출은 프로모션마다 USP 특성에 맞춰 새로 구상해요 (예: 여러 장소 투어 → 장소 위치 태그, 쿠폰 → 숫자 크게)
- 영상 문구는 USP·프모페에 있는 사실만 써요. 과장 표현이 필요하면 USP에 적어 주세요
- 영상은 Pexels, 음악은 Mixkit 무료 라이선스(상업적 사용 가능)
- 결과물은 `~/da-reels/<도시>_<날짜>/` 에 저장돼요
