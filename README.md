# Visión sin ojos

App para practicar la "visión extraocular" (*eyeless sight*) en solitario, con los ojos vendados, y comprobar con números si aciertas más de lo que daría el azar.

**Úsala online:** https://pgarralda-personal.github.io/Vision-sin-ojos/

## Qué hace
- **15 niveles** de lo simple a lo complejo: blanco o negro, colores (2 a 6), símbolos de las cartas Zener, Zener con colores, letras, letras con colores y palabras.
- **Avance por niveles:** el siguiente nivel se desbloquea al superar el actual con una sesión completa de 20 ensayos o más cuyo resultado tenga como mucho un 1 % de probabilidad de salir por suerte (exigencia configurable: 5 %, 1 % o 0,1 %). Se puede desactivar para elegir cualquier nivel.
- **Perfiles con nombre:** cada persona tiene sus propios niveles, historial y gráfico de evolución. Se guarda solo en el navegador (`localStorage`).
- **Idiomas:** español, inglés, alemán y portugués (Brasil). Sin idioma elegido, usa el del navegador (y si no es ninguno de estos, inglés). Se cambia arriba a la derecha.
- **Voces grabadas:** la app lee las opciones, dice si acertaste y resume el resultado con voces libres (Kokoro; Piper para alemán), las mismas que Ideogram Drills. Si falta algún audio, usa la voz del sistema.
- **Respuestas sin mirar:** teclado (1–6, o la letra en los niveles de letras), zonas de la pantalla táctil o voz (reconocimiento del navegador, en el idioma elegido).
- **Objetivos:** elegidos al azar con `crypto.getRandomValues`; opción de colores con la misma luminosidad; símbolos con la misma superficie; se guardan todos los ensayos, también los de sesiones a medias; sesiones de control sin objetivo.
- **Estadística:** probabilidad binomial de acertar tanto o más por suerte (p), por sesión, por nivel y acumulada; aciertos parciales (forma / color) en los niveles combinados; exportación a CSV.

## Archivos
| Archivo | Qué es |
|---|---|
| `index.html` | La app, sin dependencias. Contiene también todos los textos de cada idioma (bloque `<script id="i18n">`). Funciona sin conexión abriendo la carpeta completa, salvo el reconocimiento de voz, que puede necesitar internet. |
| `audio/<idioma>/` | Las frases grabadas (MP3): números, opciones, frases fijas y nombres de nivel. |
| `tools/make_audio.py` | Genera los audios a partir de los textos de `index.html`. |

## Cambiar un texto o añadir audios
```bash
brew install ffmpeg
python3.12 -m venv tools/.venv && tools/.venv/bin/pip install -r tools/requirements.txt
tools/.venv/bin/python tools/make_audio.py           # crea solo los audios que faltan (la primera vez descarga las voces, ~400 MB)
tools/.venv/bin/python tools/make_audio.py --force   # rehace todos, p. ej. tras cambiar un texto
```
Para añadir un idioma: copia un bloque de idioma en el `i18n` de `index.html`, tradúcelo, añade su voz en `VOICES` de `tools/make_audio.py` y genera los audios.

## Publicar cambios
GitHub Pages sirve la rama `main` desde la raíz. Cada `git push` a `main` actualiza la web en 1–2 minutos.

## Probar en local
```bash
python3 -m http.server 8791
```
y abrir http://localhost:8791
