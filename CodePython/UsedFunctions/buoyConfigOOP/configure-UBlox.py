import pyublox

def configure_module(nav_rate):
    # Create an instance of the Ublox class
    u = pyublox.Ublox("/dev/ttyS0")

    try:
        # Send a command to set the navigation rate
        u.configure_navigation_rate(rate_ms=nav_rate)

        # Send a command to save the current configuration
        u.save_current_config()

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Close the connection
        u.close()
