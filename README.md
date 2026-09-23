# IX Simposio DPIP 2026 · Anatomía del presente

Sitio público del IX Simposio del Doctorado en Procesos e Instituciones Políticas (Escuela de Gobierno, Universidad Adolfo Ibáñez), con **votación por mesa** y **resultados en vivo**.

Publicado en GitHub Pages: <https://osvaldomanan.github.io/IX-Simposio-DPIP/>

## Activar GitHub Pages (una sola vez, desde la cuenta dueña del repositorio)

1. Abre <https://github.com/OsvaldoManan/IX-Simposio-DPIP/settings/pages>.
2. En **Build and deployment → Source** elige **Deploy from a branch**.
3. En **Branch** selecciona `main` y la carpeta `/ (root)`, y pulsa **Save**.
4. En uno o dos minutos el sitio queda disponible en la URL de arriba. Cada `git push` a `main` vuelve a publicarlo automáticamente.

Los códigos QR ya apuntan a esa URL, así que no hay que regenerarlos.

## Páginas

| Página | Uso |
| --- | --- |
| `index.html` | Sitio principal. La sección **06 · Participación** muestra un QR por mesa para el formulario de evaluación (baremo más voto a mejor ponencia). |
| `votar.html` | Redirige a `evaluar.html` (la votación forma parte del baremo). |
| `resultados.html` | Conteo público en vivo de la mejor ponencia de las cuatro mesas (tema oscuro, botón de pantalla completa para proyectar). `?mesa=N` muestra una sola mesa en grande. |
| `evaluar.html?mesa=1` … `?mesa=4` | Formulario de una mesa, abierto a los asistentes: cuatro páginas (una por ponencia) con tres preguntas de 0 a 5 y, al final, el voto por la mejor ponencia, que se registra también en `votos`. Una participación por mesa y dispositivo. Es la URL que abre cada QR. |
| `evaluacion-resultados.html` | Resultados del baremo (solo evaluadores con sesión): promedios por pregunta, menciones y puntaje (90 % promedio, 10 % mejor ponencia). Botón para descargar CSV. |
| `qr.html` | Hoja imprimible con el QR de cada mesa y el QR de resultados. |
| `qr/` | Los mismos códigos en SVG y PNG de alta resolución, más `URLS.txt`. |

## Activar la votación en vivo (Firebase, una sola vez)

Mientras `js/firebase-config.js` tenga `window.FIREBASE_CONFIG = null`, el sitio funciona en **modo demostración**: los votos se guardan solo en el dispositivo que vota y las páginas lo indican con un aviso amarillo. Para que todos los asistentes voten y los resultados se actualicen en tiempo real:

1. Entra a <https://console.firebase.google.com> con la cuenta de Google del simposio y crea un proyecto (por ejemplo `ix-simposio-dpip`). No hace falta Google Analytics.
2. En **Compilación → Authentication → Método de acceso**, habilita el proveedor **Anónimo**.
3. En **Compilación → Realtime Database**, crea la base de datos (ubicación `us-central1` o la que prefieras) en modo bloqueado. Luego abre la pestaña **Reglas**, pega el contenido de `database.rules.json` y publica.
4. En **Configuración del proyecto → Tus apps → Añadir app → Web**, registra la app (sin Hosting) y copia el objeto `firebaseConfig`.
5. Pega ese objeto en `js/firebase-config.js` reemplazando el `null`, por ejemplo:

   ```js
   window.FIREBASE_CONFIG = {
     apiKey: "AIza...",
     authDomain: "ix-simposio-dpip.firebaseapp.com",
     databaseURL: "https://ix-simposio-dpip-default-rtdb.firebaseio.com",
     projectId: "ix-simposio-dpip",
     storageBucket: "ix-simposio-dpip.appspot.com",
     messagingSenderId: "123456789",
     appId: "1:123456789:web:abcdef"
   };
   ```

6. Guarda, haz commit y push. En uno o dos minutos GitHub Pages publica el cambio y el aviso de modo demostración desaparece.

