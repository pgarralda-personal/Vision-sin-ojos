# Visión sin ojos

App para practicar la "visión extraocular" (*eyeless sight*) en solitario, con los ojos vendados, y comprobar con números si aciertas más de lo que daría el azar.

**Úsala online:** https://pgarralda-personal.github.io/Vision-sin-ojos/

## Qué hace
- **15 niveles** de lo simple a lo complejo: blanco o negro, colores (2 a 6), símbolos de las cartas Zener, Zener con colores, letras, letras con colores y palabras.
- **Avance por niveles:** el siguiente nivel se desbloquea al superar el actual con una sesión completa de 20 ensayos o más cuyo resultado tenga como mucho un 1 % de probabilidad de salir por suerte (exigencia configurable: 5 %, 1 % o 0,1 %). Se puede desactivar para elegir cualquier nivel.
- **Perfiles con nombre:** cada persona tiene sus propios niveles, historial y gráfico de evolución. Se guarda solo en el navegador (`localStorage`).
- **Respuestas sin mirar:** teclado (1–6, o la letra en los niveles de letras), zonas de la pantalla táctil o voz (reconocimiento del navegador). La app habla en español: lee las opciones y dice si acertaste.
- **Prueba justa:** objetivos elegidos con `crypto.getRandomValues`; colores con el mismo brillo y símbolos con la misma superficie, para que la cantidad de luz no los delate; se guardan todos los ensayos, también los de sesiones a medias; sesiones de control sin objetivo.
- **Estadística:** probabilidad binomial de acertar tanto o más por suerte (p), por sesión, por nivel y acumulada; aciertos parciales (forma / color) en los niveles combinados; exportación a CSV.

## Archivos
| Archivo | Qué es |
|---|---|
| `index.html` | La app completa en un solo archivo, sin dependencias. Funciona sin conexión (doble clic), salvo el reconocimiento de voz, que puede necesitar internet. |

## Publicar cambios
GitHub Pages sirve la rama `main` desde la raíz. Cada `git push` a `main` actualiza la web en 1–2 minutos.

## Probar en local
```bash
python3 -m http.server 8791
```
y abrir http://localhost:8791
