import serial
import time
from datetime import datetime  # Importa o módulo para trabalhar com datas e horas
import queue
from threading import Thread
import csv
from collections import deque


class Serial:
    def __init__(self, baud, com,update_log = None, filename = None):
        self.baud = baud
        self.com = com
        self.ser = None

        self.file = None
        self.file_initialized = False
        self.filename = filename

        self.t1Data = deque(maxlen=300)
        self.t2Data = deque(maxlen=300)
        self.t3Data = deque(maxlen=300)
        self.pData = deque(maxlen=300)
        self.eData = deque(maxlen=300)

        self.csv_writer = None

        # Se um nome de arquivo foi fornecido, abra o CSV
        if self.filename:
            self.file = open(f'dados_salvos/{self.filename}.csv', mode='w', newline='')
            self.csv_writer = csv.writer(self.file)
            self.csv_writer.writerow(["Hora", "T1", "T2", "T3", "Pressao", "Empuxo", "Falhas"])  # Cabeçalho
            self.file_initialized = True

        self.update_log = update_log  # Store the update_log function
        self.ser = serial.Serial(self.com, self.baud)
        time.sleep(1)  # Tempo para inicializar a porta serial

        self.message_queue = queue.Queue()  # Fila para armazenar mensagens
        self.data_queue = queue.Queue()  # Fila para dados do gráfico

        # Iniciar a thread de leitura contínua
        self.stop_thread = False  # Flag para parar a thread de leitura
        self.read_thread = Thread(target=self.read_continuously)
        self.read_thread.start()

        # self.send_message("1")

    def send_message(self, message):
        self.message_queue.put(message)

    def read_continuously(self):
        """Lê continuamente os dados da serial e envia mensagens da fila."""
        try:
            while not self.stop_thread:
                # Verifica se há mensagens na fila
                if not self.message_queue.empty():
                    message = self.message_queue.get()
                    if self.ser and self.ser.is_open:
                        self.ser.write(message.encode('ascii'))

                # Lê dados da serial
                if self.ser and self.ser.in_waiting > 0:
                    raw_data = self.ser.readline().decode('utf-8', errors='ignore').strip()
                    try:
                        arduinoData_list = [int(x) for x in raw_data.strip('[]').split(',')]
                        if len(arduinoData_list) >= 5:
                            timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
                            # Dados para os 3 primeiros valores do vetor
                            self.t1Data.append(arduinoData_list[0]/100)
                            self.t2Data.append(arduinoData_list[1]/100)
                            self.t3Data.append(arduinoData_list[2]/100)
                            self.pData.append(arduinoData_list[3]/100)
                            self.eData.append(arduinoData_list[4]/100)

                            self.data_queue.put(arduinoData_list)

                            if self.csv_writer is not None:
                                if not self.file_initialized:
                                    self.file_initialized = True
                                self.csv_writer.writerow([timestamp] + arduinoData_list)  # Grava no CSV

                            # Atualiza o log com os novos dados
                            if self.update_log:
                                self.update_log(
                                    f"\n {timestamp} -> Dados recebidos: \n Termopar 1: {self.t1Data[-1]} °C \n Termopar 2: {self.t2Data[-1]} °C \n Termopar 3: {self.t3Data[-1]} °C \n Pressão: {self.pData[-1]} bar \n Empuxo: {self.eData[-1]} N \n Falhas na TX: {arduinoData_list[5]}")

                            # self.plot_ready = True
                    except Exception as e:
                            if raw_data:
                                self.update_log(
                                    f"\n {datetime.now().strftime('%H:%M:%S')} -> Dados recebidos: \n {raw_data}")
            
        except Exception as e:
            pass

    def close_con(self):
        """Método para fechar a conexão serial."""
        if self.ser is not None:
            try:
                self.ser.close()
                self.update_log("\nConexão serial anterior fechada com sucesso.")
                self.stop_thread = True
            except Exception as e:
                self.update_log(f"Erro ao fechar a conexão serial: {e}")
        else:
            self.update_log("Nenhuma conexão serial ativa.")

        # Fecha o arquivo CSV
        if self.file:
            try:
                self.file.close()
                self.update_log("\nArquivo CSV salvo e fechado com sucesso.")
            except Exception as e:
                self.update_log(f"Erro ao fechar o arquivo CSV: {e}")
