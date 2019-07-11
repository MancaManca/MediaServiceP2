import threading

from kivy import Logger
import constant_instance as c_i


def scan_network_for_single_connection(_subnet, db_inst):
    Logger.info('Network scanning initializes on thread {}'.format(threading.currentThread().getName()))

    # network_address = '192.168.0.{}'.format(_subnet)
    Logger.info('Scanner for {}'.format(_subnet))
    s = c_i.So()

    try:
        _socket = s.sock.connect_ex((_subnet, 8000))

        if _socket == 0:
            Logger.info('Found online at {}'.format(_subnet))

            responded_msgs = s.sock.recv(2048)
            db_inst._put(key=_subnet, val=str(responded_msgs.decode()))

            Logger.info('Device on address {} responded with message {}'.format(_subnet,
                                                                                str(responded_msgs.decode())))
            s.sock.close()

        else:
            Logger.info('{} responded {}'.format(_subnet, _socket))

    finally:
        s.sock.close()
        Logger.info(
            'Current :{} Exiting for {} and closing {}'.format(threading.currentThread().getName(), _subnet, s))


def start_scanning(server_list, *args):
    for _subnet_in in server_list.values():
        t2 = threading.Thread(target=scan_network_for_single_connection, args=(_subnet_in,))
        t2.start()