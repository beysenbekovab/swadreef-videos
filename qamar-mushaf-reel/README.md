# Qamar — Reel «Мусхаф»

Вертикальный ролик 1080×1920 (24 с, 30 fps) для Instagram Qamar: хук → 5 функций мусхафа на iPad → CTA.

- `index.html` — сцена и анимация; всё редактируемое в `CONFIG` (тексты, список фич, длительность, скриншоты).
- `screenshots/` — реальные скриншоты из приложения; укажите путь в `CONFIG.screenshots.<mode>`, и он заменит макет в этой сцене.
- Предпросмотр: открыть `index.html?play` в браузере.
- Контрольные кадры: `node render.mjs --stills` → `out/stills/`.
- Видео: `node render.mjs` → `out/qamar-mushaf-reel.mp4` (нужны Playwright + ffmpeg).

Функции в ролике пока черновые — сверить с реальными возможностями Qamar.
