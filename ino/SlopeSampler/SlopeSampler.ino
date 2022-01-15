
#include <Firmata.h>

int  y=0;
int  yMin=20000;
int  yMax=-20000;
unsigned long currMicros=0;
unsigned long lastMicros=0;
unsigned long delta=0;
unsigned long minMaxCount=0;
unsigned long period=0;
bool slopeDirection=true;
unsigned int slopeCount=0;

int thrRising  = 500;
int thrFalling = 300;
unsigned int ignorePeriods=4;
char wave = 't';


void setup()
{
  Firmata.setFirmwareVersion(FIRMATA_FIRMWARE_MAJOR_VERSION, FIRMATA_FIRMWARE_MINOR_VERSION);
  Firmata.begin(57600);
  delay(3000);

  pinMode(13, OUTPUT);

}


bool isRising( )
{
  if( ( y > thrRising ) && ( slopeDirection == false ) )
  {
    return true;
  }
  return false;
}

bool isFalling( )
{
  if( ( y < thrFalling ) && ( slopeDirection == true ) )
  {
    return true;
  }
  return false;
}

void loop() {
  
  y = analogRead(0);

  if( yMax < y )
    yMax=y;
  if( yMin > y )
    yMin=y;


  if( isFalling())
      slopeDirection= !slopeDirection;
  
  if ( isRising() )
  {
    currMicros =micros();
    period = currMicros-lastMicros;
    slopeDirection= !slopeDirection;
    lastMicros=currMicros;    

    if( ignorePeriods == 0 )
      sendToPC_ul( &period , 'x' );
      else 
      ignorePeriods-=1;

    minMaxCount+=1;

    if( minMaxCount > 50 )
    {
      minMaxCount=0;
      sendToPC( &yMin , 'y');
      sendToPC( &yMax , 'Y');
      yMin=20000;
      yMax=-20000;
    }
  }

  if( slopeDirection )
    digitalWrite(13, HIGH);
  else
    digitalWrite(13, LOW);
}

void sendToPC( int  *x , char prefix )//(float* data1 )
{
  char result[16];
  result[0]=prefix;
  itoa( *x, &result[1], 10);
  Firmata.sendString(result);
}
void sendToPC_ul( unsigned long  *x , char prefix)//(float* data1 )
{
  char result[16];
  result[0]=prefix;
  itoa( *x, &result[1], 10);
  Firmata.sendString(result);
}
