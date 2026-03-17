#include "HX711.h"

// HX711 connections
const int LOADCELL_DOUT_PIN = 3;  // DT pin
const int LOADCELL_SCK_PIN = 2;   // SCK pin

HX711 scale;

void setup() {
  Serial.begin(115200);
  scale.begin(LOADCELL_DOUT_PIN, LOADCELL_SCK_PIN);
  Serial.println("HX711 Raw Data Reader");
  Serial.println("No offset or scaling applied");
}

void loop() {
  if (scale.is_ready()) {
    long raw_value = scale.read();  // Get raw ADC value
    Serial.println(raw_value);      // Print raw data
  }
  delay(1000);  // Small delay to avoid flooding Serial Monitor
}
