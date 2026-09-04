/* Capa de votación del IX Simposio DPIP.
   Expone window.Votacion con:
   - mode: "firebase" | "demo"
   - ready(): Promise
   - hasVoted(mesaKey): Promise<string|null>   (código de la ponencia votada o null)
   - vote(mesaKey, codigo): Promise
   - subscribe(mesaKey, cb(votos, error)): () => void   (votos = { uid: {ponencia, t} })
   - count(mesa, votos): { porPonencia: {codigo: n}, total }
   - mesaActual(): mesa cuyo horario está en curso (o null)
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
          const off = auth.onAuthStateChanged((user) => {
            if (user) { this._uid = user.uid; off(); resolve(); }
          }, (err) => reject(err));
          auth.signInAnonymously().catch((err) => {
            if (err && err.code === "auth/operation-not-allowed") {
              reject(new Error("Activa el proveedor de acceso anónimo en Firebase Authentication."));
            } else reject(err);
          });
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
