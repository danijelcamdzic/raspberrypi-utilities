class RasPiKnownNetworks:

    # RasPiKnownNetworks loads the known networks into a list
    #
    def __init__(self, known_wifi_network_database_name=''):

        self.known_wifi_network_database_name = known_wifi_network_database_name
        self.known_wifi_network_database = []
    
    # Returns the network from the database list in the given location
    #
    def get_network(self, location):

        return self.known_wifi_network_database[location]

    # Load all the wifi networks from a file into a list
    #
    def load_known_networks(self):

        lines = []

        if self.known_wifi_network_database_name == '':
            print('Warning: No network database file was given. Consider restarting the program and adding it..')
            return

        filename = self.known_wifi_network_database_name
        f = open(filename, "r")
        lines = f.readlines()
        f.close

        if lines == '':
            print('Warning: The network database file you gave is empty!')
            return

        try:
            ssid, psk, key_mgmt = self.parse_strings(lines)
        except:
            print('Error: There was an error processing your network database file!')
            return

        self.add_to_database(ssid, psk, key_mgmt)

        print("Info: Loaded all the networks from the network database file. \n")

    # Parse the strings from the file into separate types
    #
    def parse_strings(self, lines):

        ssid = []
        psk = []
        key_mgmt = []

        for line in lines:
            if line[0] == '\n':
                continue
            line = line.split(' ')
            line[-1] = line[-1].strip()

            new_line = []

            for item in line:
                if item:
                    item = item.replace("\t", "")
                    new_line.append(item)

            if len(new_line) != 3:
                print('Warning: There was an error reading the line from the database name! Process skipped it!')
                continue

            ssid.append(new_line[0])
            psk.append(new_line[1])
            key_mgmt.append(new_line[2])

        return (ssid, psk, key_mgmt)

    # Add the wifi network to database
    #
    def add_to_database(self, ssid, psk, key_mgmt):

        for ssid, psk, key_mgmt in zip(ssid, psk, key_mgmt ):
            wifi_network = {}
            wifi_network['ssid'] = ssid
            wifi_network['psk'] = psk
            wifi_network['key_mgmt'] = key_mgmt

            location = self.locate(ssid)

            if (location == -1):
                self.known_wifi_network_database.append(wifi_network)
            else:
                object_to_replace = self.known_wifi_network_database[location]
                self.known_wifi_network_database[location] = wifi_network
                del object_to_replace
                print('Warning: Two wifi networks from the network database file have the same name!')

    # Check to see if wifi network with the same id already exists
    #
    def locate(self, name):

        for network in self.known_wifi_network_database:
            if name == network['ssid']:
                return self.known_wifi_network_database.index(network)
        
        return -1