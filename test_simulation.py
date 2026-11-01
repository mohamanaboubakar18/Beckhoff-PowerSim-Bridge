import pytest
from ads_bridge import BeckhoffADSBridge
from converter_model import PowerConverterSimulator


def test_ads_bridge_forcing():
    """Vérifie que le forçage d'interface prend le dessus sur l'écriture automate."""
    bridge = BeckhoffADSBridge("io_mapping.json", use_mock=True)
    bridge.connect()
    bridge.force_var("MAIN.fDcBusVoltage_V", 750.0)
    bridge.write_var("MAIN.fDcBusVoltage_V", 690.0)
    assert bridge.read_var("MAIN.fDcBusVoltage_V") == 750.0

    bridge.release_var("MAIN.fDcBusVoltage_V")
    bridge.write_var("MAIN.fDcBusVoltage_V", 690.0)
    assert bridge.read_var("MAIN.fDcBusVoltage_V") == 690.0


def test_converter_overvoltage_protection():
    """Vérifie le déclenchement instantané (Trip) en cas de surtension Bus DC."""
    sim = PowerConverterSimulator(dt=0.1)
    sim.fault_injections["dc_overvoltage"] = True

    inputs = {"MAIN.bStartCmd": True, "MAIN.bResetFault": False, "MAIN.fSpeedSetpoint_RPM": 1500.0}
    outputs = {
        "MAIN.fActualSpeed_RPM": 1500.0,
        "MAIN.fDcBusVoltage_V": 690.0,
        "MAIN.fStatorCurrent_A": 180.0,
        "MAIN.fIgbtTemp_C": 45.0,
        "MAIN.bReadyToRun": True,
        "MAIN.bFaultTripped": False
    }

    res = sim.step(inputs, outputs)
    assert res["MAIN.bFaultTripped"] is True
    assert res["MAIN.bReadyToRun"] is False