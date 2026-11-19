#!/usr/bin/env python3
# DA 릴스 제작 도구 — 영상 찾기(Pexels API) · 컷 편집 · 투명 오버레이 · 목소리 맞추기 · 음악 깔기
# 사용: python3 dareels.py <명령> [옵션]   (명령 목록: python3 dareels.py -h)
# 작업 폴더(--dir) 안에 src/ still/ ov/ vo/ music/ sheet/ 를 만들어 씀
import argparse, builtins, json, os, re, subprocess, sys, time, urllib.request, urllib.parse

# 윈도우 대비: 글 파일은 항상 UTF-8 (윈도우 기본값 cp949 면 한글 대본·JSON 이 깨짐)
_open = builtins.open


def open(file, mode="r", *args, **kw):
    if "b" not in mode and "encoding" not in kw and not args:
        kw["encoding"] = "utf-8"
    return _open(file, mode, *args, **kw)


if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

FF = os.environ.get("DAREELS_FFMPEG", "ffmpeg")
FP = os.environ.get("DAREELS_FFPROBE", "ffprobe")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36"
W, H, FPS = 1080, 1920, 30


def run(cmd, quiet=True):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        sys.exit("명령 실패: " + " ".join(cmd[:6]) + " …\n" + r.stderr[-1500:])
    return r


def dur(path):
    return float(run([FP, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path]).stdout.strip())


def get(url, headers=None, binary=False, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})})
            with urllib.request.urlopen(req, timeout=60) as r:
                b = r.read()
                return b if binary else b.decode("utf-8", "replace")
        except Exception as e:
            if i == tries - 1:
                raise
            time.sleep(2 + i * 2)


HERE = os.path.dirname(os.path.abspath(__file__))


def read_key(name):
    """키 찾는 순서: 환경변수 → 스킬 폴더 keys/<name> (팀 공용) → ~/.da-reels/<name> (개인)"""
    k = os.environ.get(name.upper().replace("_KEY", "_API_KEY"))
    for p in (os.path.join(HERE, "..", "keys", name), os.path.expanduser("~/.da-reels/" + name)):
        if not k and os.path.exists(p):
            k = open(p).read().strip()
    return k


def pick_file(cands):
    """세로 영상은 폭 1080에 가까운 것, 가로 영상은 4K(높이 1920 이상)만 — 9:16으로 잘라도 안 흐리게"""
    v = [f for f in cands if f["h"] > f["w"]]
    if v:
        return sorted(v, key=lambda f: (abs(f["w"] - 1080), -f["w"]))[0], "세로"
    h = [f for f in cands if f["h"] >= 1900]
    if h:
        return sorted(h, key=lambda f: f["h"])[0], "가로4K"
    return None, None


def search_pexels(q, n, key):
    url = "https://api.pexels.com/videos/search?" + urllib.parse.urlencode(
        {"query": q, "orientation": "portrait", "per_page": n, "size": "medium"})
    out = []
    for v in json.loads(get(url, {"Authorization": key})).get("videos", []):
        files = [{"url": f["link"], "w": f["width"], "h": f["height"]} for f in v.get("video_files", [])
                 if f.get("width") and f.get("height") and f.get("file_type") == "video/mp4"]
        best, kind = pick_file(files)
        if best:
            out.append({"id": "px" + str(v["id"]), "page": v.get("url"), "duration": v.get("duration"), "file": best["url"],
                        "w": best["w"], "h": best["h"], "kind": kind, "thumb": v.get("image"), "site": "Pexels"})
    return out


def search_pixabay(q, n, key):
    url = "https://pixabay.com/api/videos/?" + urllib.parse.urlencode(
        {"key": key, "q": q, "per_page": max(3, min(n * 2, 200)), "safesearch": "true"})
    out = []
    for v in json.loads(get(url)).get("hits", []):
        vids = v.get("videos", {})
        files = [{"url": f["url"], "w": f.get("width", 0), "h": f.get("height", 0), "thumb": f.get("thumbnail")}
                 for f in vids.values() if f.get("url")]
        best, kind = pick_file(files)
        if best:
            th = next((f.get("thumbnail") for f in vids.values() if f.get("thumbnail")), None)
            out.append({"id": "pb" + str(v["id"]), "page": v.get("pageURL"), "duration": v.get("duration"), "file": best["url"],
                        "w": best["w"], "h": best["h"], "kind": kind, "thumb": th, "site": "Pixabay"})
    return sorted(out, key=lambda x: x["kind"] != "세로")[:n]


