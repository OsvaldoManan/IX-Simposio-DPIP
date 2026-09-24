// Estado de la evaluación y votación por mesa (IX Simposio DPIP 2026).
//
// VOTACION_HABILITADA: interruptor general. Con false, todo queda cerrado.
// Con true, cada mesa se abre sola según el cronograma:
//   abre   = inicio de la mesa  - ABRE_MIN_ANTES
//   cierra = término de la mesa + CIERRA_MIN_DESPUES
// VOTACION_EXTRA_MIN alarga el cierre de una mesa, p. ej. { 1: 20 }.
// VOTACION_MANUAL permite forzar una mesa si el programa se atrasa o adelanta:
//   { 2: true }  -> Mesa 2 abierta ya, sin importar la hora
//   { 1: false } -> Mesa 1 cerrada
window.VOTACION_HABILITADA = true;

window.VOTACION_FECHA = "2026-09-24";
window.VOTACION_ZONA = "-03:00";
window.VOTACION_HORARIOS = {
  1: ["10:25", "11:45"],
  2: ["11:45", "13:05"],
  3: ["14:30", "15:50"],
  4: ["16:05", "17:25"]
};
window.ABRE_MIN_ANTES = 0;
window.CIERRA_MIN_DESPUES = 30;
window.VOTACION_MANUAL = { 1: false };  // Mesa 1 cerrada manualmente (24 sep, 12:08)
// Minutos extra de cierre por mesa (se suman a CIERRA_MIN_DESPUES).
window.VOTACION_EXTRA_MIN = { 1: 20 };

// Devuelve { estado: "abierta" | "proxima" | "cerrada", abre: Date, cierra: Date } para la mesa n.
window.estadoVotacionMesa = function (n, ahora) {
  var h = window.VOTACION_HORARIOS[n];
  if (!h) return { estado: "cerrada" };
  var t = (ahora || new Date()).getTime();
  var base = window.VOTACION_FECHA + "T";
  var abre = new Date(new Date(base + h[0] + ":00" + window.VOTACION_ZONA).getTime() - window.ABRE_MIN_ANTES * 60000);
  var extra = (window.VOTACION_EXTRA_MIN && window.VOTACION_EXTRA_MIN[n]) || 0;
  var cierra = new Date(new Date(base + h[1] + ":00" + window.VOTACION_ZONA).getTime() + (window.CIERRA_MIN_DESPUES + extra) * 60000);
  var r = { abre: abre, cierra: cierra };
  if (window.VOTACION_HABILITADA === false) { r.estado = "cerrada"; r.general = true; return r; }
  var m = window.VOTACION_MANUAL && window.VOTACION_MANUAL[n];
  if (m === true) { r.estado = "abierta"; return r; }
  if (m === false) { r.estado = "cerrada"; return r; }
  r.estado = t < abre.getTime() ? "proxima" : (t < cierra.getTime() ? "abierta" : "cerrada");
  return r;
};
window.horaVotacion = function (d) {
  return d.toLocaleTimeString("es-CL", { hour: "2-digit", minute: "2-digit", hourCycle: "h23", timeZone: "America/Santiago" });
};
