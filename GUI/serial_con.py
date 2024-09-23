import serial
import time
from datetime import datetime  # Importa o módulo para trabalhar com datas e horas
from tkinter import messagebox

class Serial:
    def __init__(self, baud, com,update_log = None):
        self.baud = baud
        self.com = com
        self.ser = None

        self.t1Data = []
        self.t2Data = []
        self.t3Data = []
        self.pData = []
        self.eData = []

        self.error = False
        self.update_log = update_log  # Store the update_log function
        self.file_initialized = False
        self.connect()
        self.send_message("1")

    def connect(self):
        self.ser = serial.Serial(self.com, self.baud)
        time.sleep(2)  # Tempo para inicializar a porta serial

    def send_message(self, message):
        if self.ser is not None and self.ser.is_open:
            # Certifique-se de codificar a mensagem em bytes antes de enviar
            self.ser.write(message.encode('ascii'))  # Envia a mensagem
            arduinoData_string = self.ser.readline().decode('ascii').strip()  # Decode and strip newline characters
            if arduinoData_string == 'Falha ao ignitar.':
                messagebox.showerror("Erro", f"Falha ao ignitar.")
                self.error = True
        else:
            print("A conexão serial não está aberta.")

    def close_con(self):
        if self.ser is not None:
            self.ser.close()
            print("Conexão serial fechada.")

    def read_data(self,csv_writer):
        arduinoData_string = self.ser.readline().decode('ascii').strip()  # Decode and strip newline characters
        try:
            arduinoData_list = [int(x) for x in arduinoData_string.strip('[]').split(',')]
            if len(arduinoData_list) >= 5:
                timestamp = datetime.now().strftime("%H:%M:%S")  # Timestamp no formato HH:MM:SS
                # Dados para os 3 primeiros valores do vetor
                self.t1Data.append(arduinoData_list[0]/100)
                self.t2Data.append(arduinoData_list[1]/100)
                self.t3Data.append(arduinoData_list[2]/100)
                self.pData.append(arduinoData_list[3]/100)
                self.eData.append(arduinoData_list[4]/100)

                if csv_writer is not None:
                    if not self.file_initialized:
                        csv_writer.writerow(["Hora", "T1", "T2", "T3", "Pressao", "Empuxo", "Falhas"])  # Cabeçalho
                        self.file_initialized = True
                    csv_writer.writerow([timestamp] + arduinoData_list)  # Grava no CSV

                # Atualiza o log com os novos dados
                if self.update_log:
                    self.update_log(
                        f"\n {timestamp} -> Dados recebidos: \n Termopar 1: {self.t1Data[-1]} °C \n Termopar 2: {self.t2Data[-1]} °C \n Termopar 3: {self.t3Data[-1]} °C \n Pressão: {self.pData[-1]} bar \n Empuxo: {self.eData[-1]} N \n Falhas na TX: {arduinoData_list[5]}")

                self.plot_ready = True

        except ValueError:
            pass
