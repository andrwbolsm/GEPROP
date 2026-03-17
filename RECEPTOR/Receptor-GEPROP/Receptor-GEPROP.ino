#include "SPI.h"
#include "NRFLite.h"

#define PINGREEN 8
#define PINRED A1

const static uint8_t RADIO_ID = 0;      
const static uint8_t DESTINATION_RADIO_ID = 1;
const static uint8_t PIN_RADIO_CE = 9;
const static uint8_t PIN_RADIO_CSN = 10;
uint8_t IGNITE = 1;
uint8_t TESTE = 2;
uint8_t RESET = 3;

int Data[6];
uint8_t command = 0;

struct RadioPacket // Tem que alterar isso aqui para os dados que quero enviar.
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

void setup()
{
    Serial.begin(115200);

    pinMode(PINGREEN, OUTPUT);
    digitalWrite(PINGREEN,HIGH);

    pinMode(PINRED, OUTPUT); 

    if (!_radio.init(RADIO_ID, PIN_RADIO_CE, PIN_RADIO_CSN, NRFLite::BITRATE2MBPS, 90))
    {
        Serial.println("Comunicação com o rádio: ERRO.");
        while (1); // Wait here forever.
    }
    else{
      Serial.println("Comunicação com o rádio: OK.");
    }
}

void loop() {
    while (Serial.available()) {
        command = Serial.read();
        
        if (command == 51) {  // Supondo que 51 é o código de reset
            sendData(3);  // Envia o comando de reset
        } else if (command == 49) {
            sendData(1);  // Envia o comando de ignição
        } else if (command == 50) {
            sendData(2);  // Envia o comando de teste
        }
    }

    if(command == 49 || command == 50){
      listenData();
    }
}


void sendData(uint8_t lei) {
    if (_radio.send(DESTINATION_RADIO_ID, &lei, sizeof(lei))) {  // Envia o comando
        if (lei == 1) {
            Serial.println("Sucesso ao ignitar!");
        }
        else if (lei == 2) {
            Serial.println("Realizando teste.");
        }
        else if (lei == 3) {
            Serial.println("Comando de reset enviado.");
        }
    } else {
        Serial.println("Falha na comunicação.");
    }
}

void listenData(){
    if (_radio.hasData())
    {   
        digitalWrite(PINRED,HIGH);

        _radio.readData(&_radioData); // Note how '&' must be placed in front of the variable name.

        Data[0] = _radioData.T1read;
        Data[1] = _radioData.T2read;
        Data[2] = _radioData.T3read;
        Data[3] = _radioData.Pressure;
        Data[4] = _radioData.Carga;
        Data[5] = _radioData.FailTX;

        

        Serial.print("[");
        for(int i=0;i<=5;i++){
           Serial.print(Data[i]);
           if (i<5){
            Serial.print(",");
            }
        }
        Serial.println("]");
        
    }

    digitalWrite(PINRED,LOW);
}
