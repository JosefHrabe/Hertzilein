
#include <Firmata.h>

int  x=0;
unsigned long sampleTimer = 0;
unsigned long sampleInterval = 2600; //100 us = 100Hz rate

void setup()
{
  Firmata.setFirmwareVersion(FIRMATA_FIRMWARE_MAJOR_VERSION, FIRMATA_FIRMWARE_MINOR_VERSION);
  Firmata.begin(57600);
  delay(3000);
}


void loop() {
  unsigned long currMicros = micros();
  if (currMicros - sampleTimer >= sampleInterval) // is it time for a sample?
  {
    sampleTimer = currMicros;
    x = analogRead(0);
    sendToPC(&x);
    //sendToPC_ul( &sampleTimer );
  }
}

void sendToPC( int  *x)//(float* data1 )
{
  char result[16];
  itoa( *x, result, 10);
  Firmata.sendString(result);
}
void sendToPC_ul( unsigned long  *x)//(float* data1 )
{
  char result[16];
  itoa( *x, result, 10);
  Firmata.sendString(result);
}
