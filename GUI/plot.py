import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.ticker as ticker
import pandas as pd

class AnimationPlot:
    def __init__(self, port):
        self.file_initialized = False  # Flag to track if the CSV file header is written
        self.fig, (self.ax1, self.ax2, self.ax3) = plt.subplots(3, 1, figsize=(8, 10), facecolor='black',dpi=80)  # 3 gráficos empilhados
        self.port = port

    def animate(self, framedata, ser, csv_writer):
        ser.read_data(csv_writer)
        
        t1dataList = ser.t1Data[-50:]   # Fix the list size so that the animation plot 'window' is x number of points
        t2dataList = ser.t2Data[-50:]
        t3dataList = ser.t3Data[-50:]
        pdataList = ser.pData[-50:]
        edataList = ser.eData[-50:]

        # Limpa os gráficos anteriores
        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()

        self.ax1.plot(t1dataList,label="T1",color='Cyan')
        self.ax1.plot(t2dataList,label="T2",color='Yellow')
        self.ax1.plot(t3dataList,label="T3",color='Green')
        self.ax2.plot(pdataList,color='Cyan')
        self.ax3.plot(edataList,color='Cyan')

        # Calcula o máximo e mínimo apenas se a lista não estiver vazia, caso contrário define um valor padrão

        max_temp = int(max(
            max(t1dataList) if t1dataList else 50,  # Usa -inf como padrão para garantir que será ignorado no max()
            max(t2dataList) if t2dataList else 50,
            max(t3dataList) if t3dataList else 50
        ))

        min_temp = int(min(
            min(t1dataList) if t1dataList else 0,  # Usa inf como padrão para garantir que será ignorado no min()
            min(t2dataList) if t2dataList else 0,
            min(t3dataList) if t3dataList else 0
        ))

        # Verifica se pdataList não está vazio
        max_pressure = int(max(pdataList) if pdataList else 50)
        min_pressure = int(min(pdataList) if pdataList else 0)

        # Verifica se edataList não está vazio
        max_empuxo = int(max(edataList) if edataList else 50)
        min_empuxo = int(min(edataList) if edataList else 0)


        self.getPlotFormat(self.ax1, "Temperatura", min_temp, max_temp, "°C")
        self.getPlotFormat(self.ax2, "Pressão", min_pressure, max_pressure, "bar")
        self.getPlotFormat(self.ax3, "Empuxo", min_empuxo, max_empuxo, "N")

    def showAnimation(self, ser, csv_writer):
        ani = animation.FuncAnimation(self.fig, self.animate, frames=60, fargs=(ser, csv_writer), interval=220)
        plt.tight_layout()
        plt.show()

    def plot_saved_file(self, csv_file):
        # Leitura dos dados do CSV
        data = pd.read_csv(csv_file)

        # Converter a coluna 'Hora' para um formato de tempo
        data['Hora'] = pd.to_datetime(data['Hora'], format='%H:%M:%S')

        # Calcular os Segundos desde a primeira amostra
        data['Segundos'] = (data['Hora'] - data['Hora'].iloc[0]).dt.total_seconds()

        # Dividir todos os valores exceto 'Segundos' por 100
        data['T1'] = data['T1'] / 100
        data['T2'] = data['T2'] / 100
        data['T3'] = data['T3'] / 100
        data['Pressao'] = data['Pressao'] / 100
        data['Empuxo'] = data['Empuxo'] / 100

        # Definindo cores para o fundo e as linhas
        background_color = 'black'
        line_colors = ['cyan', 'magenta', 'yellow']

        # Criar múltiplas figuras em uma única janela (plt.show() será chamado uma vez no final)
        fig1, ax1 = plt.subplots(figsize=(10, 5), facecolor=background_color)
        fig2, ax2 = plt.subplots(figsize=(10, 5), facecolor=background_color)
        fig3, ax3 = plt.subplots(figsize=(10, 5), facecolor=background_color)

        # 1º Gráfico: T1, T2, T3
        ax1.plot(data['Segundos'], data['T1'], label='T1', marker='o', color=line_colors[0])
        ax1.plot(data['Segundos'], data['T2'], label='T2', marker='o', color=line_colors[1])
        ax1.plot(data['Segundos'], data['T3'], label='T3', marker='o', color=line_colors[2])
        ax1.set_title("Temperatura x Tempo", color='white')
        ax1.set_xlabel("Tempo [s]", color='white')
        ax1.set_ylabel("Temperatura [°C]", color='white')
        ax1.set_facecolor(background_color)
        ax1.spines['left'].set_color('white')
        ax1.spines['bottom'].set_color('white')
        ax1.tick_params(axis='y', colors='white')
        ax1.tick_params(axis='x', colors='white')
        ax1.grid(True, linestyle='-', linewidth=0.5, color='purple')
        ax1.legend(loc='upper right', facecolor=background_color, edgecolor='white', labelcolor='white')

        # 2º Gráfico: Pressão
        ax2.plot(data['Segundos'], data['Pressao'], marker='o', color='cyan')
        ax2.set_title("Pressão x Tempo", color='white')
        ax2.set_xlabel("Tempo [s]", color='white')
        ax2.set_ylabel("Pressão [bar]", color='white')
        ax2.set_facecolor(background_color)
        ax2.spines['left'].set_color('white')
        ax2.spines['bottom'].set_color('white')
        ax2.tick_params(axis='y', colors='white')
        ax2.tick_params(axis='x', colors='white')
        ax2.grid(True, linestyle='-', linewidth=0.5, color='purple')

        # 3º Gráfico: Empuxo
        ax3.plot(data['Segundos'], data['Empuxo'], marker='o', color='cyan')
        ax3.set_title("Empuxo x Tempo", color='white')
        ax3.set_xlabel("Tempo [s]", color='white')
        ax3.set_ylabel("Empuxo", color='white')
        ax3.set_facecolor(background_color)
        ax3.spines['left'].set_color('white')
        ax3.spines['bottom'].set_color('white')
        ax3.tick_params(axis='y', colors='white')
        ax3.tick_params(axis='x', colors='white')
        ax3.grid(True, linestyle='-', linewidth=0.5, color='purple')

        # Mostrar todas as figuras ao mesmo tempo
        plt.tight_layout()
        plt.show()


    def getPlotFormat(self, ax, title, min, max, unidades):
        ax.set_ylim([min-5, max+5])  # Limite do eixo Y
        ax.yaxis.set_major_locator(ticker.MultipleLocator(5))  # Intervalo dos ticks no eixo Y
        ax.set_title(f"{title}", color='white')  # Título do gráfico
        ax.set_ylabel(f"{unidades}", color='white')
        ax.set_facecolor('black')
        ax.spines['left'].set_color('white')
        ax.tick_params(axis='y', colors='white')
        ax.grid(True, linestyle='-', linewidth=0.5, color='purple')
        ax.spines['bottom'].set_visible(False)  # Oculta o eixo X
        ax.tick_params(axis='x', which='both', bottom=False, top=False)  # Remove os ticks do eixo X
        
        if unidades == "°C":
            ax.legend(loc='upper right', frameon=False, fontsize='small', labelcolor='white')  # Legenda fixa no canto superior direito
            ax.legend()