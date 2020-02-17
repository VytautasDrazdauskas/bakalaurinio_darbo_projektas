#include <max6675.h>

#define tempPin A2
#define actuatorPin1 5
#define actuatorPin2 7 
#define actuatorPin3 6  
#define ktcSO 8
#define ktcCS 9
#define ktcCLK 10

float temp = 0;
int act1 = 0;
int act2 = 0;
int act3 = 0;

MAX6675 ktc(ktcCLK, ktcCS, ktcSO);

void setup()
{
  Serial.begin(9600);
  pinMode(actuatorPin1, OUTPUT);
  pinMode(actuatorPin2, OUTPUT);
  pinMode(actuatorPin3, OUTPUT);
  delay(500);
}
void loop()
{
  temp = ktc.readCelsius();
  act1 = digitalRead(actuatorPin1);
  act2 = digitalRead(actuatorPin2);
  act3 = digitalRead(actuatorPin3);

  Serial.print("temp=");
  Serial.print(temp);
  Serial.print(":act1=");
  Serial.print(act1);
  Serial.print(":act2=");
  Serial.print(act2);
  Serial.print(":act3=");
  Serial.print(act3);
  Serial.print(";");
  Serial.println();
  
  serialEvent();

  delay(300);
}



void serialEvent()
{
 static char cmdBuffer[USB_EP_SIZE] = "";
 char c;
 while(Serial.available())
 {
   c = processCharInput(cmdBuffer, Serial.read());
   
   if (c == '\n')
   {    
     if (strcmp("ACT1 ON", cmdBuffer) == 0)
     {
        digitalWrite(actuatorPin1,HIGH);
     }
     else if (strcmp("ACT1 OFF", cmdBuffer) == 0)
     {
        digitalWrite(actuatorPin1,LOW);
     }
     else if (strcmp("ACT2 ON", cmdBuffer) == 0)
     {
        digitalWrite(actuatorPin2,HIGH);
     }
     else if (strcmp("ACT2 OFF", cmdBuffer) == 0)
     {
        digitalWrite(actuatorPin2,LOW);
     }
     else if (strcmp("ACT3 ON", cmdBuffer) == 0)
     {
        digitalWrite(actuatorPin3,HIGH);
     }
     else if (strcmp("ACT3 OFF", cmdBuffer) == 0)
     {
        digitalWrite(actuatorPin3,LOW);
     }
     cmdBuffer[0] = 0;
   }
 }
}

char processCharInput(char* cmdBuffer, const char c)
{
 //Store the character in the input buffer
 if (c >= 32 && c <= 126) //Ignore control characters and special ascii characters
 {
   if (strlen(cmdBuffer) < USB_EP_SIZE)
   {
     strncat(cmdBuffer, &c, 1);   //Add it to the buffer
   }
   else  
   {  
     return '\n';
   }
 }
 else if ((c == 8 || c == 127) && cmdBuffer[0] != 0) //Backspace
 {

   cmdBuffer[strlen(cmdBuffer)-1] = 0;
 }

 return c;
}
