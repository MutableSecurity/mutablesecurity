from enum import Enum

from ._abstract import AbstractSolution


# TODO: Remove this. Automatically detect the available solution.
class AvailableSolution(Enum):
    SURICATA = ("suricata", "Suricata")
    TELER = ("teler", "Teler")
    LETS_ENCRYPT = ("lets_encrypt", "LetsEncrypt")
