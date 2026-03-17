import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
from serial_con import Serial
import serial.tools.list_ports
from plot import AnimationPlot
import threading
from tkinter import scrolledtext

class Gui:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GEPROP")
        self.root.geometry("640x480")
        self.root.configure(bg="white")  # Define o fundo como branco
        # self.root.resizable(False, False)  # Impede a maximização
        
        # Frame lateral para os controles
        self.left_frame = tk.Frame(self.root, bg='White')
        self.left_frame.pack(side=tk.LEFT, fill=tk.X, padx=10, pady=10)

        # Botão para configuração de conexão
        self.connect_button = tk.Button(self.left_frame, text="Configuração", command=self.open_connection_window,padx=25,pady=5)
        self.connect_button.pack(padx=5, pady=5)

        # Botão para plotar dados salvos
        self.plot_saved_button = tk.Button(self.left_frame, text="Visualizar dados salvos", pady=5, command=self.plot_saved_data)
        self.plot_saved_button.pack(padx=5, pady=5)

        # Botão para teste
        self.test_button = tk.Button(self.left_frame, text="TESTE", command=self.teste,padx=45,pady=5,state='disabled')
        self.test_button.pack(padx=5, pady=5)

        # Botão para iniciar
        self.start_button = tk.Button(self.left_frame, text="IGNITAR", command=self.start,padx=39,pady=5,fg='#ff0000',state='disabled')
        self.start_button.pack(padx=5, pady=5)

        # Botão para resetar
        self.reset_button = tk.Button(self.left_frame, text="RESETAR", command=self.resetar,padx=39,pady=5,state='disabled')
        self.reset_button.pack(padx=5, pady=5)

        # Botão para gráfico
        self.animation_plot = None
        self.graph_button = tk.Button(self.left_frame,text="GRÁFICOS", padx = 33, pady=5, command=self.graph_plot, state='disabled')
        self.graph_button.pack(padx=5, pady=5)

        # Botão para fechar conexão
        self.close_button = tk.Button(self.left_frame,text="ENCERRAR", padx = 33, pady=5, command=self.stop_con,state='disabled')
        self.close_button.pack(padx=5, pady=5)

        # Frame para logs
        self.log_frame = tk.Frame(self.root, bg='White')
        self.log_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, padx=10, expand=True)

        # Área de texto para log de erros com barra de rolagem
        self.log_text = scrolledtext.ScrolledText(self.log_frame, height=10, width=80, bg='black', fg='white', insertbackground='white')
        self.log_text.pack(fill=tk.BOTH, expand=True)

        self.connection_info_label = tk.Label(
            self.root, text="", font=("Arial", 8), bg="white", fg="black", anchor="w"
        )
        self.connection_info_label.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)

        # Botões para controlar o log
        self.button_frame = tk.Frame(self.log_frame, bg='white')
        self.button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.lock_scroll_var = tk.BooleanVar(value=True)
        self.lock_scroll_button = tk.Checkbutton(self.button_frame, text="Travar Scroll", variable=self.lock_scroll_var)
        self.lock_scroll_button.pack(side=tk.RIGHT, fill=tk.X)

        self.clear_button = tk.Button(self.button_frame, text="Limpar Log", command=self.clear_log)
        self.clear_button.pack(side=tk.LEFT, fill=tk.X)

        # Carregar e exibir uma imagem no lado esquerdo
        self.image_path = r"C:\Users\andre\OneDrive\Documentos\GEPROP\GEPROP - CODES\GEPROP-1\GUI\images\logo.jpeg"  # Substitua pelo caminho correto da sua imagem
        self.image = Image.open(self.image_path)
        self.image = self.image.resize((150, 150))  # Ajuste o tamanho da imagem conforme necessário
        self.photo = ImageTk.PhotoImage(self.image)
        self.image_label = tk.Label(self.left_frame, image=self.photo)
        self.image_label.pack(padx=5, pady=5, expand=True)

        # Inicializa a conexão serial
        self.port_menu = None
        self.porta_var = tk.StringVar()
        self.csv_save_var = tk.BooleanVar()
        
        self.update_ports()
        self.baudrates = ["9600", "14400", "19200", "38400", "57600", "115200"]
        self.baudrate_var = tk.StringVar(value=self.baudrates[5])

        self.ser = None

        try:
            self.ser_connect(self.baudrate_var.get(), self.porta_var.get())
            self.update_log(f"Conectado na porta: {self.porta_var.get()}\nBaudrate: {self.baudrate_var.get()}\n\nPara alterar, acesse Configuração.")
        except Exception as e:
            print(e)

        self.monitor_usb_thread = threading.Thread(target=self.monitor_usb_disconnection, daemon=True)
        self.monitor_usb_thread.start()

        self.is_animation_running = False

        self.root.mainloop()

    def graph_plot(self):
        if not self.is_animation_running:
            self.is_animation_running = True  # Marca que o gráfico está ativo
            try:
                self.animation_plot = AnimationPlot(self.porta_var.get())
                self.animation_plot.showAnimation(self.ser)
            finally:
                self.is_animation_running = False  # Marca como inativo ao finalizar

    def ser_connect(self,baud,port, filename = None):
        if self.ser is not None:
            self.ser.close_con()

        if port != '-':
            self.ser = Serial(int(baud), port, update_log=self.update_log, filename=filename)
            self.connection_info_label.config(
            text=f"Conectado na porta {port} com baudrate {baud}"
            )
            self.start_button['state'] = 'normal'
            self.test_button['state'] = 'normal'
            self.reset_button['state'] = 'normal'
            self.close_button['state'] = 'normal'
            self.graph_button['state'] = 'normal'
        else:
            self.connection_info_label.config(text="Nenhuma conexão ativa")

    def stop_con(self):
        if self.ser:
            self.ser.close_con()
            self.connection_info_label.config(text="Nenhuma conexão ativa")
            self.start_button['state'] = 'disabled'
            self.test_button['state'] = 'disabled'
            self.reset_button['state'] = 'disabled'
            self.close_button['state'] = 'disabled'
            self.graph_button['state'] = 'disabled'
            self.csv_save_var.set(0)
        
        if self.animation_plot:
            self.is_animation_running = False 
            self.animation_plot.plot_close()

    def monitor_usb_disconnection(self):
        """Monitora se a porta USB conectada foi desconectada."""
        while True:
            if self.ser and self.ser.ser and self.ser.ser.is_open:
                connected_ports = self.get_serial_ports()
                if self.ser.ser.port not in connected_ports:
                    self.update_log(f"\nPorta {self.ser.ser.port} desconectada.")
                    self.stop_con()

    def open_connection_window(self):
        """Abre uma nova janela para configurar as conexões."""
        if hasattr(self, 'connection_window') and self.connection_window.winfo_exists():
            # Se a janela de conexão já estiver aberta, não faz nada
            return
        self.connection_window = tk.Toplevel(self.root)
        self.connection_window.title("Configurar Conexão")
        self.connection_window.geometry("200x215")

        self.connection_window.resizable(False, False)  # Impede a maximização

        # Elementos da interface para seleção da porta
        tk.Label(self.connection_window, text="Porta COM:").pack(pady=5)
        self.port_menu = tk.OptionMenu(self.connection_window, self.porta_var, *self.ports)
        self.port_menu.pack()

        # Atualiza o menu de portas
        self.update_ports()

        # Elementos da interface para seleção da baudrate
        tk.Label(self.connection_window, text="Baudrate:").pack(pady=5)
        tk.OptionMenu(self.connection_window, self.baudrate_var, *self.baudrates).pack()

        # Checkbox para salvar dados em CSV
        self.csv_checkbox = tk.Checkbutton(
            self.connection_window, text="Salvar dados em CSV", variable=self.csv_save_var, command=self.prompt_filename
        )
        self.csv_checkbox.pack(pady=10)

        # Botão para confirmar as configurações
        self.confirm_button = tk.Button(self.connection_window, text="Confirmar", command=self.close_connection_window, state="disabled")
        self.confirm_button.pack(pady=10)

        self.update_confirm_button()

    def update_confirm_button(self):
        """Habilita o botão Confirmar apenas se porta e baudrate forem selecionados."""
        if self.porta_var.get() != "-" and self.baudrate_var.get():
            self.confirm_button.config(state="normal")
        else:
            self.confirm_button.config(state="disabled")

    def close_connection_window(self):
        """Fecha a janela de configuração de conexão."""
        porta = self.porta_var.get()
        baudrate = self.baudrate_var.get()
        save_csv = self.csv_save_var.get()

        if save_csv:
            self.ser_connect(baudrate,porta, filename=self.filename)
        else:
            self.ser_connect(baudrate,porta, filename=None)
            
        self.update_log(f"\nConfigurações salvas:\nPorta: {porta}\nBaudrate: {baudrate}\nSalvar em CSV: {'Sim' if save_csv else 'Não'}")
        
        self.connection_window.destroy()

    def prompt_filename(self):
        """Exibe uma caixa de diálogo para solicitar o nome do arquivo se a opção CSV estiver selecionada."""
        if self.csv_save_var.get():
            self.filename = simpledialog.askstring("Nome do Arquivo", "Digite o nome do arquivo CSV:")
            if not self.filename:
                self.csv_save_var.set(False)  # Desmarca a opção se nenhum nome for fornecido

    def plot_saved_data(self):
        # Abrir o explorador de arquivos para selecionar o arquivo CSV
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv")],
            title="Selecione o arquivo CSV"
        )
        
        if file_path:
            try:
                AnimationPlot.plot_saved_file(None,file_path)
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao plotar dados salvos: {e}")
        else:
            messagebox.showerror("Erro", "Arquivo CSV não encontrado.")

    def start(self):
        self.ser.send_message('1')

    def teste(self):
        self.ser.send_message('2')

    def resetar(self):
        self.ser.send_message('3')

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
        self.ports = self.get_serial_ports()  # Obtém as portas disponíveis
        if self.ports:
            self.porta_var.set(self.ports[0])  # Define a primeira porta como padrão
        else:
            self.ports = ["-"]  # Define uma opção padrão quando não há portas
            self.porta_var.set(self.ports[0])

        if self.port_menu and "menu" in self.port_menu.keys():  # Garante que port_menu está inicializado
            self.port_menu["menu"].delete(0, "end")  # Limpa as opções do menu
            for port in self.ports:
                self.port_menu["menu"].add_command(
                    label=port,
                    command=lambda p=port: self.porta_var.set(p)
                )

    def get_serial_ports(self):
        """Obtém a lista de portas COM disponíveis."""
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]
