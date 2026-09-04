// Configuración de Firebase para la votación en vivo.
// 1) Crea un proyecto en https://console.firebase.google.com
// 2) Activa Realtime Database y Authentication > Anonymous
// 3) Pega aquí el objeto firebaseConfig de tu app web (Configuración del proyecto > Tus apps).
// Mientras este valor sea null, el sitio funciona en MODO DEMOSTRACIÓN (los votos quedan solo en el dispositivo).
window.FIREBASE_CONFIG = null;

// Ejemplo:
// window.FIREBASE_CONFIG = {
//   apiKey: "AIza...",
//   authDomain: "ix-simposio-dpip.firebaseapp.com",
//   databaseURL: "https://ix-simposio-dpip-default-rtdb.firebaseio.com",
//   projectId: "ix-simposio-dpip",
//   storageBucket: "ix-simposio-dpip.appspot.com",
//   messagingSenderId: "123456789",
//   appId: "1:123456789:web:abcdef"
// };
