import argparse
from RasPiUtilities import RasPiUtilities

# Defines the argument list and default values
parser = argparse.ArgumentParser(description='Raspberry Pi utility script')
parser.add_argument("-w", "--known_wifi_network_database_name", help = "known wifi network database name", default = '')
parser.add_argument("-i", "--interface_name", help = "interface name", default = 'wlan0')
parser.add_argument("-s", "--signal_strength_limit", help = "minimum signal strength", default = -52)
args = parser.parse_args()

# Start the script which enables user to use the utilities
#
def main():

    # Creating a RasPiUtilities object and starting logging process
    RasPiUtility = RasPiUtilities(known_wifi_network_database_name = args.known_wifi_network_database_name,
                                        interface_name = args.interface_name,
                                        signal_strength_limit = args.signal_strength_limit
                                        )
    # Start the automatization process
    RasPiUtility.start()

if __name__ == '__main__':

    main()