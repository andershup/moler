import os.path
import time
from moler.config import load_config
from moler.device.device import DeviceFactory


def test_network_outage():
    load_config(config=os.path.abspath('config/my_devices.yml'))
    unix1 = DeviceFactory.get_device(name='MyMachine1')
    unix2 = DeviceFactory.get_device(name='MyMachine2')

    # test setup - ensure network is up before running test
    net_up = unix2.get_cmd(cmd_name="ifconfig", cmd_params={"options": "lo up"})
    sudo_ensure_net_up = unix2.get_cmd(cmd_name="sudo", cmd_params={"password": "moler", "cmd_object": net_up})
    sudo_ensure_net_up()

    # run test
    ping = unix1.get_cmd(cmd_name="ping", cmd_params={"destination": "localhost", "options": "-O"})
    ping.start(timeout=120)
    time.sleep(3)

    # run event observing "network down"
    no_ping = unix1.get_event(event_name="ping_no_response")
    no_ping.start()

    ifconfig_down = unix2.get_cmd(cmd_name="ifconfig", cmd_params={"options": "lo down"})
    sudo_ifconfig_down = unix2.get_cmd(cmd_name="sudo", cmd_params={"password": "moler", "cmd_object": ifconfig_down})
    sudo_ifconfig_down()

    time.sleep(5)

    ifconfig_up = unix2.get_cmd(cmd_name="ifconfig", cmd_params={"options": "lo up"})
    sudo_ifconfig_up = unix2.get_cmd(cmd_name="sudo", cmd_params={"password": "moler", "cmd_object": ifconfig_up})
    sudo_ifconfig_up()

    time.sleep(3)

    # test teardown
    ping.cancel()
    no_ping.cancel()


if __name__ == '__main__':
    test_network_outage()

"""
copy this file into workshop1/network_outage.py
*** running event in background ***
1. run it
2. see logs - look for 'PingNoResponse' inside moler.log and moler.MyMachine1.log

3. exchange:
     no_ping = unix1.get_event(event_name="ping_no_response")
   with:
     no_ping = unix1.get_event(event_name="ping_no_response", event_params={"till_occurs_times": 1})
   see difference in logs
 
   Default for events is to run them for infinite occurrences of "observed thing" ("till_occurs_times": -1)
   But you may use as you with - maybe tested "background event" should occur just 3 times?

4. Question: is shifting no_ping.start() after sudo_ifconfig_down() correct?
"""
