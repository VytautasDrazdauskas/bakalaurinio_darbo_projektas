#define tempPin A2
#define ledPin 8 

void setup()
{
  Serial.begin(9600);
  pinMode(ledPin, OUTPUT);
}
void loop()
{
  int val = analogRead(tempPin);
  float mv = ( val/1024.0)*500;
  float cel = mv;
  bool ledState = digitalRead(ledPin);
   
  Serial.print("t=" + (String)cel + ";");
  Serial.print("val=" + (String)val + ";");
  Serial.print("ledState=" + String(ledState) + ";");
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
     if (strcmp("ON", cmdBuffer) == 0)
     {
        digitalWrite(ledPin,HIGH);
     }
     else if (strcmp("OFF", cmdBuffer) == 0)
     {
        digitalWrite(ledPin,LOW);
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
