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
| `index.html` | Sitio principal. La sección **06 · Participación** muestra un QR por mesa y el acceso a resultados. |
| `votar.html?mesa=1` … `?mesa=4` | Papeleta de una mesa. Es la URL que abre cada código QR. Un voto por mesa y por dispositivo. |
| `resultados.html` | Resultados en vivo de las cuatro mesas (tema oscuro, botón de pantalla completa para proyectar). `?mesa=N` muestra una sola mesa en grande. |
| `qr.html` | Hoja imprimible con los cuatro QR de votación y el QR de resultados. |
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

El script extrae las imágenes embebidas a `assets/`, inserta la sección de votación por mesas y actualiza los metadatos.

## Estructura

```
index.html            sitio principal
votar.html            papeleta por mesa
resultados.html       resultados en vivo
qr.html               hoja de códigos QR
js/mesas.js           datos de las 4 mesas y 16 ponencias
js/firebase-config.js configuración de Firebase (pegar aquí)
js/votacion.js        capa de votación (Firebase o modo demostración)
css/votacion.css      estilos de votación y resultados
database.rules.json   reglas de seguridad de Realtime Database
qr/                   códigos QR (svg, png)
assets/               imágenes del sitio
tools/                scripts de construcción y generación de QR
```
