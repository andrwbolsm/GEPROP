#include "SPI.h"
#include "NRFLite.h"

int command = 0;

const static uint8_t RADIO_ID = 0;       // Our radio's id.  The transmitter will send to this id.
const static uint8_t DESTINATION_RADIO_ID = 1;
const static uint8_t PIN_RADIO_CE = 9;
const static uint8_t PIN_RADIO_CSN = 10;

int Data[6] = {0, 0, 0, 0, 0, 0};

struct RadioPacket
{
    uint8_t FromRadioId;
    uint8_t IGNITE;
    uint32_t T1read;
    uint32_t T2read;
    uint32_t T3read;
    uint32_t Pressure;
    uint32_t Carga;
    uint32_t FailedTxCount;
};

NRFLite _radio;
RadioPacket _radioData;

void setup()
{
    Serial.begin(115200);
    
    if (!_radio.init(RADIO_ID, PIN_RADIO_CE, PIN_RADIO_CSN, NRFLite::BITRATE2MBPS, 120))
    {
        Serial.println("Cannot communicate with radio");
        while (1); // Wait here forever.
    }
}

void loop()
{
  while(Serial.available()){
    command = Serial.read();
  }

  if (command > 0){
    _radioData.IGNITE = 1;
    sendData();
  }
}


void sendData(){
    if (_radio.send(DESTINATION_RADIO_ID, &_radioData, sizeof(_radioData))) // Note how '&' must be placed in front of the variable name.
    {   
        Serial.println("Sucesso ao ignitar!");
        while(1){
          listenData();}
    }
    else
    {
        Serial.println("Falha ao ignitar.");
        _radioData.FailedTxCount++;
    }

}

void listenData(){
    while (_radio.hasData())
    {   
        _radio.readData(&_radioData); // Note how '&' must be placed in front of the variable name.

        Data[0] = _radioData.T1read;
        Data[1] = _radioData.T2read;
        Data[2] = _radioData.T3read;
        Data[3] = _radioData.Pressure;
        Data[4] = _radioData.Carga;
        Data[5] = _radioData.FailedTxCount;

        Serial.print("[");
        for(int i=0;i<=5;i++){
           Serial.print(Data[i]);
           if (i<5){
            Serial.print(",");
            }
        }
        Serial.println("]");
        
    }
}