def font(size):
    from PIL import ImageFont
    for f in ["/System/Library/Fonts/AppleSDGothicNeo.ttc", "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
              "C:/Windows/Fonts/malgunbd.ttf", "C:/Windows/Fonts/malgun.ttf", "C:/Windows/Fonts/arialbd.ttf"]:
        if os.path.exists(f):
            return ImageFont.truetype(f, size)
    return ImageFont.load_default()


# ---------------------------------------------------------------- 1. 영상 찾기
def save_results(a, q, res):
    """검색 결과를 cand.json·groups.json 에 더하고 썸네일 받기"""
    os.makedirs(f"{a.dir}/sheet/th", exist_ok=True)
    cp, gp = f"{a.dir}/cand.json", f"{a.dir}/sheet/groups.json"
    cand = json.load(open(cp)) if os.path.exists(cp) else {}
    groups = json.load(open(gp)) if os.path.exists(gp) else []
    ids = []
    for r in res:
        r["query"] = q
        cand[r["id"]] = r
        th = f"{a.dir}/sheet/th/{r['id']}.jpg"
        if not os.path.exists(th) and r.get("thumb"):
            try:
                u = r["thumb"]
                if "images.pexels.com" in u:
                    u = u.split("?")[0] + "?auto=compress&h=360"
                open(th, "wb").write(get(u, binary=True))
            except Exception:
                pass
        if (not os.path.exists(th) or os.path.getsize(th) < 2000) and r.get("preview"):
            # 썸네일이 없으면 저화질 영상에서 1초 지점 한 장 뽑기
            subprocess.run([FF, "-nostdin", "-v", "error", "-y", "-ss", "1", "-i", r["preview"], "-frames:v", "1",
                            "-vf", "scale=-2:360", th], capture_output=True)
        ids.append(r["id"])
    groups = [g for g in groups if g[0] != q] + [[q, ids[:14]]]
    json.dump(cand, open(cp, "w"), ensure_ascii=False, indent=1)
    json.dump(groups, open(gp, "w"), ensure_ascii=False)
    print(f"{q}: {len(ids)}개 (세로 {sum(cand[i]['kind'] == '세로' for i in ids)})")
    return cand, groups


