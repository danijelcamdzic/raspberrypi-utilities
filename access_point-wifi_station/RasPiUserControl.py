import os
import time
import threading

class RasPiUserControl:

    # RasPiUserControl let's the user control the mode (access point or wifi station) of the Raspberry Pi
    #
    def __init__(self, Networking=None, NetworkController=None):

        self.mode = 'Wifi Station'
        self.Networking = Networking
        self.NetworkController = NetworkController

    # Starting the thread that takes input from the user to control the mode change
    #
    def start_input_thread(self):

        input_ = threading.Thread(target = self.input_thread, args=())
        input_.start()
        time.sleep(0.1)

    # The actual input thread
    #
    def input_thread(self):

        while (1):
            command = input()

            if command == 'a':
                
                self.configure_access_point_mode()

            elif command == 's':

                self.configure_wifi_station_mode()

                while(1):
                    try:
                        # Start reactor thread and create your interface inside the Networking class
                        self.Networking.start_reactor_thread()
                        self.Networking.create_interface()

                        # Connect to the strongest network of your known networks
                        self.NetworkController.connect_to_strongest_network()
                            
                        self.NetworkController.SetWifiMode()
                        break
                    
                    except:
                        time.sleep(2)
                        continue

    # Setup access point mode
    #
    def configure_access_point_mode(self):

        self.NetworkController.SetAPMode()
        time.sleep(5)
        os.system("clear")
        print('Setting access point mode..\n')
        os.system("sudo systemctl stop wpa_supplicant")
        time.sleep(5)
        os.system("sudo systemctl stop wpa_supplicant@wlan0.service")
        time.sleep(5)
        os.system("sudo systemctl start wpa_supplicant@ap0.service")
        self.mode = 'Access Point'
        print('Info: Activated access point mode!\n')
        self.NetworkController.ResetConnectedSSID()

    # Setup wifi station mode
    #
    def configure_wifi_station_mode(self):

        print('Setting wifi station mode..\n')
        os.system("sudo systemctl stop wpa_supplicant@ap0.service")
        time.sleep(5)
        os.system("sudo systemctl stop wpa_supplicant")
        time.sleep(5)
        self.mode = 'Wifi Station'
        print('Info: Activated wifi station mode!\n')

    # Restarts configuration so script can start properly
    #
    def restart_configuration(self):

        os.system("sudo systemctl stop wpa_supplicant@ap0.service")
        time.sleep(2)
        os.system("sudo systemctl stop wpa_supplicant@wlan0.service")
        time.sleep(2)
        os.system("sudo systemctl stop wpa_supplicant")
        time.sleep(2)

