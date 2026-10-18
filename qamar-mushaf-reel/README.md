# Qamar — Reel «Мусхаф»

Готовое видео: `qamar-mushaf-reel.mp4` — 1080×1920, 24 с, 30 fps (беззвучная дорожка; музыку/чтение добавить в Instagram).

Сцены: хук → 5 функций на реальных скриншотах iPad → CTA.
1. Мусхаф с цветовым таджвидом
2. Нажатие на аят — транскрипция и перевод
3. Чтец с подсветкой аята
4. Ночная тема
5. Заметки и закладки

Файлы:
- `index.html` — сцена и анимация; тексты и подписи в `CONFIG`, наезды камеры в `CAM`.
- `screenshots/raw/` — исходные скриншоты; `python3 prep_screens.py` обрезает статус-бар → `screenshots/*.jpg`.
- Предпросмотр: открыть `index.html?play` в браузере.
- Контрольные кадры: `node render.mjs --stills` → `out/stills/`.
- Видео: `node render.mjs` → `out/qamar-mushaf-reel.mp4` (нужны Playwright + ffmpeg).
