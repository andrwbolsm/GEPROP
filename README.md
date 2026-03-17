## About
 
This project covers the design of the data acquisition (DAQ) electronics board and its associated software for a rocket engine static fire test stand. During a test, the system collects **temperature**, **pressure**, and **thrust** data in real time and transmits it wirelessly over long range to a graphical user interface (GUI) for remote monitoring.

## System Overview
 
```
[ Test Stand ]                              [ Operator Station ]
  Sensors (T, P, F)
       │
  DAQ Board                ── RF Link ──►   GUI (live plots)
  (signal conditioning,
   ADC, microcontroller)
```
 
| Measured quantity | Sensor type |
|---|---|
| Temperature | Thermocouple / RTD |
| Pressure | Pressure transducer |
| Thrust (force) | Load cell |
 
---
 
## Features
 
- Multi-channel sensor acquisition (temperature, pressure, thrust)
- Long-range wireless data transmission
- Real-time graphical interface for test monitoring
- Designed for safe stand-off operation during live engine tests
 
---