Las reglas de `database.rules.json` permiten leer los conteos a cualquiera y escribir **una sola vez por usuario anónimo y por mesa**, así que un mismo teléfono no puede votar dos veces en la misma mesa ni modificar su voto. El plan gratuito de Firebase (Spark) cubre con holgura un evento de este tamaño.

## Cuentas de evaluador (baremo)

Los **resultados** del baremo (`evaluacion-resultados.html`) solo son accesibles con una de las tres cuentas creadas en **Firebase Authentication** (proveedor correo/contraseña): `evaluador1@ix-simposio-dpip.cl`, `evaluador2@…` y `evaluador3@…`. Las contraseñas se entregan por separado; para cambiarlas o restablecerlas, usa la consola de Firebase (Authentication → Usuarios → menú de la cuenta). Las reglas de `database.rules.json` permiten a cualquier asistente escribir una evaluación por mesa y dispositivo, pero solo esos tres correos pueden leer `evaluaciones`. El formulario, como la votación, se abre con `VOTACION_HABILITADA`.

## Abrir o cerrar la votación

El estado lo controla una sola línea en `js/config-votacion.js`:

```js
window.VOTACION_HABILITADA = false; // cambiar a true el día del simposio
```

Con `false`, las secciones de votación y de evaluación de ponencias y el botón "Votar ponencia" aparecen desactivados, y `votar.html` y `evaluar.html` muestran un aviso en lugar del formulario (para probarla igual, agrega `&preview=1` a la URL). Con `true`, todo queda operativo. Haz commit y push tras el cambio; Pages lo publica en uno o dos minutos.

## Abstracts de las ponencias

Los PDF originales van en la carpeta `Abstract/` (no versionada) con el nombre `<posición en la mesa>. <Autor>.pdf`. Para incorporarlos o actualizarlos:

```bash
pip install pypdf
python tools/importar_abstracts.py
python tools/build_index.py
```

El primer script copia los PDF a `abstracts/` con nombres limpios, une los 16 en `abstracts/IX-Simposio-DPIP-2026-abstracts.pdf` y extrae resumen, palabras clave y reseña de cada ponente a `abstracts/abstracts.json`. El segundo los inserta en la sección de ponencias (resumen plegable, palabras clave, "Sobre quien expone" y botón de descarga).

## Regenerar los códigos QR

Los QR apuntan a la URL de GitHub Pages. Si el sitio se publica en otro dominio:

```bash
pip install segno
python tools/generar_qr.py https://nuevo-dominio.cl/
```

## Reconstruir `index.html`

`index.html` se genera desde el HTML exportado del sitio (`IX-Simposio-Anatomia-del-Presente.html`, no versionado). Si se exporta una versión nueva del sitio, cópiala con ese nombre en la raíz y ejecuta:

```bash
pip install pillow
python tools/build_index.py
```

El script extrae las imágenes embebidas a `assets/`, inserta la sección de votación por mesas, actualiza los metadatos y aplica `tools/ajustes_editoriales.py` (cronograma vigente, secciones eliminadas, distinción de invitados, cargos). Los cambios de contenido posteriores deben hacerse en ese script para que sobrevivan a una reconstrucción.

## Estructura

```
index.html            sitio principal
votar.html            papeleta por mesa
resultados.html       resultados en vivo
qr.html               hoja de códigos QR
js/mesas.js           datos de las 4 mesas y 16 ponencias
js/config-votacion.js abrir/cerrar la votación
js/firebase-config.js configuración de Firebase
js/votacion.js        capa de votación (Firebase o modo demostración)
css/votacion.css      estilos de votación y resultados
database.rules.json   reglas de seguridad de Realtime Database
qr/                   códigos QR de votación y baremo (svg, png)
evaluar.html          baremo del público por mesa
evaluacion-resultados.html resultados del baremo
assets/               imágenes del sitio
abstracts/            PDF de abstracts, compilado y abstracts.json
tools/                scripts de construcción y generación de QR
```
