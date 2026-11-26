"""Interfaz Streamlit: tablero de lecturas, chatbot con audio y aprobación humana."""
import altair as alt
import pandas as pd
import streamlit as st

from app import acciones, config, db, ia

st.set_page_config(page_title="Biblioteca · SALA-02", page_icon=":material/lightbulb:", layout="wide")

SAVANA_SVG = (
    "data:image/svg+xml;utf8,"
    "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 600 160' preserveAspectRatio='xMaxYMax slice'>"
    "<path d='M0 160 L0 120 Q120 90 240 118 T480 110 T600 100 L600 160Z' fill='%234a2c3d' fill-opacity='.45'/>"
    "<path d='M0 160 L0 138 Q150 118 300 140 T600 128 L600 160Z' fill='%232d1b2e' fill-opacity='.55'/>"
    "<g fill='%232d1b2e' fill-opacity='.8'><rect x='428' y='92' width='5' height='40'/>"
    "<ellipse cx='430' cy='88' rx='44' ry='10'/><ellipse cx='404' cy='94' rx='22' ry='6'/>"
    "<ellipse cx='458' cy='93' rx='20' ry='5'/></g>"
    "<g fill='%232d1b2e' fill-opacity='.7'><rect x='528' y='108' width='3' height='26'/>"
    "<ellipse cx='530' cy='105' rx='26' ry='6'/></g></svg>"
)

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, .stApp { font-family: 'Inter', system-ui, sans-serif; }
.stApp {
  background: linear-gradient(180deg, #FFF6E5 0%, #FCE5C4 32%, #F6CBA0 62%, #EDAF93 84%, #D9979B 100%);
  background-attachment: fixed;
}
[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 1.6rem; max-width: 1200px; }
.hero {
  position: relative; overflow: hidden; border-radius: 18px; padding: 1.7rem 2rem 2.4rem 2rem; margin-bottom: 1.2rem;
  background: linear-gradient(120deg, #F7B267 0%, #EE8A62 45%, #C4607A 80%, #7A4E7E 100%);
  box-shadow: 0 10px 30px rgba(122, 78, 126, .22); color: #fff;
}
.hero::after { content: ""; position: absolute; inset: 0; background-image: url("%SVG%"); background-repeat: no-repeat; background-position: right bottom; background-size: cover; pointer-events: none; }
.hero h1 { margin: 0; font-size: 1.9rem; font-weight: 700; letter-spacing: -.01em; color: #fff; padding: 0; }
.hero p { margin: .3rem 0 0 0; font-size: .95rem; color: rgba(255,255,255,.92); max-width: 70%; position: relative; z-index: 1; }
.hero h1 { position: relative; z-index: 1; }
.pill { display: inline-block; margin-top: .8rem; padding: .22rem .75rem; border-radius: 999px; background: rgba(255,255,255,.22); border: 1px solid rgba(255,255,255,.45); font-size: .78rem; font-weight: 500; position: relative; z-index: 1; }
[data-testid="stMetric"] { background: rgba(255,255,255,.62); backdrop-filter: blur(6px); border: 1px solid rgba(180,83,42,.16); border-left: 5px solid #E07A5F; border-radius: 14px; padding: .9rem 1.1rem; box-shadow: 0 4px 14px rgba(120,70,50,.08); }
[data-testid="stMetricLabel"] { color: #7a5a48; }
[data-testid="stMetricValue"] { color: #3B2A20; font-weight: 700; }
.stTabs [data-baseweb="tab-list"] { gap: .4rem; border-bottom: 1px solid rgba(180,83,42,.25); }
.stTabs [data-baseweb="tab"] { padding: .55rem 1rem; border-radius: 10px 10px 0 0; font-weight: 500; color: #7a5a48; }
.stTabs [aria-selected="true"] { color: #B4532A; background: rgba(255,255,255,.55); }
[data-testid="stDataFrame"], [data-testid="stJson"], [data-testid="stAlert"] { border-radius: 12px; }
div.stButton > button { background: linear-gradient(120deg, #E8894F, #C4607A); color: #fff; border: 0; border-radius: 10px; padding: .55rem 1.2rem; font-weight: 600; box-shadow: 0 4px 12px rgba(196,96,122,.3); }
div.stButton > button:hover { filter: brightness(1.06); color: #fff; }
h2, h3 { color: #4a2c3d; font-weight: 600; }
.card { background: rgba(255,255,255,.6); border: 1px solid rgba(180,83,42,.14); border-radius: 14px; padding: 1rem 1.2rem; }
</style>
""".replace("%SVG%", SAVANA_SVG),
    unsafe_allow_html=True,
)

st.markdown(
    f"""<div class="hero"><h1>Iluminación de la biblioteca · SALA-02</h1>
<p>Monitoreo de lecturas y solicitudes de inspección para Mantenimiento de sede.</p>
<span class="pill">Alerta si lux &lt; {config.UMBRAL_LUX:.0f} entre 08:00 y 20:00 · {config.TZ.key} · IA: {config.IA_MODO}</span></div>""",
    unsafe_allow_html=True,
)

tab1, tab2, tab3 = st.tabs([":material/monitoring: Tablero", ":material/smart_toy: Chatbot", ":material/task_alt: Aprobación"])

COLOR_ESTADO = {"ALERTA": "background-color:#F4B6A0;color:#7A2E17;font-weight:600",
                "REVISION": "background-color:#FBE3A6;color:#6B4E00;font-weight:600",
                "HISTORIAL": "background-color:#DCE7C6;color:#3F5A22"}


def pintar(v):
    return COLOR_ESTADO.get(v, "")


with tab1:
    lecs = db.listar("lecturas")
    if lecs:
        df = pd.DataFrame(lecs)
        df["lectura"] = df["id"].map(lambda n: db.fmt_id("LEC", n))
        df["hora"] = pd.to_datetime(df["ts"]).dt.tz_localize(None)
        c1, c2, c3 = st.columns(3)
        c1.metric("Lecturas recibidas", len(df))
        c2.metric("Alertas", int((df.estado == "ALERTA").sum()))
        c3.metric("Solo historial", int((df.estado == "HISTORIAL").sum()))
        estados = sorted(df.estado.unique())
        filtro = st.multiselect("Filtrar por estado", estados, default=estados)
        vista = df[df.estado.isin(filtro)][["lectura", "sala_id", "ts", "lux", "estado", "motivo"]]
        st.dataframe(vista.style.map(pintar, subset=["estado"]).format({"lux": "{:g}"}), use_container_width=True, hide_index=True)
        st.subheader("Iluminación a lo largo del día")
        linea = alt.Chart(df).mark_line(color="#C4607A", strokeWidth=3, interpolate="monotone").encode(
            x=alt.X("hora:T", title="Hora local", axis=alt.Axis(format="%H:%M")), y=alt.Y("lux:Q", title="Lux", scale=alt.Scale(zero=True)))
        puntos = alt.Chart(df).mark_circle(size=130, opacity=1).encode(
            x="hora:T", y="lux:Q",
            color=alt.Color("estado:N", legend=alt.Legend(title="Estado"),
                            scale=alt.Scale(domain=["ALERTA", "HISTORIAL", "REVISION"], range=["#D1495B", "#7C9A5E", "#E9A23B"])),
            tooltip=["lectura", "lux", "estado", "motivo"])
        umbral = alt.Chart(pd.DataFrame({"y": [config.UMBRAL_LUX]})).mark_rule(color="#7A2E17", strokeDash=[6, 4]).encode(y="y:Q")
        st.altair_chart((linea + puntos + umbral).properties(height=300), use_container_width=True)
        st.caption(f"Línea discontinua: umbral de {config.UMBRAL_LUX:.0f} lux.")
    else:
        st.info("Aún no hay lecturas. Ejecuta el simulador: python simulador/publicar_lecturas.py", icon=":material/info:")
    st.subheader("Incidentes y excepciones")
    inc = db.listar("incidentes")
    if inc:
        d = pd.DataFrame(inc)
        d.insert(0, "incidente", d["id"].map(lambda n: db.fmt_id("INC", n)))
        st.dataframe(d.drop(columns=["id", "payload_ia"]), use_container_width=True, hide_index=True)
    else:
        st.caption("Sin incidentes abiertos.")
    exc = db.listar("excepciones")
    if exc:
        st.warning("Excepciones registradas: derivadas a revisión", icon=":material/warning:")
        st.dataframe(pd.DataFrame(exc), use_container_width=True, hide_index=True)

pend = [i for i in db.listar("incidentes") if i["estado"] == "PENDIENTE_APROBACION"]

with tab2:
    if not pend:
        st.info("No hay incidentes pendientes.", icon=":material/info:")
    else:
        opciones = {db.fmt_id("INC", i["id"]): i for i in pend}
        sel = st.selectbox("Incidente", list(opciones))
        inc = opciones[sel]
        lec = next(l for l in db.listar("lecturas") if l["id"] == inc["lectura_id"])
        hora = lec["ts"][11:16]
        lectura = {"sala_id": inc["sala_id"], "lux": lec["lux"], "hora": hora}
        st.write("Lectura que originó el incidente")
        st.json(lectura)
        audio = st.audio_input("Nota de voz del auxiliar (opcional)")
        nota = st.text_area("Nota (se completa con la transcripción)", key=f"nota_{sel}")
        if audio is not None and st.button("Transcribir audio", icon=":material/mic:"):
            st.session_state[f"nota_{sel}"] = ia.transcribir_audio(audio.getvalue(), "audio/wav")
            st.rerun()
        variante = st.radio("Variante de prompt", ["few_shot", "zero_shot"], horizontal=True)
        if st.button("Preparar JSON con la IA", icon=":material/auto_awesome:") and nota.strip():
            st.session_state[f"res_{sel}"] = ia.cadena(nota, lectura, variante)
        res = st.session_state.get(f"res_{sel}")
        if res:
            st.write("JSON propuesto")
            st.json(res["json"])
            st.write(f"Clasificación: **{res['clasificacion']}** · Acción sugerida: {res['accion_sugerida']}")
            if res["validacion"]["valido"]:
                st.success("Validación correcta: esquema válido y sala/lux coinciden con la lectura.", icon=":material/check_circle:")
            else:
                st.error(f"Validación fallida: {res['validacion']['errores']}", icon=":material/error:")

with tab3:
    if not pend:
        st.info("No hay incidentes pendientes de aprobación.", icon=":material/info:")
    else:
        sel = st.selectbox("Incidente a aprobar", [db.fmt_id("INC", i["id"]) for i in pend], key="ap")
        res = st.session_state.get(f"res_{sel}")
        payload = res["json"] if res and res["validacion"]["valido"] else None
        st.write("Payload que se registrará")
        st.json(payload or {"nota": "sin JSON validado; se usará la ficha del catálogo"})
        quien = st.text_input("Aprobador (nombre)")
        ok = st.checkbox("Apruebo registrar la solicitud de inspección")
        if st.button("Registrar solicitud", icon=":material/send:"):
            try:
                reg = acciones.registrar_solicitud(sel, quien, ok, payload)
                st.success(f"Solicitud {reg['solicitud_id']} registrada para {reg['destino']}", icon=":material/check_circle:")
            except acciones.AprobacionRequerida as e:
                st.error(str(e), icon=":material/error:")
    st.subheader("Solicitudes registradas")
    sols = db.listar("solicitudes")
    if sols:
        s = pd.DataFrame(sols)
        s.insert(0, "solicitud", s["id"].map(lambda n: db.fmt_id("SOL", n)))
        st.dataframe(s.drop(columns=["id"]), use_container_width=True, hide_index=True)
    else:
        st.caption("Aún no hay solicitudes registradas.")