def make_sheets(a, cand, groups):
    from PIL import Image, ImageDraw
    f1, f2 = font(22), font(16)
    for gi in range(0, len(groups), 3):
        rows = groups[gi:gi + 3]
        S = Image.new("RGB", (14 * 150, len(rows) * 300), "white")
        d = ImageDraw.Draw(S)
        for ri, (q, ids) in enumerate(rows):
            y = ri * 300
            d.text((5, y + 2), q, fill="black", font=f1)
            for ci, vid in enumerate(ids[:14]):
                p = f"{a.dir}/sheet/th/{vid}.jpg"
                try:
                    im = Image.open(p).convert("RGB")
                except Exception:
                    d.text((ci * 150 + 3, y + 60), f"{vid}\n(미리보기 없음)", fill="black", font=f2)
                    continue
                if im.width > im.height:  # 가로 영상은 가운데 9:16 만 보여줌 (실제로 쓰일 부분)
                    cw = int(im.height * 9 / 16)
                    im = im.crop(((im.width - cw) // 2, 0, (im.width - cw) // 2 + cw, im.height))
                im.thumbnail((150, 266))
                S.paste(im, (ci * 150, y + 30))
                d.rectangle([ci * 150, y + 30, ci * 150 + 138, y + 52], fill="black")
                d.text((ci * 150 + 3, y + 31), f"{vid} {cand[vid].get('duration') or ''}", fill="yellow", font=f2)
                if cand[vid].get("kind") == "가로4K":
                    d.rectangle([ci * 150, y + 274, ci * 150 + 70, y + 294], fill="red")
                    d.text((ci * 150 + 3, y + 275), "가로", fill="white", font=f2)
        out = f"{a.dir}/sheet/search_{gi // 3 + 1}.jpg"
        S.save(out, quality=80)
        print("미리보기:", out)


def cmd_search(a):
    """키 방식: Pixabay(또는 Pexels) 공식 API"""
    pb, px = read_key("pixabay_key"), read_key("pexels_key")
    if not (pb or px):
        sys.exit("영상 검색 키가 없어요. 클로드 크롬이 있으면 reference.md 'Pexels 크롬 검색' 방식(import)을 쓰고, "
                 "아니면 https://pixabay.com/api/docs/ 키를 스킬 폴더 keys/pixabay_key 에 저장해 주세요.")
    cand, groups = {}, []
    for q in a.q:
        res = (search_pexels(q, a.n, px) if px else []) + (search_pixabay(q, a.n, pb) if pb else [])
        cand, groups = save_results(a, q, res)
    make_sheets(a, cand, groups)


def cmd_import(a):
    """크롬 방식: 클로드 크롬으로 Pexels 검색 페이지에서 뽑은 JSON 을 후보로 등록"""
    raw = json.load(open(a.json))
    res = []
    for it in raw:
        files = []
        for f in it.get("files", []):
            m = re.search(r"_(\d+)_(\d+)_[\d.]+fps\.mp4$", f)
            if m:
                files.append({"url": "https://videos.pexels.com/" + f.lstrip("/"), "w": int(m.group(1)), "h": int(m.group(2))})
        best, kind = pick_file(files)
        if best:
            small = sorted(files, key=lambda f: f["w"] * f["h"])[0]["url"]
            res.append({"id": "px" + str(it["id"]), "page": it.get("page"), "duration": it.get("duration"),
                        "file": best["url"], "w": best["w"], "h": best["h"], "kind": kind,
                        "thumb": it.get("thumb"), "preview": small, "site": "Pexels"})
    cand, groups = save_results(a, a.q, res)
    make_sheets(a, cand, groups)


def cmd_fetch(a):
    cand = json.load(open(f"{a.dir}/cand.json"))
    os.makedirs(f"{a.dir}/src", exist_ok=True)
    for vid in a.ids.split(","):
        vid = vid.strip()
        out = f"{a.dir}/src/{vid}.mp4"
        if os.path.exists(out) and os.path.getsize(out) > 10000:
            continue
        open(out, "wb").write(get(cand[vid]["file"], binary=True))
        print(vid, f"{os.path.getsize(out) / 1e6:.1f}MB", f"{dur(out):.1f}s")


def cmd_strips(a):
    from PIL import Image, ImageDraw
    src = sorted(f[:-4] for f in os.listdir(f"{a.dir}/src") if f.endswith(".mp4"))
    os.makedirs(f"{a.dir}/sheet/fr", exist_ok=True)
    f1, f2 = font(15), font(14)
    for part in range(0, len(src), 10):
        ids = src[part:part + 10]
        S = Image.new("RGB", (6 * 135 + 90, len(ids) * 240), "white")
        d = ImageDraw.Draw(S)
        for r, vid in enumerate(ids):
            p = f"{a.dir}/src/{vid}.mp4"
            D = dur(p)
            d.text((2, r * 240 + 100), vid, fill="black", font=f1)
            for k in range(6):
                t = round(D * (k + 0.5) / 6, 1)
                fr = f"{a.dir}/sheet/fr/{vid}_{k}.jpg"
                run([FF, "-nostdin", "-v", "error", "-y", "-ss", str(t), "-i", p, "-frames:v", "1",
                     "-vf", "scale=135:240:force_original_aspect_ratio=increase,crop=135:240", fr])
                S.paste(Image.open(fr), (90 + k * 135, r * 240))
                d.rectangle([90 + k * 135, r * 240, 90 + k * 135 + 40, r * 240 + 16], fill="black")
                d.text((92 + k * 135, r * 240), str(t), fill="yellow", font=f2)
        out = f"{a.dir}/sheet/strip_{part // 10 + 1}.jpg"
        S.save(out, quality=80)
        print("장면판:", out)


# ---------------------------------------------------------------- 2. 컷 편집
def read_cuts(path):
    """cuts.txt 한 줄 = 컷 하나
    영상: <영상번호> <시작초> <길이>
    사진: p <사진파일> <길이> [가로중심 0~1] [세로중심 0~1]  (9:16으로 잘라 천천히 확대)"""
    cuts = []
    for line in open(path):
        line = line.split("#")[0].strip()
        if not line:
            continue
        t = line.split()
        if t[0] == "v":
            t = t[1:]
        if t[0] == "p":
            cx = float(t[3]) if len(t) > 3 else 0.5
            cy = float(t[4]) if len(t) > 4 else 0.5
            cuts.append(("p", t[1], float(t[2]), cx, cy))
        else:
            cuts.append(("v", t[0], float(t[1]), float(t[2])))
    return cuts


def find_photo(d, name):
    for c in (name, f"{d}/src/{name}", f"{d}/src/{name}.jpg", f"{d}/src/p{name}.jpg", f"{d}/photos/{name}",
              f"{d}/photos/{name}.jpg", f"{d}/photos/p{name}.jpg"):
        if os.path.exists(os.path.expanduser(c)):
            return os.path.expanduser(c)
    sys.exit(f"사진을 못 찾았어요: {name} (작업 폴더 src/ 나 photos/ 에 넣어 주세요)")


def ken_burns(src, out, d, cx, cy, zoom=0.06):
    """사진 천천히 확대. ffmpeg zoompan 은 위치를 정수 픽셀로 끊어 움직여서 형광등처럼 떨림 →
    Pillow 로 소수점 위치까지 계산해 프레임마다 직접 그림"""
    from PIL import Image
    im = Image.open(src).convert("RGB")
    iw, ih = im.size
    if iw / ih > W / H:
        bh, bw = ih, ih * W / H
    else:
        bw, bh = iw, iw * H / W
    bx, by = (iw - bw) * cx, (ih - bh) * cy
    fr = round(d * FPS)
    p = subprocess.Popen([FF, "-nostdin", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                          "-r", str(FPS), "-i", "-", "-vf", "setsar=1,format=yuv420p", "-an", "-c:v", "libx264",
                          "-crf", "15", out], stdin=subprocess.PIPE)
    for n in range(fr):
        z = 1.0 + zoom * n / max(fr - 1, 1)
        w, h = bw / z, bh / z
        x0, y0 = bx + (bw - w) / 2, by + (bh - h) / 2
        p.stdin.write(im.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + w, y0 + h)).tobytes())
    p.stdin.close()
    if p.wait():
        sys.exit(f"사진 컷 만들기 실패: {src}")


