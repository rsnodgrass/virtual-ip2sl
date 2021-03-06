import sys
import time
import serial
import logging
import threading

log = logging.getLogger(__name__)

DEFAULT_CONFIG = {
    'baud':      9600,
    'flow':      'FLOW_NONE',
    'parity':    'PARITY_NO',
    'stop_bits': 'STOPBITS_1',
    'timeout':   10
}

PARITY = {
    'PARITY_NO':   'N', # serial.PARITY_NONE,
    'PARITY_ODD':  'O', # serial.PARITY_ODD,
    'PARITY_EVEN': 'E'  # serial.PARITY_EVEN
}

STOP_BITS = {
    'STOPBITS_1':  1, # serial.STOPBITS_ONE
    'STOPBITS_2':  2  # serial.STOPBITS_TWO
}

FLOW_OR_DUPLEX = {
    'FLOW_HARDWARE': 'rs232',
    'FLOW_NONE':     'rs232',
    'DUPLEX_HALF':   'rs485',
    'DUPLEX_FULL':   'rs485'
}

def get_with_default(config, key):
    if key not in config:
        config[key] = DEFAULT_CONFIG[key] # update config with default if missing
    return config[key]

class IP2SLSerialInterface:
    def __init__(self, config):
        self._lock = threading.Lock()
        self._tty_path = config['path']
        self._config = config

        try:
            self._raw_serial = None
            self.get_raw_serial()
        except:
            log.error("Unexpected error: %s", sys.exc_info()[0])
            raise RuntimeError("Connect failure to {}".format(self._tty_path))

    def get_raw_serial(self):
        with self._lock:
            if self._raw_serial:
                return self._raw_serial
            
            config = self._config

            baud = int(get_with_default(config, 'baud'))
            self._baud = max(min(baud, 115200), 300) # ensure baud is ranged between 300-115200
            config['baud'] = self._baud # rewrite config to ensure it is within range

            self._parity    = PARITY[get_with_default(config, 'parity')]
            self._stop_bits = STOP_BITS[get_with_default(config, 'stop_bits')]
            self._timeout   = int( get_with_default(config, 'timeout') )
            
            # default to hardware flow control on (FLOW_HARDWARE)
            self._flow  = get_with_default(config, 'flow')
            flow_rtscts = (self._flow == 'FLOW_HARDWARE')
            flow_dsrdtr = flow_rtscts

            raw_serial = serial.Serial(self._tty_path,
                                         timeout=self._timeout,
                                         baudrate=self._baud,
                                         parity=self._parity,
                                         stopbits=self._stop_bits,
                                         bytesize=serial.EIGHTBITS,
                                         dsrdtr=flow_dsrdtr,
                                         rtscts=flow_rtscts)
            log.info(f"Connected to {self._tty_path} (config={self._config})")

            self._rs485 = self._flow in [ 'DUPLEX_FULL', 'DUPLEX_HALF' ]
            if self._rs485:
                message = f"RS485 not yet supported! (detected RS485 flow/duplex '{self._flow}' configuration)"
                log.error(message)
                raise RuntimeError(message)
                # FIXME: support RS485 --> ser.rs485_mode = serial.rs485.RS485Settings()

            # configure serial port for non-blocking mode (POSTIX only), requires timeout=0
            raw_serial.nonblocking()

            self._raw_serial = raw_serial

        return self._raw_serial


    def config(self):
        with self._lock:
            return self._config

    def close(self):
        with self._lock:
            raw_serial = self.get_raw_serial()
            if raw_serial:
                raw_serial.flush()
                raw_serial.close()

    # FIXME: this should really just change the existing serial connection, but for
    # now we will just swap and replace the serial object.
    def reset_serial_parameters(self, config):
        with self._lock:
            try:
                if self._raw_serial:
                    self._raw_serial.close()
                    self._raw_serial = None

                # update config and reopen raw serial
                self._config = config
                raw_serial = self.get_raw_serial()

            except:
                log.error("Unexpected error: %s", sys.exc_info()[0])
                raise RuntimeError("Connect failure to {}".format(self._tty_path))