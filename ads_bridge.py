import json
import logging
from typing import Any, Dict

try:
    import pyads
    PYADS_AVAILABLE = True
except ImportError:
    PYADS_AVAILABLE = False

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class BeckhoffADSBridge:
    """
    Gestionnaire d'interface de communication ADS pour automate Beckhoff TwinCAT.
    Basculer automatiquement sur une mémoire partagée simulée (Mock) si aucun runtime n'est joint.
    """

    def __init__(self, config_path: str = "io_mapping.json", use_mock: bool = True):
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        self.ams_net_id = self.config["plc_target"]["ams_net_id"]
        self.ams_port = self.config["plc_target"]["ams_port"]
        self.use_mock = use_mock or not PYADS_AVAILABLE
        self.plc = None

        # Mémoire interne (Mock PLC) et table de forçage I/O
        self._memory: Dict[str, Any] = {}
        self._forced_vars: Dict[str, Any] = {}
        self._init_memory()

    def _init_memory(self) -> None:
        """Initialise la table d'échange avec les valeurs par défaut du fichier JSON."""
        for group in ["inputs_from_plc", "outputs_to_plc"]:
            for var_name, meta in self.config["variables"][group].items():
                self._memory[var_name] = meta["default"]

    def connect(self) -> bool:
        """Établit la connexion ADS avec le runtime TwinCAT ou active le simulateur mémoire."""
        if not self.use_mock:
            try:
                self.plc = pyads.Connection(self.ams_net_id, self.ams_port)
                self.plc.open()
                logging.info(f"Connecté au runtime TwinCAT ({self.ams_net_id}:{self.ams_port})")
                return True
            except Exception as e:
                logging.warning(f"Échec connexion ADS ({e}). Basculement en mode Mock autonome.")
                self.use_mock = True
        return True

    def read_var(self, name: str) -> Any:
        """Lit une variable automate (prend en compte le forçage I/O éventuel)."""
        if name in self._forced_vars:
            return self._forced_vars[name]
        if not self.use_mock and self.plc:
            return self.plc.read_by_name(name)
        return self._memory.get(name)

    def write_var(self, name: str, value: Any) -> None:
        """Écrit une variable vers l'automate (sauf si elle est forcée par l'opérateur)."""
        if name in self._forced_vars:
            self._memory[name] = self._forced_vars[name]
            return
        if not self.use_mock and self.plc:
            self.plc.write_by_name(name, value)
        self._memory[name] = value

    def force_var(self, name: str, value: Any) -> None:
        """Force une variable à une valeur fixe pour les tests de validation."""
        self._forced_vars[name] = value
        self._memory[name] = value

    def release_var(self, name: str) -> None:
        """Libère le forçage d'une variable."""
        self._forced_vars.pop(name, None)

    def get_all_states(self) -> Dict[str, Any]:
        """Retourne un snapshot complet de la table d'échange."""
        return {k: self.read_var(k) for k in self._memory.keys()}