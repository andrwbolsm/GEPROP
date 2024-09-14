import serial
import time

class Serial:
    def __init__(self,baud,com):
        self.baud = baud
        self.com = com
        self.ser = None

        self.connect()

    def connect(self):
        self.ser = serial.Serial(self.com, self.baud)

        time.sleep(2)  # Tempo para inicializar a porta serial
    
    def close_con(self):
        self.ser.close()