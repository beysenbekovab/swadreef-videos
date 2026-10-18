# Подготовка скриншотов: срезаем статус-бар iPad и шапку, закрашиваем индикатор в правом нижнем углу.
import glob, os
from PIL import Image
here = os.path.dirname(os.path.abspath(__file__))
TOP = 118
for src in sorted(glob.glob(os.path.join(here, 'screenshots/raw/*.png'))):
    im = Image.open(src).convert('RGB')
    w, h = im.size
    im = im.crop((0, TOP, w, h))
    if 'note' not in src:
        c = im.getpixel((w - 140, im.size[1] - 20))
        im.paste(c, (w - 110, im.size[1] - 110, w, im.size[1]))
    out = os.path.join(here, 'screenshots', os.path.basename(src).replace('.png', '.jpg'))
    im.save(out, quality=93)
    print(out, im.size)
