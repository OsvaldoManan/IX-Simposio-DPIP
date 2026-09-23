/* Capa de votación del IX Simposio DPIP.
   Expone window.Votacion con:
   - mode: "firebase" | "demo"
   - ready(): Promise
   - hasVoted(mesaKey): Promise<string|null>   (código de la ponencia votada o null)
   - vote(mesaKey, codigo): Promise
   - subscribe(mesaKey, cb(votos, error)): () => void   (votos = { uid: {ponencia, t} })
   - count(mesa, votos): { porPonencia: {codigo: n}, total }
   - mesaActual(): mesa cuyo horario está en curso (o null)
   - evaluador() / loginEvaluador(email, pass) / logoutEvaluador(): cuenta de evaluador del baremo (3 cuentas autorizadas)
   - hasEvaluated / evaluate / subscribeEval: baremo (solo evaluadores autenticados)
*/
(function () {
  const MESAS = window.MESAS || [];
  const cfg = window.FIREBASE_CONFIG;
  const firebaseDisponible = !!(cfg && cfg.apiKey && cfg.databaseURL && window.firebase);

  const DEMO_UID_KEY = "ixdpip-uid";
  const demoKey = (m) => "ixdpip-demo-votos-" + m;

  function demoUid() {
    let u = null;
    try { u = localStorage.getItem(DEMO_UID_KEY); } catch (e) {}
    if (!u) {
      u = "d" + Math.random().toString(36).slice(2, 10) + Date.now().toString(36);
      try { localStorage.setItem(DEMO_UID_KEY, u); } catch (e) {}
    }
    return u;
  }
  function demoRead(m) {
    try { return JSON.parse(localStorage.getItem(demoKey(m)) || "{}"); } catch (e) { return {}; }
  }
  function demoReadKey(k) {
    try { return JSON.parse(localStorage.getItem(k) || "{}"); } catch (e) { return {}; }
  }

  const demo = {
    mode: "demo",
    async ready() {},
    async hasVoted(m) {
      const v = demoRead(m)[demoUid()];
      return v ? v.ponencia : null;
    },
    async vote(m, codigo) {
      const all = demoRead(m);
      const uid = demoUid();
      if (all[uid]) throw new Error("already-voted");
      all[uid] = { ponencia: codigo, t: Date.now() };
      localStorage.setItem(demoKey(m), JSON.stringify(all));
      try { new BroadcastChannel("ixdpip-votos").postMessage({ m: m }); } catch (e) {}
    },
    evaluador() {
      try { const e = localStorage.getItem("ixdpip-demo-evaluador"); return e ? { uid: "demo-" + e, email: e } : null; } catch (x) { return null; }
    },
    async loginEvaluador(email) {
      localStorage.setItem("ixdpip-demo-evaluador", email);
      return { uid: "demo-" + email, email: email };
    },
    async logoutEvaluador() { localStorage.removeItem("ixdpip-demo-evaluador"); },
    async hasEvaluated(m) {
      const v = demoReadKey("ixdpip-demo-eval-" + m)[demoUid()];
      return v || null;
    },
    async evaluate(m, payload) {
      const key = "ixdpip-demo-eval-" + m;
      const all = demoReadKey(key);
      const uid = demoUid();
      if (all[uid]) throw new Error("already-evaluated");
      all[uid] = Object.assign({}, payload, { t: Date.now() });
      localStorage.setItem(key, JSON.stringify(all));
      if (payload.mejor) { try { await this.vote(m, payload.mejor); } catch (e) {} }
      try { new BroadcastChannel("ixdpip-votos").postMessage({ m: m }); } catch (e) {}
    },
    subscribeEval(m, cb) {
      const key = "ixdpip-demo-eval-" + m;
      const emit = () => cb(demoReadKey(key), null);
      emit();
      let bc = null;
      try { bc = new BroadcastChannel("ixdpip-votos"); bc.addEventListener("message", emit); } catch (e) {}
      window.addEventListener("storage", emit);
      return () => { if (bc) bc.close(); window.removeEventListener("storage", emit); };
    },
    subscribe(m, cb) {
      const emit = () => cb(demoRead(m), null);
      emit();
      let bc = null;
      try {
        bc = new BroadcastChannel("ixdpip-votos");
        bc.addEventListener("message", (e) => { if (!e.data || e.data.m === m) emit(); });
      } catch (e) {}
      const onStorage = (e) => { if (!e.key || e.key === demoKey(m)) emit(); };
      window.addEventListener("storage", onStorage);
      return () => { if (bc) bc.close(); window.removeEventListener("storage", onStorage); };
    },
  };

  const fb = {
    mode: "firebase",
    _readyPromise: null,
    _db: null,
    _uid: null,
    ready() {
      if (this._readyPromise) return this._readyPromise;
      this._readyPromise = new Promise((resolve, reject) => {
        try {
          if (!firebase.apps.length) firebase.initializeApp(cfg);
          this._db = firebase.database();
          const auth = firebase.auth();
          let first = true;
          const off = auth.onAuthStateChanged((user) => {
            if (user) { this._uid = user.uid; this._user = user; off(); resolve(); return; }
            if (!first) return;
            first = false;
            auth.signInAnonymously().catch((err) => {
              if (err && err.code === "auth/operation-not-allowed") {
                reject(new Error("Activa el proveedor de acceso anónimo en Firebase Authentication."));
              } else reject(err);
            });
          }, (err) => reject(err));
        } catch (err) { reject(err); }
      });
      return this._readyPromise;
    },
    async hasVoted(m) {
      await this.ready();
      const snap = await this._db.ref("votos/" + m + "/" + this._uid).get();
      return snap.exists() ? snap.val().ponencia : null;
    },
    async vote(m, codigo) {
      await this.ready();
      await this._db.ref("votos/" + m + "/" + this._uid).set({
        ponencia: codigo,
        t: firebase.database.ServerValue.TIMESTAMP,
      });
    },
    evaluador() {
      const u = firebase.auth().currentUser;
      return u && !u.isAnonymous ? { uid: u.uid, email: u.email } : null;
    },
    async loginEvaluador(email, password) {
      const cred = await firebase.auth().signInWithEmailAndPassword(email, password);
      this._uid = cred.user.uid; this._user = cred.user;
      return { uid: cred.user.uid, email: cred.user.email };
    },
    async logoutEvaluador() {
      await firebase.auth().signOut();
      this._readyPromise = null; this._uid = null;
    },
    async hasEvaluated(m) {
      await this.ready();
      const snap = await this._db.ref("evaluaciones/" + m + "/" + this._uid).get();
      return snap.exists() ? snap.val() : null;
    },
    async evaluate(m, payload) {
      await this.ready();
      await this._db.ref("evaluaciones/" + m + "/" + this._uid).set(Object.assign({}, payload, {
        t: firebase.database.ServerValue.TIMESTAMP,
      }));
      if (payload.mejor) { try { await this.vote(m, payload.mejor); } catch (e) {} }
    },
    subscribeEval(m, cb) {
      let ref = null;
      let handler = null;
      let cancelled = false;
      this.ready().then(() => {
        if (cancelled) return;
        ref = this._db.ref("evaluaciones/" + m);
        handler = ref.on("value", (s) => cb(s.val() || {}, null), (err) => cb(null, err));
      }).catch((err) => cb(null, err));
      return () => { cancelled = true; if (ref && handler) ref.off("value", handler); };
    },
    subscribe(m, cb) {
      let ref = null;
      let handler = null;
      let cancelled = false;
      this.ready().then(() => {
        if (cancelled) return;
        ref = this._db.ref("votos/" + m);
        handler = ref.on("value", (s) => cb(s.val() || {}, null), (err) => cb(null, err));
      }).catch((err) => cb(null, err));
      return () => { cancelled = true; if (ref && handler) ref.off("value", handler); };
    },
  };

  const backend = firebaseDisponible ? fb : demo;

  backend.mesas = MESAS;
  backend.mesa = (n) => MESAS.find((m) => m.numero === Number(n)) || null;
  backend.count = (mesa, votos) => {
    const porPonencia = {};
    mesa.ponencias.forEach((p) => { porPonencia[p.codigo] = 0; });
    let total = 0;
    Object.values(votos || {}).forEach((v) => {
      if (v && Object.prototype.hasOwnProperty.call(porPonencia, v.ponencia)) {
        porPonencia[v.ponencia] += 1;
        total += 1;
      }
    });
    return { porPonencia: porPonencia, total: total };
  };
  backend.PREGUNTAS = [
    { key: "c", nombre: "Claridad", texto: "¿En qué medida pudo seguir y comprender la ponencia, aunque no domine el tema?" },
    { key: "r", nombre: "Relevancia", texto: "¿En qué medida le quedó clara la importancia de la investigación y el problema al que responde?" },
    { key: "f", nombre: "Fuerza de la presentación", texto: "¿Qué tan convincente y bien organizada le resultó la presentación?" },
  ];
  backend.ESCALA = ["Nada", "Muy poco", "Poco", "Moderadamente", "Bastante", "Totalmente"];
  // Resumen del baremo: promedios por pregunta y ponencia, votos a mejor ponencia y puntaje del público
  // (90 % promedio de las tres preguntas, 10 % proporcional a la mención como mejor ponencia).
  backend.resumenEval = (mesa, evals) => {
    const por = {};
    mesa.ponencias.forEach((p) => { por[p.codigo] = { n: 0, c: 0, r: 0, f: 0, mejor: 0 }; });
    let respuestas = 0; let menciones = 0;
    Object.values(evals || {}).forEach((e) => {
      if (!e || !e.p) return;
      respuestas += 1;
      Object.entries(e.p).forEach(([codigo, v]) => {
        const acc = por[codigo]; if (!acc || !v) return;
        acc.n += 1; acc.c += Number(v.c) || 0; acc.r += Number(v.r) || 0; acc.f += Number(v.f) || 0;
      });
      if (e.mejor && por[e.mejor]) { por[e.mejor].mejor += 1; menciones += 1; }
    });
    Object.values(por).forEach((acc) => {
      acc.pc = acc.n ? acc.c / acc.n : 0; acc.pr = acc.n ? acc.r / acc.n : 0; acc.pf = acc.n ? acc.f / acc.n : 0;
      acc.media = (acc.pc + acc.pr + acc.pf) / 3;
      acc.share = menciones ? acc.mejor / menciones : 0;
      acc.puntaje = 0.9 * (acc.media / 5) * 100 + 0.1 * acc.share * 100;
    });
    return { por: por, respuestas: respuestas, menciones: menciones };
  };
  backend.mesaActual = () => {
    const now = Date.now();
    for (const m of MESAS) {
      const ini = new Date("2026-09-24T" + m.inicio + ":00-03:00").getTime();
      const fin = new Date("2026-09-24T" + m.fin + ":00-03:00").getTime();
      if (now >= ini && now < fin) return m;
    }
    return null;
  };
  backend.escapeHtml = (value) => String(value).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" }[c]));

  window.Votacion = backend;
})();
