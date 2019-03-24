from configparser import ConfigParser


class config:

    def __init__(self):
		# Initialize the config file parser
        self.profiles = ConfigParser()
        self.cfg = ConfigParser()
        # Prepare the internal variables
        self.Profiles = []
        self.Types = []
        self.Variables = []

    # loads the configuration file with the given path and filename
    def load(self, filename):
        # load the configuration file(s)
		# load the config file
        try:
            print ("Reading config file " + filename)
            self.profiles.read(filename)
            print ('{} has {} profiles'.format(filename, self.getNumberOfProfiles()))
            activeProfile = self.profiles["Default"]["Active"]
            filename=self.profiles[activeProfile]["filename"]
            print ('Loading profile {} from file {}'.format(activeProfile, filename))
            self.cfg.read('config/{}'.format(filename))
        except:
            return False
        return True

    def getActiveProfileName(self):
        p_name = self.profiles["Default"]["Active"]
        p_idx = self.profiles["Profiles"].values().index(p_name)
        p_ID = self.profiles["Profiles"].keys()[p_idx]
        return p_ID

    def getActiveProfileNum(self):
        p_name = self.profiles["Default"]["Active"]
        p_idx = self.profiles["Profiles"].values().index(p_name)
        return p_idx

    def nextProfile(self):
        p_idx = self.getActiveProfileNum()
        p_idx = p_idx + 1
        if p_idx > self.getNumberOfProfiles() - 1:
            p_idx = 0
        new_profile_name = self.profiles["Profiles"].values()[p_idx]
        filename = self.profiles[new_profile_name]["filename"]
        self.profiles["Default"]["Active"] = new_profile_name
        print ('Loading profile {} from file {}'.format(new_profile_name, filename))
        self.cfg.clear()
        self.cfg.read('config/{}'.format(filename))

    def prevProfile(self):
        p_idx = self.getActiveProfileNum()
        p_idx = p_idx - 1
        if p_idx < 0:
            p_idx = self.getNumberOfProfiles()-1
        new_profile_name = self.profiles["Profiles"].values()[p_idx]
        filename = self.profiles[new_profile_name]["filename"]
        self.profiles["Default"]["Active"] = new_profile_name
        print ('Loading profile {} from file {}'.format(new_profile_name, filename))
        self.cfg.clear()
        self.cfg.read('config/{}'.format(filename))

    def getNumberOfProfiles(self):
        return self.profiles["Profiles"].keys().__len__()

    # returns the collection of Requests for the active Profile
    def getRequests(self):
        return self.cfg["Requests"]

    # returns the collection of Variables for the active Profile
    def getVariables(self):
        return self.cfg["Variables"]

    # returns the variable type for the given variable
    def getVariableType(self, var):
        return self.getVariableItem(var, "type")

    # returns the given item for the given variable
    def getVariableItem(self, var, item):
        var = 'Var.{}'.format(var)
        return self.cfg[var][item]

    # returns the collection of states in the given map
    def getMap(self, mapname):
        map = 'Map.{}'.format(mapname)
        return self.cfg[map]