def cmd_build(a):
    cuts = read_cuts(f"{a.dir}/cuts.txt")
    os.makedirs(f"{a.dir}/seg", exist_ok=True)
    segs, c, rows = [], 0.0, []
    for i, cut in enumerate(cuts):
        o = f"{a.dir}/seg/seg_{i + 1:02d}.mp4"
        if cut[0] == "v":
            _, vid, ss, d = cut
            src = f"{a.dir}/src/{vid}.mp4"
            if ss + d > dur(src) + 0.01:
                sys.exit(f"{vid}: {ss}+{d}초가 원본 길이 {dur(src):.1f}초를 넘어요")
            run([FF, "-nostdin", "-v", "error", "-y", "-ss", str(ss), "-i", src, "-t", str(d), "-vf",
                 f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,crop={W}:{H},fps={FPS},setsar=1,"
                 "eq=saturation=1.08,format=yuv420p", "-an", "-c:v", "libx264", "-crf", "15", o])
            rows.append(f"컷{i + 1:>2} 영상 {vid} {ss}초부터")
        else:
            _, name, d, cx, cy = cut
            ken_burns(find_photo(a.dir, name), o, d, cx, cy)
            rows.append(f"컷{i + 1:>2} 사진 {name}")
        segs.append((o, d))
    lst = f"{a.dir}/seg/list.txt"
    open(lst, "w").write("".join("file '%s'\n" % os.path.abspath(o).replace("\\", "/") for o, _ in segs))
    out = f"{a.dir}/bg.mp4"
    run([FF, "-nostdin", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", out])
    for r, (o, d) in zip(rows, segs):
        print(f"{r}  {c:5.2f}~{c + d:5.2f}s")
        c += d
    print(f"배경 영상 {out} 총 {dur(out):.2f}초")
    os.makedirs(f"{a.dir}/still", exist_ok=True)
    c = 0
    for i, (o, d) in enumerate(segs):
        run([FF, "-nostdin", "-v", "error", "-y", "-ss", str(d / 2), "-i", o, "-frames:v", "1", "-q:v", "3",
             f"{a.dir}/still/c{i + 1}.jpg"])


# ---------------------------------------------------------------- 3. 투명 오버레이
def cmd_matte(a):
    names = a.names.split(",")
    os.makedirs(f"{a.dir}/ov", exist_ok=True)
    for i, n in enumerate(names):
        x = i * W
        run([FF, "-nostdin", "-v", "error", "-y", "-i", a.black, "-i", a.white, "-filter_complex",
             f"[0:v]crop={W}:{H}:{x}:0,format=gbrp,split[b1][b2];[1:v]crop={W}:{H}:{x}:0,format=gbrp[w];"
             "[w][b1]blend=all_mode=difference,format=gray,negate[al];"
             "[b2][al]alphamerge,format=gbrap,unpremultiply=inplace=1,format=rgba",
             "-frames:v", "1", f"{a.dir}/ov/{n}.png"])
    print("투명 PNG:", ", ".join(f"ov/{n}.png" for n in names))


def read_spec(path):
    sp = []
    for line in open(path):
        line = line.split("#")[0].strip()
        if line:
            n, s, e = line.split()[:3]
            sp.append((n, float(s), float(e)))
    return sp


def cmd_overlay(a):
    sp = read_spec(f"{a.dir}/spec.txt")
    total = dur(f"{a.dir}/bg.mp4")
    args, fc, prev = ["-i", f"{a.dir}/bg.mp4"], "", "0:v"
    last = max(e for _, _, e in sp)
    for k, (n, s, e) in enumerate(sp, 1):
        if e == last:  # 영상이 프레임 반올림으로 조금 더 길어도 마지막 장면 자막이 끝까지 깔리게 (빈 마지막 프레임 방지)
            e = max(e, total + 1)
        args += ["-loop", "1", "-t", f"{total:.3f}", "-i", f"{a.dir}/ov/{n}.png"]
        fd = "" if s == 0 else f",fade=in:st={s}:d=0.15:alpha=1"
        fc += f"[{k}:v]format=rgba{fd}[o{k}];[{prev}][o{k}]overlay=0:0:enable='between(t,{s},{e - 0.001})'[m{k}];"
        prev = f"m{k}"
    out = f"{a.dir}/novoice.mp4"
    run([FF, "-nostdin", "-v", "error", "-y", *args, "-filter_complex", fc.rstrip(";"), "-map", f"[{prev}]",
         "-t", f"{total:.3f}", "-r", str(FPS), "-c:v", "libx264", "-profile:v", "high", "-crf", "17",
         "-pix_fmt", "yuv420p", "-movflags", "+faststart", out])
    print("자막 합친 영상:", out)


# ---------------------------------------------------------------- 4. 목소리 맞추기
def silences(path, db=-38, d=0.08):
    err = run([FF, "-nostdin", "-i", path, "-af", f"silencedetect=noise={db}dB:d={d}", "-f", "null", "-"]).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
    en = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    return list(zip(st, en + [dur(path)] * (len(st) - len(en))))


def cmd_voice(a):
    """vo_script.txt: 장면번호|장면시작초|장면끝초|문장  — 녹음 1개를 문장별로 잘라 장면 시작에 배치"""
    lines = []
    for l in open(f"{a.dir}/vo_script.txt"):
        l = l.strip()
        if l and not l.startswith("#"):
            n, s, e, t = l.split("|", 3)
            lines.append((n, float(s), float(e), t))
    N = len(lines)
    total = dur(a.mp3)
    sil = silences(a.mp3)
    head = sil[0][1] if sil and sil[0][0] < 0.05 else 0.0
    tail = sil[-1][0] if sil and sil[-1][1] >= total - 0.05 else total
    gaps = [(s, e) for s, e in sil if s > head + 0.2 and e < tail - 0.2]
    w = [max(1, len(re.sub(r"[\s,.!?~·…]", "", t))) for _, _, _, t in lines]
    W_ = sum(w)
    speech = tail - head
    # 동적 계획법: 쉼 K개 중 N-1개를 골라 문장 길이(글자 수 비율)와 가장 잘 맞게 자르기
    pts = [(head, head)] + gaps + [(tail, tail)]
    K = len(pts)
    INF = 1e9
    best = [[INF] * K for _ in range(N + 1)]
    back = [[-1] * K for _ in range(N + 1)]
    best[0][0] = 0
    for i in range(1, N + 1):
        for j in range(1, K):
            for p in range(j):
                if best[i - 1][p] >= INF:
                    continue
                seg = pts[j][0] - pts[p][1]
                if seg <= 0.2:
                    continue
                cost = (seg / speech - w[i - 1] / W_) ** 2
                gap_len = pts[j][1] - pts[j][0]
                cost -= 0.002 * min(gap_len, 0.6) if j < K - 1 else 0
                if best[i - 1][p] + cost < best[i][j]:
                    best[i][j] = best[i - 1][p] + cost
                    back[i][j] = p
    if best[N][K - 1] >= INF:
        sys.exit(f"녹음에서 문장 {N}개로 나눌 쉼을 못 찾았어요. Vrew에서 문장 사이를 조금 더 띄워 다시 내보내 주세요.")
    idx, j = [], K - 1
    for i in range(N, 0, -1):
        idx.append(j)
        j = back[i][j]
    idx.append(0)
    idx = idx[::-1]
    segs = [(pts[idx[i]][1], pts[idx[i + 1]][0]) for i in range(N)]
    os.makedirs(f"{a.dir}/vo", exist_ok=True)
    parts, lab = [], ""
    fc = f"[0:a]highpass=f=70,aformat=sample_rates=48000:channel_layouts=stereo,asplit={N}" + "".join(
        f"[s{i}]" for i in range(N)) + ";"
    report = []
    prev_end = -1.0
    for i, ((n, s, e, t), (a0, b0)) in enumerate(zip(lines, segs)):
        a0, b0 = max(0, a0 - 0.03), min(total, b0 + 0.06)
        d = b0 - a0
        start = max(s + 0.05, prev_end + 0.08)  # 앞 문장과 겹치지 않게 (앞 문장이 길면 살짝 뒤로)
        room = e - start - 0.05
        tempo = 1.0 if d <= room else min(1.12, d / max(room, 0.1))
        end = start + d / tempo
        prev_end = end
        ms = int(start * 1000)
        fo = max(0.0, d - 0.04)
        fc += (f"[s{i}]atrim={a0:.3f}:{b0:.3f},asetpts=PTS-STARTPTS,afade=t=in:d=0.02,"
               f"afade=t=out:st={fo:.3f}:d=0.04,atempo={tempo:.3f},adelay={ms}|{ms}[c{i}];")
        lab += f"[c{i}]"
        warn = " ⚠️다음 장면으로 %.2f초 넘어감" % (end - e) if end > e + 0.05 else ""
        report.append(f"{n} 녹음 {a0:5.2f}~{b0:5.2f}s → 영상 {start:5.2f}~{end:5.2f}s (장면 {s}~{e}) "
                      f"속도 {tempo:.2f}배{warn} | {t}")
    vdur = a.total or dur(f"{a.dir}/novoice.mp4")
    run([FF, "-nostdin", "-v", "error", "-y", "-i", a.mp3, "-filter_complex",
         f"{fc}{lab}amix=inputs={N}:normalize=0,apad,atrim=0:{vdur:.3f},loudnorm=I=-14:TP=-1.5:LRA=11[out]",
         "-map", "[out]", "-ar", "48000", f"{a.dir}/vo/vo.wav"])
    print("\n".join(report))
    print("목소리 트랙:", f"{a.dir}/vo/vo.wav")


# ---------------------------------------------------------------- 5. 음악
MIXKIT_PAGES = ["tag/summer", "tag/beach", "mood/happy", "discover/house", "discover/pop", "discover/travel",
                "discover/chill", "discover/latin", "discover/winter"]  # 도시 분위기에 맞춰 --pages discover/<영어 단어> 로 추가


def cmd_music(a):
    os.makedirs(f"{a.dir}/music", exist_ok=True)
    seen = {}
    for p in (a.pages.split(",") if a.pages else MIXKIT_PAGES):
        try:
            h = get(f"https://mixkit.co/free-stock-music/{p}/")
        except Exception as e:
            print(p, "실패", e)
            continue
        for m in re.finditer(r'\{"@id":"[^"]*","@type":"MusicRecording".*?"datePublished":"[^"]+"\}', h):
            d = json.loads(m.group(0))
            if "Free" not in d.get("copyrightNotice", "") or "Restricted" in d.get("copyrightNotice", ""):
                continue
            mid = d["url"].split("/")[-1][:-4]
            seen[mid] = {"name": d["name"], "genre": d["genre"], "duration": d["duration"], "url": d["url"],
                         "license": d["copyrightNotice"], "page": p}
        time.sleep(1.5)
    json.dump(seen, open(f"{a.dir}/music/list.json", "w"), ensure_ascii=False, indent=1)
    skip = {"Children", "Country", "Bluegrass", "Folk", "Christmas"}
    for mid, d in seen.items():
        if d["genre"] not in skip:
            print(mid, "|", d["name"], "|", d["genre"], "|", d["duration"])
    print(f"(어린이·컨트리·포크 장르 제외하고 표시, 전체 {len(seen)}곡은 music/list.json)")


def loud_window(path, win):
    err = run([FF, "-nostdin", "-i", path, "-af", "aresample=44100,asetnsamples=44100,astats=metadata=1:reset=1,"
               "ametadata=print:key=lavfi.astats.Overall.RMS_level", "-f", "null", "-"]).stderr
    L = [float(x) if x not in ("-inf", "inf") else -90 for x in re.findall(r"RMS_level=(-?[\d.]+|-?inf)", err)]
    n = int(win) + 1
    if len(L) <= n + 4:
        return 0
    return max(range(4, len(L) - n), key=lambda i: sum(L[i:i + n]))


def cmd_mix(a):
    video = f"{a.dir}/novoice.mp4"
    T = dur(video)
    has_vo = os.path.exists(f"{a.dir}/vo/vo.wav") and not a.no_voice
    outs = []
    for mid in a.music.split(","):
        mid = mid.strip()
        mp3 = f"{a.dir}/music/{mid}.mp3"
        if not os.path.exists(mp3):
            open(mp3, "wb").write(get(f"https://assets.mixkit.co/music/{mid}/{mid}.mp3", binary=True))
        st = a.start if a.start is not None else loud_window(mp3, T)
        mus = (f"[m0]aresample=48000,aformat=channel_layouts=stereo,loudnorm=I=-20:TP=-2,volume={a.music_db}dB,"
               f"afade=t=in:d=0.25,afade=t=out:st={T - 1.3:.2f}:d=1.3[m]")
        if has_vo:
            inputs = ["-i", f"{a.dir}/vo/vo.wav", "-ss", str(st), "-t", f"{T:.3f}", "-i", mp3]
            fc = (mus.replace("[m0]", "[1:a]") + ";[0:a]asplit[v][key];"
                  "[m][key]sidechaincompress=threshold=0.04:ratio=5:attack=15:release=350[md];"
                  f"[v][md]amix=inputs=2:normalize=0,atrim=0:{T:.3f},loudnorm=I=-14:TP=-1.5:LRA=11[out]")
        else:
            inputs = ["-ss", str(st), "-t", f"{T:.3f}", "-i", mp3]
            fc = mus.replace("[m0]", "[0:a]").replace("[m]", ",loudnorm=I=-14:TP=-1.5[out]")
        wav = f"{a.dir}/music/mix_{mid}.wav"
        run([FF, "-nostdin", "-v", "error", "-y", *inputs, "-filter_complex", fc, "-map", "[out]", "-ar", "48000", wav])
        out = f"{a.dir}/{a.name}_{mid}.mp4"
        run([FF, "-nostdin", "-v", "error", "-y", "-i", video, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
             "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", out])
        print(f"완성: {out} (음악 {mid} {st}초부터)")
        outs.append(out)


def cmd_check(a):
    from PIL import Image
    ts = [float(x) for x in a.times.split(",")]
    os.makedirs(f"{a.dir}/sheet/chk", exist_ok=True)
    S = Image.new("RGB", (len(ts) * 270, 480))
    for i, t in enumerate(ts):
        p = f"{a.dir}/sheet/chk/{i}.jpg"
        run([FF, "-nostdin", "-v", "error", "-y", "-ss", str(t), "-i", a.video, "-frames:v", "1", "-vf", "scale=270:480", p])
        S.paste(Image.open(p), (i * 270, 0))
    out = f"{a.dir}/sheet/check.jpg"
    S.save(out, quality=85)
    print("확인판:", out)


def main():
    P = argparse.ArgumentParser(description="DA 릴스 제작 도구")
    P.add_argument("--dir", required=True, help="작업 폴더")
    sp = P.add_subparsers(dest="cmd", required=True)
    s = sp.add_parser("search", help="Pexels 세로 영상 검색 + 미리보기판")
    s.add_argument("--q", action="append", required=True)
    s.add_argument("--n", type=int, default=14)
    s = sp.add_parser("import", help="클로드 크롬으로 뽑은 Pexels 검색 결과 JSON 등록")
    s.add_argument("--json", required=True)
    s.add_argument("--q", required=True)
    s = sp.add_parser("fetch", help="고른 영상 원본 받기")
    s.add_argument("--ids", required=True)
    sp.add_parser("strips", help="받은 영상별 6장면 미리보기판")
    sp.add_parser("build", help="cuts.txt → bg.mp4 + 컷별 정지화면")
    s = sp.add_parser("matte", help="검정·흰 배경판 → 투명 PNG")
    s.add_argument("--black", required=True)
    s.add_argument("--white", required=True)
    s.add_argument("--names", required=True)
    sp.add_parser("overlay", help="spec.txt 대로 오버레이 합치기 → novoice.mp4")
    s = sp.add_parser("voice", help="Vrew 녹음을 문장별로 잘라 장면에 배치 → vo/vo.wav")
    s.add_argument("--mp3", required=True)
    s.add_argument("--total", type=float)
    s = sp.add_parser("music", help="Mixkit 무료 음악 후보 목록")
    s.add_argument("--pages")
    s = sp.add_parser("mix", help="음악(+목소리) 합쳐 완성본")
    s.add_argument("--music", required=True, help="Mixkit 곡 번호, 쉼표로 여러 개")
    s.add_argument("--name", default="final")
    s.add_argument("--start", type=float)
    s.add_argument("--music-db", type=float, default=-4)
    s.add_argument("--no-voice", action="store_true")
    s = sp.add_parser("check", help="지정 시점 프레임 확인판")
    s.add_argument("--video", required=True)
    s.add_argument("--times", required=True)
    a = P.parse_args()
    os.makedirs(a.dir, exist_ok=True)
    globals()["cmd_" + a.cmd](a)


if __name__ == "__main__":
    main()
