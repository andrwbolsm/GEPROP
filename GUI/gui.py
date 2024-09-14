import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox, simpledialog
from serial_con import Serial
import serial.tools.list_ports
from plot import AnimationPlot
import csv
from tkinter import scrolledtext

class MenuWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Menu")

        # Botão para plotar dados serial
        self.plot_serial_button = tk.Button(self.root, text="Plotar Dados Serial", command=self.open_serial_plot_window)
        self.plot_serial_button.pack(pady=10)

        # Botão para plotar dados salvos
        self.plot_saved_button = tk.Button(self.root, text="Plotar Dados Salvos", command=self.plot_saved_data)
        self.plot_saved_button.pack(pady=10)

        self.root.mainloop()
    
    def open_serial_plot_window(self):
        self.root.destroy()
        Gui()
    
    def plot_saved_data(self):
        x = []
        y = []

        # Abrir o explorador de arquivos para selecionar o arquivo CSV
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv")],
            title="Selecione o arquivo CSV"
        )

        if file_path:
            try:
                with open(file_path, 'r') as file:
                    csv_reader = csv.reader(file)
                    next(csv_reader)  # Skip the header
                    cnt = 0
                    for row in csv_reader:
                        cnt = cnt + 1
                        if row:  # Make sure row is not empty
                            x.append(cnt)  # Sample number
                            y.append(float(row[1]))  # Value

                AnimationPlot.plot_saved_file(None,x,y)
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao plotar dados salvos: {e}")
        else:
            messagebox.showerror("Erro", "Arquivo CSV não encontrado.")
class Gui:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GEPROP - Software")
        self.root.geometry("640x360")

        # Frame superior para os controles
        self.top_frame = tk.Frame(self.root)
        self.top_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        # Elementos da interface para seleção da porta
        self.label_porta = tk.Label(self.top_frame, text="Porta COM:")
        self.label_porta.pack(side=tk.LEFT)
        
        self.port_menu = None
        self.porta_var = tk.StringVar()
        self.update_ports()  # Atualiza a lista de portas ao inicializar

        self.port_menu = tk.OptionMenu(self.top_frame, self.porta_var, *self.ports)
        self.port_menu.pack(side=tk.LEFT)

        # Botão para atualizar a lista de portas
        self.refresh_button = tk.Button(self.top_frame, text="Refresh", command=self.update_ports)
        self.refresh_button.pack(side=tk.LEFT)

        # Elementos da interface para seleção da baudrate
        self.label_baudrate = tk.Label(self.top_frame, text="Baudrate:")
        self.label_baudrate.pack(side=tk.LEFT)

        baudrates = ["9600", "14400", "19200", "38400", "57600", "115200"]
        self.baudrate_var = tk.StringVar(value=baudrates[0])
        self.baudrate_menu = tk.OptionMenu(self.top_frame, self.baudrate_var, *baudrates)
        self.baudrate_menu.pack(side=tk.LEFT)

        # Checkbox para salvar dados em CSV
        self.csv_save_var = tk.BooleanVar()
        self.csv_checkbox = tk.Checkbutton(self.top_frame, text="Salvar dados em CSV", variable=self.csv_save_var, command=self.prompt_filename)
        self.csv_checkbox.pack(side=tk.LEFT)

        # Botão para iniciar
        self.start_button = tk.Button(self.top_frame, text="Iniciar", command=self.start)
        self.start_button.pack(side=tk.LEFT)

        # Frame para logs
        self.log_frame = tk.Frame(self.root)
        self.log_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, padx=10, expand=True)

        # Área de texto para log de erros com barra de rolagem
        self.log_text = scrolledtext.ScrolledText(self.log_frame, height=10, width=80, bg='black', fg='white', insertbackground='white')
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Botões para controlar o log
        self.button_frame = tk.Frame(self.log_frame)
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.lock_scroll_var = tk.BooleanVar(value=True)
        self.lock_scroll_button = tk.Checkbutton(self.button_frame, text="Travar Scroll", variable=self.lock_scroll_var)
        self.lock_scroll_button.pack(side=tk.RIGHT, fill=tk.X)

        self.clear_button = tk.Button(self.button_frame, text="Limpar Log", command=self.clear_log)
        self.clear_button.pack(side=tk.LEFT, fill=tk.X)

        self.root.mainloop()

    def prompt_filename(self):
        """Exibe uma caixa de diálogo para solicitar o nome do arquivo se a opção CSV estiver selecionada."""
        if self.csv_save_var.get():
            self.filename = simpledialog.askstring("Nome do Arquivo", "Digite o nome do arquivo CSV:")
            if not self.filename:
                self.csv_save_var.set(False)  # Desmarca a opção se nenhum nome for fornecido

    def clear_log(self):
        self.log_text.delete(1.0, tk.END)

    def update_log(self, message):
        """Atualiza a caixa de log com a mensagem recebida."""
        self.log_text.insert(tk.END, message + "\n")
        
        # Se a checkbox estiver marcada, travar o scroll no final
        if self.lock_scroll_var.get():
            self.log_text.see(tk.END)  # Move o scroll para o final
        # Caso contrário, não travar o scroll

    def update_ports(self):
        """Atualiza a lista de portas COM disponíveis e atualiza o menu de seleção."""
        self.ports = self.get_serial_ports()
        if self.ports:
            self.porta_var.set(self.ports[0])  # Define a primeira porta como valor padrão
        else:
            self.ports = ["-"]  # Define uma opção padrão quando não há portas
            self.porta_var.set(self.ports[0])  # Define "Nenhuma porta disponível" como padrão
        if self.port_menu is not None:
            menu = self.port_menu["menu"]
            menu.delete(0, "end")
            for port in self.ports:
                menu.add_command(label=port, command=tk._setit(self.porta_var, port))

    def get_serial_ports(self):
        """Obtém a lista de portas COM disponíveis."""
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    def start(self):
        porta = self.porta_var.get()       # Obtém a porta escolhida
        baudrate = self.baudrate_var.get() # Obtém a baudrate escolhida
        save_csv = self.csv_save_var.get() # Obtém a escolha de salvar em CSV

        realTimePlot = AnimationPlot(port=self.porta_var.get(), update_log=self.update_log)

        try:
            ser = Serial(int(baudrate), porta)
            
            if save_csv:
                with open(self.filename + '.csv', mode='w', newline='') as file:
                    csv_writer = csv.writer(file)
                    realTimePlot.showAnimation(ser.ser, csv_writer)
            else:
                realTimePlot.showAnimation(ser.ser, csv_writer=None)

            ser.close_con()  # Fecha a conexão serial quando o plot é fechado

        except Exception as e:
            self.log_text.insert(tk.END, f"Erro: {e}\n")
            messagebox.showerror("Erro", f"Erro ao conectar com a porta serial: {e}")

# Exemplo de inicialização da interface
if __name__ == "__main__":
    menu = MenuWindow()
