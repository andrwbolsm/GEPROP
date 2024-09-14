#include "SPI.h"
#include "NRFLite.h"
#include "max6675.h"

// *** Inicialização do TRANSDUTOR DE PRESSÃO ***
// Configura a porta A7 como entrada analógica
const int analogPin = A7;
const float Vref = 5.0;        // Tensão de referência
const float minCurrent = 4.0;  // Corrente mínima em mA (corresponde a 0 bar)
const float maxCurrent = 20.0; // Corrente máxima em mA (corresponde a 100 bar)
const float minPressure = 0.0; // Pressão mínima em bar
const float maxPressure = 100.0; // Pressão máxima em bar

// *** Inicialização dos TERMOPARES ***
int t1Pins[3] = {47, 45, 43}; //DO, DS, CLK
int t2Pins[3] = {41, 39, 37}; //DO, DS, CLK
int t3Pins[3] = {35, 33, 31}; //DO, DS, CLK

MAX6675 T1(t1Pins[0], t1Pins[1], t1Pins[2]);
MAX6675 T2(t2Pins[0], t2Pins[1], t2Pins[2]);
MAX6675 T3(t3Pins[0], t3Pins[1], t3Pins[2]);

// *** *** *** *** *** *** *** *** *** ***

// *** Inicialização do RÁDIO ***
const static uint8_t RADIO_ID = 1;             // ID deste rádio.
const static uint8_t DESTINATION_RADIO_ID = 0; // ID do rádio receptor.
const static uint8_t PIN_RADIO_CE = 49;
const static uint8_t PIN_RADIO_CSN = 53;

struct RadioPacket // Tem que alterar isso aqui para os dados que quero enviar.
{
    uint8_t FromRadioId;
    uint32_t T1read;
    uint32_t T2read;
    uint32_t T3read;
    uint32_t Pressure;
    uint32_t FailedTxCount;
};

NRFLite _radio;
RadioPacket _radioData;

// *** *** *** *** *** *** *** *** *** ***

void setup()
{
    Serial.begin(115200);

    // Configuração do RÁDIO

    // By default, 'init' configures the radio to use a 2MBPS bitrate on channel 100 (channels 0-125 are valid).
    // Both the RX and TX radios must have the same bitrate and channel to communicate with each other.
    // You can run the 'ChannelScanner' example to help select the best channel for your environment.
    // You can assign a different bitrate and channel as shown below.
    //   _radio.init(RADIO_ID, PIN_RADIO_CE, PIN_RADIO_CSN, NRFLite::BITRATE2MBPS, 100) // THE DEFAULT
    //   _radio.init(RADIO_ID, PIN_RADIO_CE, PIN_RADIO_CSN, NRFLite::BITRATE1MBPS, 75)
    //   _radio.init(RADIO_ID, PIN_RADIO_CE, PIN_RADIO_CSN, NRFLite::BITRATE250KBPS, 0)

    if (!_radio.init(RADIO_ID, PIN_RADIO_CE, PIN_RADIO_CSN))
    {
        Serial.println("Não é possível comunicar-se com o rádio.");
        while (1); // Wait here forever.
    }
    
    // _radio.init(RADIO_ID, PIN_RADIO_CE, PIN_RADIO_CSN);
    _radioData.FromRadioId = RADIO_ID;
    
    // Fim da configuração do RÁDIO

    delay(1000); // Espera para estabilizar o circuito.
}

void loop()
{
      // Lê o valor do pino analógico
    int sensorValue = analogRead(analogPin);

    // Converte o valor lido em tensão
    float voltage = sensorValue * (Vref / 1023.0);

    // Converte a corrente para pressão (bar)
    float pressure_bar = -1.13 + 51.1*voltage - 122*voltage*voltage + 280*(voltage*voltage*voltage);

    if (pressure_bar < 0.0){
      pressure_bar = 0.0;
    }

    // Imprime a pressão correspondente no monitor serial
    Serial.print("Pressão: ");
    Serial.print(pressure_bar);
    Serial.println(" bar");

    _radioData.T1read = T1.readCelsius();
    _radioData.T2read = T2.readCelsius();
    _radioData.T3read = T3.readCelsius();
    _radioData.Pressure = pressure_bar;

    Serial.println("Sending: ");
    Serial.print("[T1,T2,T3] = ");
    Serial.print(_radioData.T1read);
    Serial.print(", ");
    Serial.print(_radioData.T2read);
    Serial.print(", ");
    Serial.println(_radioData.T3read);

    Serial.print("Pressure: ");
    Serial.println(_radioData.Pressure);

    Serial.print("Status");
    
    if (_radio.send(DESTINATION_RADIO_ID, &_radioData, sizeof(_radioData))) // Note how '&' must be placed in front of the variable name.
    {   
        Serial.println("Success");
    }
    else
    {
        Serial.println("Failed");
        _radioData.FailedTxCount++;
    }

    delay(220); // Esse é o delay mínimo para que o termopar possa operar.
}
