from RasPiNetworking import RasPiNetworking
from RasPiKnownNetworks import RasPiKnownNetworks
from RasPiNetworkController import RasPiNetworkController
from RasPiUserControl import RasPiUserControl

class RasPiUtilities:

    # RasPiUtilities supports wifi network scanning and connectivity along with
    # access point - wifi station mode change
    #
    def __init__(self, known_wifi_network_database_name='', interface_name='wlan0', signal_strength_limit=-52):

        self.Networking = RasPiNetworking(interface_name)
        self.NetworkDatabase = RasPiKnownNetworks(known_wifi_network_database_name)
        self.NetworkController = RasPiNetworkController(self.Networking, self.NetworkDatabase, signal_strength_limit)
        self.UserControl = RasPiUserControl(self.Networking, self.NetworkController)

    # Function that is started from the main script and runs the entire automatization of Raspberry Pi
    #
    def start(self):

        # Make sure everything is setup properly on the Raspberry Pi for script to run
        self.UserControl.restart_configuration()

        # Load your known networks from a file
        self.NetworkDatabase.load_known_networks()

        # Start the user input thread
        self.UserControl.start_input_thread()

        # Start reactor thread and create your interface inside the Networking class
        self.Networking.start_reactor_thread()
        self.Networking.create_interface()

        # Connect to the strongest network of your known networks
        self.NetworkController.connect_to_strongest_network()
        # Start the thread that checks the signal strength of your network
        self.NetworkController.start_check_network_thread()
