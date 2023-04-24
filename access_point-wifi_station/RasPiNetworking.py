import time
import threading
from wpa_supplicant.core import WpaSupplicantDriver
from twisted.internet.selectreactor import SelectReactor

class RasPiNetworking:

    # RasPiNetworking creates an interface with a given name
    #
    def __init__(self, interface_name='wlan0'):

        self.interface_name = interface_name
        self.reactor=None
        self.driver=None
        self.supplicant=None
        self.interface=None
        self.connected_network=None
    
    # Start a simple Twisted SelectReactor
    #
    def start_reactor_thread(self):

        self.reactor = SelectReactor()
        reactor_thread = threading.Thread(target=self.reactor.run, kwargs={'installSignalHandlers': 0})
        reactor_thread.start()
        time.sleep(0.1)

    # Create an interface with a given name
    #
    def create_interface(self):

        self.start_driver()

        self.connect_supplicant()

        # Register an interface w/ the supplicant, this can raise an error if the supplicant
        # already knows about this interface
        try:
            try:
                self.interface = self.supplicant.create_interface(self.interface_name)
                #print("Info: Created an interface!\n")
            except:
                self.interface = self.supplicant.get_interface(self.interface_name)
                #print("Info: Got an already created interface!\n")
        except:
            print("Error: An error occured with the creation of the interface!\n")

    # Start driver
    #
    def start_driver(self):

        self.driver = WpaSupplicantDriver(self.reactor)

    # Connect to the supplicant, which returns the "root" D-Bus object for wpa_supplicant
    #
    def connect_supplicant(self):

        self.supplicant = self.driver.connect()

    # Scan available networks in the area around your Raspberry Pi
    #
    def scan_networks(self):

        # Scanning the area
        scan_results = self.interface.scan(block=True)
        print('Scanning networks...')
        print ('--------------')
        for bss in scan_results:
            print(bss.get_ssid())
            print(bss.get_channel())
            print(bss.get_signal_dbm())
            print(bss.get_signal_quality())
            print ('--------------')
        print ('Finished scanning networks..\n')

        return scan_results

    # Connect to the given network
    #
    def connect_to_network(self, network={}):

        network_path = self.interface.add_network(network)
        self.connected_network = network

        self.interface.select_network(network_path.get_path())
        
        time.sleep(2)

        while(1):
            try:
                bss = self.interface.get_current_bss()
                ssid = bss.get_ssid()
                print("I am connected to: " + ssid + '\n')
                break
            except:
                time.sleep(2)
                continue
