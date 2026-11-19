// DA 릴스 피그마 오버레이 생성기 — use_figma 의 code 로 그대로 보냄
// 맨 위 SPEC 만 바꿔서 사용. 새 페이지에 섹션 + 장면별 1080×1920 투명 프레임 + 참고용 배경 사각형(BG)을 만든다.
// 반환값: { page, section, frames:{id:nodeId}, bgs:[BG nodeId…(장면 순서)] }
const SPEC = __SPEC__;

const FONTS = [["Black Han Sans","Regular"],["Noto Sans KR","Black"],["Noto Sans KR","Bold"],["Nanum Pen","Regular"]];
for (const f of FONTS) await figma.loadFontAsync({family:f[0],style:f[1]});
const Y={r:1,g:225/255,b:0}, P={r:1,g:59/255,b:92/255}, W={r:1,g:1,b:1};
const COL={yellow:Y,white:W,pink:P};
const SH=[{type:'DROP_SHADOW',color:{r:0,g:0,b:0,a:0.75},offset:{x:0,y:3},radius:14,spread:0,visible:true,blendMode:'NORMAL'},
          {type:'DROP_SHADOW',color:{r:0,g:0,b:0,a:0.35},offset:{x:0,y:0},radius:40,spread:0,visible:true,blendMode:'NORMAL'}];
function txt(s,fam,sty,size,col,o={}){const t=figma.createText();t.fontName={family:fam,style:sty};t.characters=s;t.fontSize=size;
  t.fills=[{type:'SOLID',color:col}];t.letterSpacing={unit:'PERCENT',value:o.ls??-2};if(o.lh)t.lineHeight={unit:'PERCENT',value:o.lh};
  t.textAlignHorizontal=o.align||'CENTER';t.effects=SH;return t;}
function hl(t,word,col=Y){if(!word)return;for(const w of [].concat(word)){const i=t.characters.indexOf(w);if(i>=0)t.setRangeFills(i,i+w.length,[{type:'SOLID',color:col}]);}}
function column(parent,y,align,sp=12){const c=figma.createFrame();c.name='문구';c.layoutMode='VERTICAL';c.primaryAxisSizingMode='AUTO';
  c.counterAxisSizingMode='AUTO';c.counterAxisAlignItems=align==='left'?'MIN':'CENTER';c.itemSpacing=sp;c.fills=[];c.clipsContent=false;parent.appendChild(c);c.y=y;return c;}
function place(c,align){c.x=align==='left'?80:Math.round((1080-c.width)/2);}
function grad(f,a=0.6,h=1100){const r=figma.createRectangle();r.name='상단 그라데이션';r.resize(1080,h);
  r.fills=[{type:'GRADIENT_LINEAR',gradientTransform:[[0,1,0],[-1,0,1]],gradientStops:[{position:0,color:{r:0,g:0,b:0,a}},{position:1,color:{r:0,g:0,b:0,a:0}}]}];f.appendChild(r);}
function softDark(f,cy,h,a=0.55){const e=figma.createEllipse();e.name='글씨 뒤 어둠(부드럽게)';e.resize(1500,h);e.x=-210;e.y=Math.round(cy-h/2);
  e.fills=[{type:'SOLID',color:{r:0,g:0,b:0},opacity:a}];e.effects=[{type:'LAYER_BLUR',radius:140,visible:true}];f.insertChild(f.children.findIndex(n=>n.name==='상단 그라데이션')+1,e);}  // 그라데이션 바로 위·글씨 아래
function big(parts){const s=parts.map(p=>p[0]).join('');const t=txt(s,'Black Han Sans','Regular',parts[0][1],W,{ls:-1,lh:100});let i=0;
  for(const [p,sz,c] of parts){t.setRangeFontSize(i,i+p.length,sz);t.setRangeFills(i,i+p.length,[{type:'SOLID',color:COL[c||'yellow']||Y}]);i+=p.length;}return t;}
function hand(s,size=86,rot=-2){const t=txt(s,'Nanum Pen','Regular',size,W,{ls:0});t.rotation=rot;return t;}

