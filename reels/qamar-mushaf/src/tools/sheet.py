# Контакт-лист кадров: python3 tools/sheet.py stills/ sheet.jpg [колонок]
import sys, glob, os
from PIL import Image, ImageDraw
src, out = sys.argv[1], sys.argv[2]
cols = int(sys.argv[3]) if len(sys.argv) > 3 else 6
fs = sorted(glob.glob(os.path.join(src, 't_*.jpg')), key=lambda f: float(os.path.basename(f)[2:-4]))
W, H = 360, 640
sheet = Image.new('RGB', (W * cols, (H + 30) * ((len(fs) + cols - 1) // cols)), 'black')
d = ImageDraw.Draw(sheet)
for i, f in enumerate(fs):
    x, y = (i % cols) * W, (i // cols) * (H + 30)
    sheet.paste(Image.open(f).resize((W, H)), (x, y + 30))
    d.text((x + 8, y + 8), os.path.basename(f)[2:-4] + ' s', fill='white')
sheet.save(out, quality=85)
