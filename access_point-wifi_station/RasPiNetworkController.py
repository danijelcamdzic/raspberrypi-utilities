import threading
import time

class RasPiNetworkController:

    # RasPiNetworkController controlls the networks and checks signal strength
    #
    def __init__(self, Networking=None, NetworkDatabase=None, signal_strength_limit=-60):

        self.Networking = Networking
        self.NetworkDatabase = NetworkDatabase
        self.signal_strength_limit = signal_strength_limit
        self.connected_ssid = ''
        self.ap_mode = 0

    # Sets the connected ssid name to empty
    #
    def ResetConnectedSSID(self):

        self.connected_ssid = ''

    # Set mode to acces point
    #
    def SetAPMode(self):

        self.ap_mode = 1

    # Set mode to wifi station
    #
    def SetWifiMode(self):

        self.ap_mode = 0

    # Connect to the strongest available network
    #
    def connect_to_strongest_network(self):

        while(1):
            try:
                scan_results = self.Networking.scan_networks()
                break
            except:
                continue

        best_ssid = ''
        best_connection = -100
        location_of_best = -1

        for bss in scan_results:
            ssid = bss.get_ssid()
            sign_str = bss.get_signal_dbm()
            location = self.NetworkDatabase.locate(ssid)
            if location != -1:
                if sign_str > best_connection:
                    best_ssid = ssid
                    best_connection = sign_str
                    location_of_best = location

        if (self.connected_ssid != best_ssid):
            print("Connecting...")
            self.connected_ssid = best_ssid
            self.Networking.connect_to_network(self.NetworkDatabase.get_network(location_of_best))
        
    # Start the thread which checks the signal strength of connected network
    #
    def start_check_network_thread(self):

        # Creating a network control
        check_network_thread = threading.Thread(target = self.check_network, args=())
        check_network_thread.start()
        time.sleep(0.1)

    # Function that does the network checking
    #
    def check_network(self):

        while(1):
            if self.ap_mode == 0:
                exists = 0
                scan_results = self.Networking.scan_networks()

                for bss in scan_results:
                    ssid = bss.get_ssid()
                    if self.connected_ssid == ssid:
                        exists = 1
                        if bss.get_signal_dbm() < self.signal_strength_limit:
                            print("Network signal is weak, reconnecting to another one..\n")
                            self.connect_to_strongest_network()
                
                if exists == 0:
                    print("Network disconected, reconnecting to another one..\n")
                    self.connected_ssid = ''
                    self.connect_to_strongest_network()
