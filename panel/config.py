# Config file maintainance
from configparser import ConfigParser


class ConfigFile:

    def __init__(self):
        self.cfg = ConfigParser()

        # setup default structure
        self.cfg["Default"] = {
            "Brightness": "15",         # ranges from 0-15
            "Instance":   "COM1",       # can be COM1, COM2, COM3
            "Sim": "x-plane",           # can be x-plane or p3d or fsx
        }

        self.cfg["Mapping"] = {
            "COM1": "",
            "COM2": "",
            "COM3": "",
            "HF1" : "",
            "HF2" : "",
            "VOR" : "",
            "ILS" : "",
            "MLS" : "",
            "ADF" : "",
            "BFO" : ""
        }

        self.cfg["Variables"] = {
            "COM1_Active" : "118.3",
            "COM1_Stdby"  : "118.0",
            "COM2_Active" : "118.4",
            "COM2_Stdby"  : "118.1",
            "COM3_Active" : "118.5",
            "COM3_Stdby"  : "118.2",
            "NAV_Override": "False",
            "Mode"        : "COM1",     # can by COM1, COM2, COM3, HF1, HF2, AM, VOR, ILS, MLS, ADF, BFO
        }

        self.cfg.read("radio.ini")

    def close(self):
        try:
            with open('radio.ini', 'w') as conf:
                self.cfg.write(conf)
        except OSError:
            print ("Failed to write radio.ini")


