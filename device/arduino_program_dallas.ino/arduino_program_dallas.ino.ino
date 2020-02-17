#define tempPin A2
#define ledPin 13
int val = 0;
float temp = 0;
int ledState = 0;

void setup()
{
  Serial.begin(9600);
  pinMode(ledPin, OUTPUT);
}
void loop()
{
  val = analogRead(tempPin);
  temp = (val/1024.0)*500;
  ledState = digitalRead(ledPin);
  
  Serial.print("temp=");
  Serial.print(temp);
  Serial.print(":ledState=");
  Serial.print(ledState);
  Serial.print(";");
  Serial.println();
  
  serialEvent();

  delay(100);
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
     if (strcmp("LED ON", cmdBuffer) == 0)
     {
        digitalWrite(ledPin,HIGH);
     }
     else if (strcmp("LED OFF", cmdBuffer) == 0)
     {
        digitalWrite(ledPin,LOW);
     }
     cmdBuffer[0] = 0;
   }
 }
}

char processCharInput(char* cmdBuffer, const char c)
{
 
 if (c >= 32 && c <= 126)
 {
   if (strlen(cmdBuffer) < USB_EP_SIZE)
   {
     strncat(cmdBuffer, &c, 1);
   }
   else  
   {  
     return '\n';
   }
 }
 else if ((c == 8 || c == 127) && cmdBuffer[0] != 0)
 {

   cmdBuffer[strlen(cmdBuffer)-1] = 0;
 }

 return c;
}
