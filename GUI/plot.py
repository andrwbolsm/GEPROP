import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.ticker as ticker
from datetime import datetime  # Importa o módulo para trabalhar com datas e horas

class AnimationPlot:
    def __init__(self, port, update_log=None):
        self.file_initialized = False  # Flag to track if the CSV file header is written
        self.fig = plt.figure(facecolor='black')  # Set figure background to black
        self.ax = self.fig.add_subplot(111)
        self.dataList = []
        self.port = port
        self.update_log = update_log  # Store the update_log function

    def animate(self, i, dataList, ser, csv_writer):
        arduinoData_string = ser.readline().decode('ascii').strip()  # Decode and strip newline characters
        try:
            arduinoData_float = float(arduinoData_string)  # Convert to float
            # Get current timestamp
            timestamp = datetime.now().strftime("%H:%M:%S")  # Format timestamp as "HH:MM:SS"

            self.dataList.append(arduinoData_float)  # Add to the list holding the fixed number of points to animate

            if csv_writer is not None:
                if not self.file_initialized:
                    csv_writer.writerow(["", "Value"])  # Write header to CSV file
                    self.file_initialized = True
                csv_writer.writerow([timestamp, arduinoData_float])  # Append timestamp and data to the CSV file

            # Update log with the new data
            if self.update_log:
                self.update_log(f"{timestamp} -> Data: {arduinoData_float}")

        except ValueError:  # Handle the exception if the data is not a valid float
            pass

        dataList = dataList[-50:]   # Fix the list size so that the animation plot 'window' is x number of points
        
        self.ax.clear() # Clear last data frame
        
        self.getPlotFormat()
        self.ax.plot(dataList,color='cyan')  # Plot new data frame with white color
    
    def showAnimation(self,ser,csv_writer):
        ani = animation.FuncAnimation(self.fig, self.animate, frames=60, fargs=(self.dataList, ser, csv_writer), interval=220) 
        plt.show()

    def plot_saved_file(self,x,y):
        # Plotting CSV data
        plt.figure(figsize=(10, 5), facecolor='black')  # Set figure background to black
        ax = plt.gca()  # Get current axis
        ax.plot(x, y, marker='o', color='cyan')  # Plot data with cyan color
        ax.set_title("Dados do CSV", color='white')  # Set title with white color
        ax.set_xlabel("Número da Amostra", color='white')  # Set x-axis label with white color
        ax.set_ylabel("Valor", color='white')  # Set y-axis label with white color
        ax.set_facecolor('black')  # Set background of the plot area to black
        ax.spines['left'].set_color('white')  # Set y-axis line color to white
        ax.spines['bottom'].set_color('white')  # Set x-axis line color to white
        ax.tick_params(axis='y', colors='white')  # Set y-axis tick color to white
        ax.tick_params(axis='x', colors='white')  # Set x-axis tick color to white
        
        # Adicionar grid fino com cor roxa
        ax.grid(True, linestyle='-', linewidth=0.5, color='purple')  # Define grid as visible, solid style, thin line, purple color
        ax.spines['bottom'].set_visible(True)  # Ensure the bottom spine is visible
        ax.tick_params(axis='x', which='both', bottom=True, top=False)  # Ensure x-axis ticks are visible
        ax.xaxis.label.set_visible(True)  # Ensure x-axis label is visible

        plt.show()

    def getPlotFormat(self):
        self.ax.set_ylim([0, 50])                                  # Set Y axis limit of plot
        self.ax.yaxis.set_major_locator(ticker.MultipleLocator(2.5)) # Define espaçamento de 5 unidades entre os ticks
        self.ax.set_title(f"Arduino Data from {self.port}", color='white')           # Set title of figure with white color
        self.ax.set_ylabel("Value", color='white')                 # Set title of y axis with white color
        self.ax.set_facecolor('black')                             # Set background of the plot area to black
        # self.ax.spines['bottom'].set_color('white')                # Set x-axis line color
        self.ax.spines['left'].set_color('white')                  # Set y-axis line color
        # self.ax.tick_params(axis='x', colors='white')              # Set x-axis tick color
        self.ax.tick_params(axis='y', colors='white')              # Set y-axis tick color

        # Adicionar grid fino com cor roxa
        self.ax.grid(True, linestyle='-', linewidth=0.5, color='purple')  # Define grid como visível, estilo sólido, linha fina e cor roxa
        # Remover eixo x para melhor perfomance
        self.ax.spines['bottom'].set_visible(False)                # Ocultar a linha do eixo x
        self.ax.tick_params(axis='x', which='both', bottom=False, top=False)  # Remover ticks do eixo x
        self.ax.xaxis.label.set_visible(False)                     # Ocultar label do eixo x