const page=figma.createPage();page.name=SPEC.title+' 오버레이';await figma.setCurrentPageAsync(page);
const sec=figma.createSection();sec.name=`${SPEC.title} (${SPEC.duration}초, 1080×1920)`;
const frames={},bgs=[];
SPEC.scenes.forEach((sc,i)=>{const x=i*1180;
  const bg=figma.createRectangle();bg.name='BG_참고용(내보내기 X) '+sc.id;bg.resize(1080,1920);bg.x=x;bg.y=0;bg.fills=[{type:'SOLID',color:{r:0.3,g:0.6,b:0.7}}];sec.appendChild(bg);bgs.push(bg.id);
  const f=figma.createFrame();f.name=`${sc.id}_${sc.name} ${sc.t[0]}-${sc.t[1]}s`;f.resize(1080,1920);f.x=x;f.y=0;f.fills=[];f.clipsContent=true;sec.appendChild(f);frames[sc.id]=f;});
sec.resizeWithoutConstraints(SPEC.scenes.length*1180+100,2100);

for(const sc of SPEC.scenes){const f=frames[sc.id];
  if(sc.type==='text'){  // 문구 묶음: label·lines·big·hand 를 order 순서대로 (기본 label,lines,big,hand)
    grad(f,0.6,(sc.y??300)>700?1920:1100);const al=sc.align||'center';const c=column(f,sc.y??300,al,sc.gap??12);
    for(const part of (sc.order||['label','lines','big','hand'])){
      if(part==='label'&&sc.label){c.appendChild(txt(sc.label.text,'Noto Sans KR',sc.label.color==='yellow'?'Black':'Bold',sc.label.size||46,COL[sc.label.color||'white'],{align:al==='left'?'LEFT':'CENTER'}));}
      if(part==='lines')for(const l of sc.lines||[]){const t=txt(l.text,'Noto Sans KR','Black',l.size||68,W,{align:al==='left'?'LEFT':'CENTER'});hl(t,l.hl);c.appendChild(t);}
      if(part==='big'&&sc.big){const b=big(sc.big);b.textAlignHorizontal=al==='left'?'LEFT':'CENTER';c.appendChild(b);}
      if(part==='hand'&&sc.hand)c.appendChild(hand(sc.hand,sc.handSize||86,al==='left'?-3:-2));
    }
    place(c,al);softDark(f,c.y+c.height/2,c.height+540,sc.dim??0.55);
  } else if(sc.type==='caption'){  // 말하는 자막: 화면 중간 아래, 라벨 없이 한두 줄
    const c=column(f,sc.y??980,'center',8);
    for(const l of sc.lines){const t=txt(l.text,'Noto Sans KR','Black',l.size||64,W);hl(t,l.hl);c.appendChild(t);}
    place(c,'center');softDark(f,c.y+c.height/2,c.height+420,sc.dim??0.5);
  } else if(sc.type==='bigword'){  // 화면을 채우는 큰 글자 하나(예: 핑/세/치, 10%) + 작은 설명
    const c=column(f,sc.y??380,sc.align||'center',0);
    const b=txt(sc.word,'Black Han Sans','Regular',sc.size||420,COL[sc.color||'yellow'],{ls:-3,lh:100});c.appendChild(b);
    if(sc.sub){const t=txt(sc.sub,'Noto Sans KR','Black',sc.subSize||60,W);hl(t,sc.subHl);c.appendChild(t);}
    place(c,sc.align||'center');softDark(f,c.y+c.height/2,c.height+300,sc.dim??0.45);
  } else if(sc.type==='tag'){
    const g=figma.createFrame();g.name='장소 태그';g.layoutMode='HORIZONTAL';g.primaryAxisSizingMode='AUTO';g.counterAxisSizingMode='AUTO';g.counterAxisAlignItems='CENTER';g.itemSpacing=16;g.fills=[];f.appendChild(g);
    const dot=figma.createEllipse();dot.resize(30,30);dot.fills=[{type:'SOLID',color:P}];dot.strokes=[{type:'SOLID',color:W}];dot.strokeWeight=5;g.appendChild(dot);
    const v=figma.createFrame();v.layoutMode='VERTICAL';v.primaryAxisSizingMode='AUTO';v.counterAxisSizingMode='AUTO';v.itemSpacing=0;v.fills=[];g.appendChild(v);
    v.appendChild(txt(sc.ko,'Black Han Sans','Regular',88,W,{align:'LEFT',ls:0}));
    if(sc.en)v.appendChild(txt(sc.en,'Noto Sans KR','Bold',30,W,{align:'LEFT',ls:12}));
    g.x=80;g.y=sc.y??1060;
  } else if(sc.type==='ending'&&sc.style==='oneliner'){  // 엔딩 변형: 큰 한 줄 + CTA
    grad(f,0.35,1920);const c=column(f,sc.y??520,'center',24);
    if(sc.label)c.appendChild(txt(sc.label,'Noto Sans KR','Bold',54,W));
    const t=txt(sc.title,'Noto Sans KR','Black',sc.size||96,W,{lh:120});hl(t,sc.titleHl);c.appendChild(t);
    c.appendChild(txt(sc.cta+'  ↓','Noto Sans KR','Black',84,Y));
    place(c,'center');softDark(f,c.y+c.height/2,c.height+560,0.6);
  } else if(sc.type==='ending'){
    grad(f,0.35,1920);
    const card=figma.createFrame();card.name='체크리스트';card.layoutMode='VERTICAL';card.primaryAxisSizingMode='AUTO';card.counterAxisSizingMode='AUTO';card.itemSpacing=34;card.fills=[];f.appendChild(card);
    if(sc.label)card.appendChild(txt(sc.label,'Noto Sans KR','Bold',54,W,{align:'LEFT'}));
    const tt=txt(sc.title,'Noto Sans KR','Black',86,W,{align:'LEFT',lh:125});hl(tt,sc.titleHl);card.appendChild(tt);
    const ln=figma.createRectangle();ln.resize(860,4);ln.fills=[{type:'SOLID',color:W,opacity:0.5}];card.appendChild(ln);
    for(const ck of sc.checks){const row=figma.createFrame();row.layoutMode='HORIZONTAL';row.primaryAxisSizingMode='AUTO';row.counterAxisSizingMode='AUTO';row.counterAxisAlignItems='CENTER';row.itemSpacing=22;row.fills=[];row.name=ck.text;card.appendChild(row);
      const box=figma.createFrame();box.resize(65,65);box.fills=[];row.appendChild(box);
      const v=figma.createVector();v.vectorPaths=[{windingRule:'NONE',data:'M 0 12 L 10 22 L 30 1'}];v.strokes=[{type:'SOLID',color:Y}];v.strokeWeight=8;v.strokeCap='ROUND';v.strokeJoin='ROUND';v.effects=SH;box.appendChild(v);v.x=17;v.y=21;
      const t=txt(ck.text,'Noto Sans KR','Black',ck.size||62,W,{align:'LEFT'});hl(t,ck.hl);row.appendChild(t);}
    card.x=Math.round((1080-card.width)/2);card.y=sc.y??275;
    const cta=txt(sc.cta+'  ↓','Noto Sans KR','Black',84,Y);f.appendChild(cta);cta.x=Math.round((1080-cta.width)/2);cta.y=card.y+card.height+80;
    softDark(f,(card.y+cta.y+cta.height)/2,(cta.y+cta.height-card.y)+560,0.6);
    if(cta.y+cta.height>1250) console.log('⚠️ 엔딩 CTA가 아래 35%(광고 버튼 자리)에 걸려요: '+(cta.y+cta.height));
  }
}
const warn=[];for(const sc of SPEC.scenes){const f=frames[sc.id];const c=f.findOne(n=>n.name==='문구');if(c&&c.y+c.height>1250)warn.push(sc.id+' 글씨가 아래 35%까지 내려감');if(c&&c.width>1000)warn.push(sc.id+' 글씨 폭 '+Math.round(c.width)+'px — 줄 나누기');}
return {page:page.id,section:sec.id,frames:Object.fromEntries(Object.entries(frames).map(([k,v])=>[k,v.id])),bgs,warn};
