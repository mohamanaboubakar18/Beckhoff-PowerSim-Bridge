import streamlit as st
import pandas as pd
from ads_bridge import BeckhoffADSBridge
from converter_model import PowerConverterSimulator

st.set_page_config(page_title="Mohaman - Beckhoff Sim Interface", layout="wide")

# Initialisation de la session
if "bridge" not in st.session_state:
    st.session_state.bridge = BeckhoffADSBridge("io_mapping.json", use_mock=False)
    st.session_state.bridge.connect()
    st.session_state.sim = PowerConverterSimulator(dt=0.2)
    st.session_state.history = []

bridge: BeckhoffADSBridge = st.session_state.bridge
sim: PowerConverterSimulator = st.session_state.sim

st.title("⚡ Gestionnaire d'Interface de Simulation Beckhoff (ADS) & IHM")
st.markdown("**Entité Power Conversion** — Banc de simulation HIL (Convertisseur AC/DC/AC & Automate TwinCAT)")

# Barre latérale : Commandes Automate & Injection de défauts
with st.sidebar:
    st.header("🎛️ Commandes Automate (PLC)")
    b_start = st.toggle("Ordre de marche (MAIN.bStartCmd)", value=bridge.read_var("MAIN.bStartCmd"))
    sp_speed = st.slider("Consigne Vitesse (RPM)", 0.0, 3000.0, float(bridge.read_var("MAIN.fSpeedSetpoint_RPM")), 50.0)
    b_reset = st.toggle("Acquitter Défauts (MAIN.bResetFault)")

    bridge.write_var("MAIN.bStartCmd", b_start)
    bridge.write_var("MAIN.fSpeedSetpoint_RPM", sp_speed)
    bridge.write_var("MAIN.bResetFault", b_reset)

    st.divider()
    st.header("⚠️ Injection de Défauts (Tests HIL)")
    sim.fault_injections["dc_overvoltage"] = st.checkbox("Surtension Bus DC (> 800 V)")
    sim.fault_injections["cooling_loss"] = st.checkbox("Perte refroidissement IGBT (Ventilation HS)")
    sim.fault_injections["breaker_trip"] = st.checkbox("Ouverture disjoncteur HTA amont")

# Exécution d'un cycle de simulation
if st.button("▶️ Exécuter 10 cycles de simulation (2s)", type="primary"):
    for _ in range(10):
        inputs = {
            "MAIN.bStartCmd": bridge.read_var("MAIN.bStartCmd"),
            "MAIN.bResetFault": bridge.read_var("MAIN.bResetFault"),
            "MAIN.fSpeedSetpoint_RPM": bridge.read_var("MAIN.fSpeedSetpoint_RPM")
        }
        current_outputs = {k: bridge.read_var(k) for k in bridge.config["variables"]["outputs_to_plc"]}
        new_outputs = sim.step(inputs, current_outputs)

        for k, v in new_outputs.items():
            bridge.write_var(k, v)

        st.session_state.history.append(new_outputs)
        bridge.write_var("MAIN.bResetFault", False)

# Affichage des KPIs Temps Réel
states = bridge.get_all_states()
col1, col2, col3, col4 = st.columns(4)
col1.metric("Vitesse Rotor", f"{states['MAIN.fActualSpeed_RPM']} RPM", f"Consigne: {states['MAIN.fSpeedSetpoint_RPM']}")
col2.metric("Tension Bus DC", f"{states['MAIN.fDcBusVoltage_V']} V")
col3.metric("Courant Stator", f"{states['MAIN.fStatorCurrent_A']} A")
col4.metric("Température IGBT", f"{states['MAIN.fIgbtTemp_C']} °C", delta_color="inverse")

if states["MAIN.bFaultTripped"]:
    st.error("🚨 DÉFAUT ACTIF (MAIN.bFaultTripped = TRUE) — Mise en sécurité du convertisseur. Acquittement requis.")
elif states["MAIN.bReadyToRun"]:
    st.success("✅ Convertisseur Prêt (MAIN.bReadyToRun = TRUE)")

# Graphiques et Table d'échange ADS
col_graph, col_table = st.columns([3, 2])

with col_graph:
    st.subheader("📈 Courbes transitoires du convertisseur")
    if st.session_state.history:
        df_hist = pd.DataFrame(st.session_state.history)
        st.line_chart(df_hist[["MAIN.fActualSpeed_RPM", "MAIN.fStatorCurrent_A", "MAIN.fIgbtTemp_C"]])
    else:
        st.info("Cliquez sur 'Exécuter 10 cycles de simulation' pour générer les courbes.")

with col_table:
    st.subheader("🔗 Table d'échange Beckhoff ADS")
    table_data = [{"Variable TwinCAT": k, "Valeur": str(v)} for k, v in states.items()]
    st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)