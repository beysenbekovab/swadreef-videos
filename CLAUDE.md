# Рилсы Qamar — пайплайн

Полная документация: `docs/smooth-motion-reel-ipad.pdf` («Как сделать smooth-motion рилс с iPad»). Ниже — выжимка правил.

## Устройство
Один рилс — одна папка `reels/<имя>/`. Headless Chrome рисует `src/web/index.html` кадр за кадром через `window.render(t)`,
ffmpeg склеивает кадры со звуком: 1080×1920, 30 fps, H.264 (bt709) + AAC, −14 LUFS. Все времена — из `src/web/timeline.json`.

```
reels/<имя>/
  README.md  caption.txt  <имя>.mp4  cover.jpg
  src/
    raw/                исходные скриншоты приложения
    tools/              prep_shots.py (обрезка), sheet.py (контакт-лист)
    sfx.py              синтез звуков по меткам → mix.wav
    render.mjs          render(t) → JPEG (CDP) → ffmpeg
    web/ index.html timeline.json fonts/ shots/
```

Команды (из `src/`): `python3 tools/prep_shots.py` → `python3 sfx.py` → `node render.mjs --stills 3,9.5,15` →
`python3 tools/sheet.py stills sheet.jpg` → `node render.mjs ../<имя>.mp4 30` → `ffmpeg -ss <t> -i ../<имя>.mp4 -frames:v 1 ../cover.jpg`.

## Секрет плавности
- Никаких CSS-анимаций, transition, setTimeout, requestAnimationFrame — всё считается из `t`.
- Меняем только opacity и transform через хелпер `S(el, o, x, y, s)`.
- Каждое движение по easing: `eo` — появление, `eio` — перелёты, `eback` — пружинистый акцент.
- Появление — прозрачность + подъём на 12–24 px за 0,4–0,5 с; исчезновение 0,3 с; сцены перекрываются (`win`).
- Стаггер 10–70 мс на элемент. Один объект перетекает в следующий кадр (линза из экрана), а не исчезает.
- Фон живой, но тихий; частицы — только сидовый PRNG (mulberry32).
- Главный кадр держится не меньше 1–1,5 с.
- Шрифты и картинки грузятся до первого кадра (`window.READY = true` после `fonts.load` и `img.decode`).
- Одна тема, два смысловых цвета из токенов приложения.

## Подводные камни
- Безопасная зона Instagram: важный текст в полосе ~200–1500 px, подальше от правого края.
- Не обещать того, чего нет в приложении. В финале: «iPhone — qamar.web.app, Android — Google Play», значка App Store нет.
- У каждого скриншота своя верхняя панель — обрезать у всех.
- Перевод аята — дословно из приложения, переводчик назван.
- Финальный mp4 коммитится один раз и меньше 100 МиБ; черновики в `.gitignore`.

## Окружение
Сеть Custom: `api.elevenlabs.io`, `qamar.web.app` (+ default package managers). Переменная `ELEVENLABS_API_KEY` для озвучки.
