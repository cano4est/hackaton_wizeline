# Homero hace un ollie

Homero hace un ollie en skate sobre una escalera de 6 escalones con pasamanos, en Springfield.

![Homero ollie](homer-ollie.gif)

`homer-ollie.mp4` es la versión completa: 1080p a 60 fps y con sonido.

## Qué tiene

- **Rig del personaje**: `homer.png` se dibuja en tres piezas (zapatos, piernas y torso). Así Homero se agacha antes del pop, recoge las piernas en el aire y amortigua al caer.
- **Ollie con la física correcta**: la cola golpea el piso, la tabla gira sobre las ruedas traseras, el pie delantero la nivela y la cadera sigue una parábola.
- **Cámara**: sigue a Homero con parallax en 4 capas, hace zoom en el salto, pone **cámara lenta** en el punto más alto y se sacude al aterrizar.
- **Arte estilo Los Simpson**: contornos de tinta y colores planos. Al fondo, la planta nuclear echando vapor, casas, el letrero de "Prohibido patinar", una banca y un poste de luz.
- **Sonido**: ruedas rodando, las juntas de la banqueta, el "clack" del pop, el viento en el aire y el golpe del aterrizaje (`sfx.py`, sincronizado con la animación).
- **Título** al inicio y un "WOO-HOO!" al aterrizar.

## Archivos

| Archivo | Para qué |
| --- | --- |
| `index.html` | Animación en vivo, con controles de pausa, cámara lenta, sonido y reinicio |
| `homer.png` | Homero recortado a 2x, con contorno limpio |
| `fonts/Bangers.ttf` | Tipografía de cómic (SIL Open Font License) |
| `record.js` | Renderiza los cuadros con Playwright y los manda a ffmpeg |
| `sfx.py` | Genera los efectos de sonido a partir de la línea de tiempo |
| `build.sh` | Genera `homer-ollie.mp4`, `homer-ollie.gif` y `ollie-sfx.m4a` |

## Uso

```bash
python3 -m http.server   # luego abre http://localhost:8000/index.html
./build.sh               # vuelve a exportar el video, el GIF y el audio
```
