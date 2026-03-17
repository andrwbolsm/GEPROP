import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.ticker as ticker
import pandas as pd

class AnimationPlot:
    def __init__(self, port):
        self.fig, (self.ax1, self.ax2, self.ax3) = plt.subplots(3, 1, figsize=(8, 10),dpi=70)  # 3 gráficos empilhados
        self.port = port
        self.fig.canvas.manager.set_window_title(f"{self.port}")

    def animate(self, i, ser):
        if not ser.data_queue.empty():
            # Atualizar dados
            while not ser.data_queue.empty():
                data = ser.data_queue.get()

                # Atualizar os buffers de dados
                ser.t1Data.append(data[0] / 100)
                ser.t2Data.append(data[1] / 100)
                ser.t3Data.append(data[2] / 100)
                ser.pData.append(data[3] / 100)
                ser.eData.append(data[4] / 100)

            # Pega os últimos 5 segundos
            # t1dataList = list(ser.t1Data)
            t2dataList = list(ser.t2Data)
            t3dataList = list(ser.t3Data)
            pdataList = list(ser.pData)
            edataList = list(ser.eData)

            # Calcular a média móvel se houver pelo menos 100 valores
            moving_avg = pd.Series(pdataList).rolling(window=100).mean().iloc[-1] if len(pdataList) >= 100 else None

            # Verifique se as linhas existem e, caso contrário, crie-as
            if len(self.ax1.lines) == 0:
                # self.ax1.plot(range(len(t1dataList)), t1dataList, label="T1", color='Red')
                self.ax1.plot(range(len(t2dataList)), t2dataList, label="T2", color='Red')
                self.ax1.plot(range(len(t3dataList)), t3dataList, label="T3", color='Orange')
            if len(self.ax2.lines) == 0:
                self.ax2.plot(range(len(pdataList)), pdataList, color='Blue')
                self.ax2.axhline(y=0, color='Red', linestyle='--', label=f"{moving_avg} bar")  # Linha inicial da média móvel
            if len(self.ax3.lines) == 0:
                self.ax3.plot(range(len(edataList)), edataList, color='Green', label='Empuxo')

            # Atualiza apenas os dados do gráfico
            # self.ax1.lines[0].set_data(range(len(t1dataList)), t1dataList)
            self.ax1.lines[0].set_data(range(len(t2dataList)), t2dataList)
            self.ax1.lines[1].set_data(range(len(t3dataList)), t3dataList)
            self.ax2.lines[0].set_data(range(len(pdataList)), pdataList)
            self.ax3.lines[0].set_data(range(len(edataList)), edataList)

            # Atualizar a posição da linha de média móvel
            if moving_avg is not None:
                self.ax2.lines[1].set_ydata([moving_avg] * 2)  # Atualiza a linha horizontal com o novo valor
                self.ax2.lines[1].set_label(f"Média Móvel: {moving_avg:.4f} bar")  # Atualiza o rótulo da linha
            else:
                self.ax2.lines[1].set_ydata([None] * 2)  # Oculta a linha caso não haja média suficiente
                self.ax2.lines[1].set_label("Média Móvel: N/A")  # Define rótulo indicando ausência de média móvel

            # Atualizar limites e títulos, se necessário
            self.getPlotFormat(self.ax1, "Temperatura", min([min(t2dataList),min(t3dataList)]), max([max(t2dataList),max(t3dataList)]), "°C")
            self.getPlotFormat(self.ax2, "Pressão", min(pdataList), max(pdataList), "bar")
            self.getPlotFormat(self.ax3, "Empuxo", min(edataList), max(edataList), "N")
            
    def showAnimation(self, ser):
        ani = animation.FuncAnimation(self.fig, self.animate, frames=30, fargs=(ser,), interval=220)
        plt.tight_layout()
        plt.show()

    def plot_saved_file(self, csv_file):
        # Leitura dos dados do CSV
        data = pd.read_csv(csv_file)

        # Converter a coluna 'Hora' para um formato de tempo
        data['Hora'] = pd.to_datetime(data['Hora'], format="%H:%M:%S.%f")

        # Calcular os Segundos desde a primeira amostra
        data['Segundos'] = (data['Hora'] - data['Hora'].iloc[0]).dt.total_seconds()

        # Dividir todos os valores exceto 'Segundos' por 100
        data['T1'] = data['T1'] / 100
        data['T2'] = data['T2'] / 100
        data['T3'] = data['T3'] / 100
        data['Pressao'] = data['Pressao'] / 100
        data['Empuxo'] = data['Empuxo'] / 100

        # Definindo cores para as linhas
        line_colors = ['blue', 'green', 'red']

        # Criar múltiplas figuras em uma única janela (plt.show() será chamado uma vez no final)
        fig1, ax1 = plt.subplots(figsize=(10, 5))
        fig2, ax2 = plt.subplots(figsize=(10, 5))
        fig3, ax3 = plt.subplots(figsize=(10, 5))

        # 1º Gráfico: T1, T2, T3
        # ax1.plot(data['Segundos'], data['T1'], label='T1', marker='o', color=line_colors[0])
        ax1.plot(data['Segundos'], data['T2'], label='T2', marker='o', color=line_colors[1])
        ax1.plot(data['Segundos'], data['T3'], label='T3', marker='o', color=line_colors[2])
        ax1.set_title("Temperatura x Tempo")
        ax1.set_xlabel("Tempo [s]")
        ax1.set_ylabel("Temperatura [°C]")
        ax1.grid(True, linestyle='-', linewidth=0.5, color='gray')
        ax1.legend(loc='upper right')

        # 2º Gráfico: Pressão
        ax2.plot(data['Segundos'], data['Pressao'], marker='o', color='cyan')
        ax2.set_title("Pressão x Tempo")
        ax2.set_xlabel("Tempo [s]")
        ax2.set_ylabel("Pressão [bar]")
        ax2.grid(True, linestyle='-', linewidth=0.5, color='gray')

        # 3º Gráfico: Empuxo
        ax3.plot(data['Segundos'], data['Empuxo'], marker='o', color='orange')
        ax3.set_title("Empuxo x Tempo")
        ax3.set_xlabel("Tempo [s]")
        ax3.set_ylabel("Empuxo")
        ax3.grid(True, linestyle='-', linewidth=0.5, color='gray')

        # Mostrar todas as figuras ao mesmo tempo
        plt.tight_layout()
        plt.show()

    def getPlotFormat(self, ax, title, min, max, unidades):
        ax.set_ylim([min-5, max+5])  # Limite do eixo Y
        ax.set_xlim([0,300])
        ax.yaxis.set_major_locator(ticker.MultipleLocator(5))  # Intervalo dos ticks no eixo Y
        ax.set_title(f"{title}")  # Título do gráfico
        ax.set_ylabel(f"{unidades}")
        
        # Oculta o eixo X e os números do eixo X
        ax.spines['bottom'].set_visible(False)  # Oculta a linha do eixo X
        ax.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)  # Remove os ticks e os números do eixo X
        
        ax.grid(True)  # Adiciona a grade padrão sem personalização
        
        ax.legend(loc='upper right', frameon=False, fontsize='small', labelcolor='black')  # Legenda fixa no canto superior direito
        
        ax.legend()

    def plot_close(self):
        # Para fechar o gráfico atual
        plt.close()

        # Para fechar um gráfico específico
        plt.close(self.fig)  # onde fig é o objeto da figura que você criou