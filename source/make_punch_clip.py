# Builds the punch easter-egg clip from Austin's video: from ~3.8 s, crop to hand + phone, track the UFC octagon
# (red ring) during the phone phase and cover it with Dylan's emblem, crop off the UFC text strip. No audio.
import cv2, numpy as np, subprocess, shutil, json, hashlib
from pathlib import Path
from PIL import Image
R = Path(__file__).resolve().parent; E = R / 'private/egg'; OUT = E / 'frames'; shutil.rmtree(OUT, ignore_errors=True); OUT.mkdir()
T0, PHONE_END = 3.8, 5.3                      # seconds: start of clip, end of octagon phase
X0, X1, Y0, Y1 = 240, 1040, 0, 535            # crop (full-res coords) keeps hand+phone, drops UFC text/button
emb = Image.open(R / 'public/assets/dkainsworld-emblem.webp').convert('RGBA')
cap = cv2.VideoCapture(str(E / 'src.mp4')); fps = cap.get(cv2.CAP_PROP_FPS); cap.set(cv2.CAP_PROP_POS_MSEC, T0 * 1000)
n = 0; last = None; log = []
while True:
    ok, fr = cap.read()
    if not ok: break
    t = T0 + n / fps
    if t < PHONE_END:
        hsv = cv2.cvtColor(fr, cv2.COLOR_BGR2HSV); h, s, v = cv2.split(hsv)
        red = (((h < 8) | (h > 170)) & (s > 150) & (v > 90)).astype(np.uint8)
        red[:80] = 0; red[:, :300] = 0; red[:, 980:] = 0; red[660:] = 0
        ys, xs = np.nonzero(red)
        if len(xs) > 400:
            box = (np.percentile(xs, 1), np.percentile(ys, 1), np.percentile(xs, 99), np.percentile(ys, 99))
            last = box if last is None else tuple(0.6 * a + 0.4 * b for a, b in zip(box, last))   # smooth jitter
        if last is not None:
            x0, y0, x1, y1 = last; cx, cy = (x0 + x1) / 2, (y0 + y1) / 2; side = max(x1 - x0, y1 - y0) * 1.18
            # white plate (phone screen) + emblem on top, both cover the octagon
            im = Image.fromarray(cv2.cvtColor(fr, cv2.COLOR_BGR2RGB)).convert('RGBA')
            plate = Image.new('RGBA', (int(side * 1.02), int(side * 1.02)), (250, 250, 250, 255))
            mask = Image.new('L', plate.size, 0); cv2_mask = np.zeros((plate.size[1], plate.size[0]), np.uint8)
            cv2.circle(cv2_mask, (plate.size[0] // 2, plate.size[1] // 2), plate.size[0] // 2, 255, -1); mask = Image.fromarray(cv2.GaussianBlur(cv2_mask, (0, 0), 3))
            im.paste(plate, (int(cx - plate.size[0] / 2), int(cy - plate.size[1] / 2)), mask)
            e = emb.copy(); ew = int(side * 1.55); e = e.resize((ew, int(ew * e.height / e.width)), Image.LANCZOS)
            im.alpha_composite(e, (int(cx - e.width / 2), int(cy - e.height / 2)))
            fr = cv2.cvtColor(np.asarray(im.convert('RGB')), cv2.COLOR_RGB2BGR)
            log.append({'t': round(t, 3), 'box': [round(x) for x in last]})
    cv2.imwrite(str(OUT / f'{n:04d}.png'), fr[Y0:Y1, X0:X1]); n += 1
print('frames', n, 'tracked', len(log))
pub = R / 'public/assets'
common = ['-framerate', str(fps), '-i', str(OUT / '%04d.png'), '-vf', 'scale=640:-2,scale=in_range=pc:out_range=tv:out_color_matrix=bt709', '-color_range', 'tv', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-an']
subprocess.run(['ffmpeg', '-v', 'error', '-y', *common, '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '24', '-preset', 'slow', '-movflags', '+faststart', str(pub / 'punch.mp4')], check=True)
subprocess.run(['ffmpeg', '-v', 'error', '-y', *common, '-c:v', 'libvpx-vp9', '-pix_fmt', 'yuv420p', '-crf', '34', '-b:v', '0', str(pub / 'punch.webm')], check=True)
cv2.imwrite(str(pub / '../../private/egg/poster.jpg'), cv2.imread(str(OUT / '0000.png')))
(E / 'clip-provenance.json').write_text(json.dumps({'source': 'owner video (Gemini-generated) a1713845', 'start_s': T0, 'crop': [X0, Y0, X1, Y1], 'octagon_covered_until_s': PHONE_END, 'tracked_frames': len(log),
  'files': {f: hashlib.sha256((pub / f).read_bytes()).hexdigest() for f in ['punch.mp4', 'punch.webm']}}, indent=1))
for f in ['punch.mp4', 'punch.webm']: print(f, (pub / f).stat().st_size // 1024, 'KB')
