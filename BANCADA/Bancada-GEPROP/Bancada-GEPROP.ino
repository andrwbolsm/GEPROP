#include <SPI.h>
#include <NRFLite.h>
#include <max6675.h>
#include <HX711.h>
#include <EEPROM.h>

#define RELE 13 // Pino digital do relé
#define pinDT  3 // DT da célula de carga
#define pinSCK  2 // SCK da célula de carga
#define ledPin 8 // Pino digital do LED do rádio
#define CHANNEL 90 // Canal de comunicação do rádio
#define LOAD_OFFSET -79917.5319 // Ofsset da célula de carga
#define LOAD_SCALE -60.2597 // Escala da célula de carga
#define FREQUENCY_SAMPLING 10 // Frequência de amostragem

const unsigned long sampling = 1000/FREQUENCY_SAMPLING; // Transformando frequência para período de amostragme

float pressure_bar = 0.0; // Variável para armazenar valores de pressão medidas em bar
float carga = 0; // Variável para armazenar valores de empuxo

uint8_t COMMAND = 0; // 0 para não ignição, 1 para ignitar, 2 para teste. Esse valor só será alterado via telecomando

// *** Inicialização da CÉLULA DE CARGA ***
HX711 scale; // Inicializa o módulo da célula de carga

// *** Inicialização do TRANSDUTOR DE PRESSÃO ***
// Configura a porta A7 como entrada analógica
const int analogPin = A7;
const float VREF = 5.0;        // Tensão de referência
const int ADC_RES = 1023;      // Resolução do ADC (10 bits no Arduino Mega)

// *** Inicialização dos TERMOPARES ***
int t1Pins[3] = {47, 45, 43}; //DO, DS, CLK
int t2Pins[3] = {41, 39, 37}; //DO, DS, CLK
int t3Pins[3] = {35, 33, 31}; //DO, DS, CLK
static unsigned long lastTemperatureUpdate = 0; // Armazena o tempo do último update das temperaturas
static unsigned long lastUpdateTime = 0;

MAX6675 T1(t1Pins[0], t1Pins[1], t1Pins[2]);
MAX6675 T2(t2Pins[0], t2Pins[1], t2Pins[2]);
MAX6675 T3(t3Pins[0], t3Pins[1], t3Pins[2]);

// *** *** *** *** *** *** *** *** *** ***

// *** Inicialização do RÁDIO ***
const static uint8_t RADIO_ID = 1;             // ID deste rádio.
const static uint8_t DESTINATION_RADIO_ID = 0; // Id of the radio we will transmit to.
const static uint8_t PIN_RADIO_CE = 49;
const static uint8_t PIN_RADIO_CSN = 53;

struct RadioPacket
{
    uint32_t FailTX;
    uint32_t T1read;
    uint32_t T2read;
    uint32_t T3read;
    uint32_t Pressure;
    uint32_t Carga;
};

NRFLite _radio;
RadioPacket _radioData;

// *** *** *** *** *** *** *** *** *** ***

void setup()
{
    Serial.begin(115200);

    pinMode(ledPin, OUTPUT);

    pinMode(RELE,OUTPUT);
    digitalWrite(RELE,HIGH);

    // Configuração do RÁDIO

    if (!_radio.init(RADIO_ID, PIN_RADIO_CE, PIN_RADIO_CSN, NRFLite::BITRATE2MBPS, CHANNEL))
    {
        Serial.println("Comunicação com o rádio: ERRO.");
        
        while (1){
          // Pisca o LED em caso de erro na comunicação Arduino-rádio
          digitalWrite(ledPin, HIGH);
          delay(1000);
          
          digitalWrite(ledPin, LOW);
          delay(1000);
        }

    }

    else{
      Serial.println("Comunicação com o rádio: OK.");
    }
    
    // Fim da configuração do RÁDIO

    _radioData.FailTX = 0;

    // Configuração da Célula de Carga
    scale.begin(pinDT, pinSCK);
    scale.set_offset(LOAD_OFFSET);
    scale.set_scale(LOAD_SCALE);
}

void loop() {
    unsigned long currentMillis_program = millis(); 

    // Verifica se há novos dados do rádio
    if (_radio.hasData()) {
        _radio.readData(&COMMAND); // Atualiza o comando com a nova mensagem recebida

        Serial.println("Comando recebido!");

        if (COMMAND == 1) {
            digitalWrite(RELE, LOW); // Ativa o relé
        } else if (COMMAND == 3) {
            digitalWrite(RELE, HIGH); // Desativa o relé
            _radioData.FailTX = 0;
        }
    }

    // Envia mensagens continuamente se COMMAND for 1 ou 2
    if (COMMAND == 1 || COMMAND == 2) {
        sendData();
    }

    
}

void sendData(){
  unsigned long currentMillis = millis(); 

  // Atualiza os dados de pressão e empuxo a 100 Hz
  if(currentMillis - lastUpdateTime >= sampling){
    _radioData.Pressure = get_pressure()*100;
    _radioData.Carga = get_load()*100;
    lastUpdateTime = currentMillis; // Atualiza o tempo do último envio
  }

  // Atualiza os dados de temperatura apenas a cada 220 ms
  if (currentMillis - lastTemperatureUpdate >= 220) {
      _radioData.T1read = T1.readCelsius() * 100;
      _radioData.T2read = T2.readCelsius() * 100;
      _radioData.T3read = T3.readCelsius() * 100;
      lastTemperatureUpdate = currentMillis; // Atualiza o tempo do último envio
  }

  if (_radio.send(DESTINATION_RADIO_ID, &_radioData, sizeof(_radioData)))
  {   
    digitalWrite(ledPin, HIGH);
  }
  else{
    digitalWrite(ledPin, LOW);
    _radioData.FailTX += 1;
    Serial.println(_radioData.FailTX);
  }
}

float get_load(){
  float returning_load = scale.get_units();

  if(returning_load < 0){
    returning_load = 0.0;
  }

  return returning_load;
}
  
float get_pressure() {
    // Lê o valor analógico
    int sensorValue = analogRead(analogPin);
    
    // Converte o valor analógico para tensão (0 a VREF)
    float voltage = (sensorValue * VREF) / ADC_RES;
    
    return voltage*22.5; // Retorna a pressão em bar
}
