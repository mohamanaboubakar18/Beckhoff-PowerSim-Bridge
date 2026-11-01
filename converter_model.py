from typing import Dict, Any


class PowerConverterSimulator:
    """
    Modèle dynamique simplifié d'un convertisseur d'énergie (AC/DC/AC)
    avec gestion des protections thermiques et électriques.
    """

    def __init__(self, dt: float = 0.1):
        self.dt = dt  # Pas d'échantillonnage de la simulation (s)
        self.ambient_temp = 25.0
        self.nominal_dc_voltage = 690.0
        self.max_temp_threshold = 95.0       # Seuil déclenchement thermique IGBT (°C)
        self.overvoltage_threshold = 800.0   # Seuil surtension Bus DC (V)

        # Flags d'injection de défauts (Tests HIL)
        self.fault_injections = {
            "dc_overvoltage": False,
            "cooling_loss": False,
            "breaker_trip": False
        }

    def step(self, plc_inputs: Dict[str, Any], current_outputs: Dict[str, Any]) -> Dict[str, Any]:
        """Exécute un pas de calcul physique de la simulation."""
        b_start = plc_inputs["MAIN.bStartCmd"]
        b_reset = plc_inputs["MAIN.bResetFault"]
        sp_speed = plc_inputs["MAIN.fSpeedSetpoint_RPM"]

        actual_speed = current_outputs["MAIN.fActualSpeed_RPM"]
        igbt_temp = current_outputs["MAIN.fIgbtTemp_C"]
        fault_tripped = current_outputs["MAIN.bFaultTripped"]

        # 1. Gestion de l'acquittement défaut (Reset)
        if b_reset:
            fault_tripped = False

        # 2. (Déplacé à l'étape 8 pour évaluer la disponibilité après la vérification des défauts)
        ready_to_run_temp = not self.fault_injections["breaker_trip"] and not fault_tripped

        # 3. Dynamique de vitesse (1er ordre avec constante de temps mécanique tau = 1.2s)
        target_speed = sp_speed if (b_start and ready_to_run_temp) else 0.0
        tau_mech = 1.2
        actual_speed += ((target_speed - actual_speed) / tau_mech) * self.dt

        # 4. Calcul du courant statorique (proportionnel au couple d'accélération + charge)
        if actual_speed > 1.0 or target_speed > 0.0:
            accel_current = abs(target_speed - actual_speed) * 0.15
            steady_current = (actual_speed / 1500.0) * 180.0
            stator_current = min(450.0, steady_current + accel_current)
        else:
            stator_current = 0.0

        # 5. Tension Bus DC (chute de tension en charge ou injection de surtension)
        if self.fault_injections["dc_overvoltage"]:
            dc_voltage = 845.0
        else:
            dc_voltage = self.nominal_dc_voltage - (stator_current * 0.04)

        # 6. Modèle électrothermique des IGBT (Effet Joule R*I² vs dissipation)
        cooling_factor = 0.02 if self.fault_injections["cooling_loss"] else 0.15
        heating_power = (stator_current ** 2) * 0.0004
        cooling_power = (igbt_temp - self.ambient_temp) * cooling_factor
        igbt_temp += (heating_power - cooling_power) * self.dt

        # 7. Logique des relais de protection (Trip)
        if igbt_temp >= self.max_temp_threshold or dc_voltage >= self.overvoltage_threshold:
            fault_tripped = True

        # 8. Évaluation finale de la disponibilité (Prend en compte les défauts détectés à l'étape 7)
        ready_to_run = not self.fault_injections["breaker_trip"] and not fault_tripped

        return {
            "MAIN.fActualSpeed_RPM": round(actual_speed, 2),
            "MAIN.fDcBusVoltage_V": round(dc_voltage, 2),
            "MAIN.fStatorCurrent_A": round(stator_current, 2),
            "MAIN.fIgbtTemp_C": round(igbt_temp, 2),
            "MAIN.bReadyToRun": ready_to_run,
            "MAIN.bFaultTripped": fault_tripped
        }