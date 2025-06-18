#include <Keypad.h>
#include <Adafruit_LiquidCrystal.h>
#include <Servo.h>

int temp = 0;
int target = 0;
bool state = 0;
bool prev = 0;
int reset = 0;
int master = 0;
Servo servo_11;
Adafruit_LiquidCrystal lcd_1(0);
const byte rows = 4;
const byte cols = 3;
char keys[rows][cols] = {
	{'1','2','3'},
	{'4','5','6'},
	{'7','8','9'},
	{'*','0','#'}
};
byte rowPins[rows] = {8, 7, 6, 5};
byte colPins[cols] = {4, 3, 2};
Keypad keypad = Keypad( makeKeymap(keys), rowPins, colPins, rows, cols );

void input()
{
  	lcd_1.clear();
  	target = 0;
  	char key;
	while(key != '#')
    {
    	key = keypad.getKey();
     	if (key == '*')
        {
        	target /= 10;
         	lcd_1.clear();
			lcd_1.print(target);
        }	
		else if (key != NO_KEY && key != '#')
        {
			target *= 10;
        	target += int(key) - 48;
          	if(target > 40)
            {
        		target = 0;
              	lcd_1.clear();
              	digitalWrite(9, HIGH);
              	lcd_1.print("input <= 40");
              	delay(2000);
              	digitalWrite(9, LOW);
              	lcd_1.clear();
            }
          	lcd_1.setCursor(0,0);
			lcd_1.print(target);
		}
    	delay(10);
    }
}

void setup()
{
  	servo_11.attach(11, 500, 2500);
  	servo_11.write(0);
	pinMode(A0, INPUT);
  	pinMode(A1, INPUT);
  	pinMode(12, INPUT);
  	pinMode(LED_BUILTIN, OUTPUT);
  	pinMode(9, OUTPUT);
  	pinMode(10, OUTPUT);
	lcd_1.begin(16, 2);
	Serial.begin(9600);
  	input();
}

void loop()
{
  	master = (analogRead(A1) - 1013) / 10 ;
  	if(master == 1)
    {
      	int read = analogRead(A0);
  		reset = digitalRead(12);
    	if(reset == HIGH)
    	{
    	  	digitalWrite(10, LOW);
    	  	servo_11.write(0);
    	  	input();
          	prev = false;
    	}
		temp = map(((read - 20) * 3.04), 0, 1023, -40, 125);
  		if(temp <= target - 3)
    	{
      		state = true;
	    }
	  	else if (temp >= target)
	    {
	      	state = false;
	    }
	  	lcd_1.setCursor(0,1);
	  	if(state == true)
	    {	
          	if(prev == false)
            {
              	servo_11.write(90);
          		delay(1000);
              	digitalWrite(10, HIGH);
              	delay(500);
              	digitalWrite(10, LOW);
            }
	      	lcd_1.setBacklight(1);
			lcd_1.print(temp);
	      	lcd_1.print(" heating on            ");
	      	digitalWrite(LED_BUILTIN, HIGH);
	    }
	  	else
	    {
          	if(prev==true)
          		servo_11.write(0);
	      	lcd_1.setBacklight(1);
	      	lcd_1.print(temp);
	      	lcd_1.print(" heating off          ");
	      	digitalWrite(LED_BUILTIN, HIGH);
	    }
      	prev = state;
    }
  	else
	{
      	digitalWrite(10, LOW);
      	if(prev==true)
    		servo_11.write(0);
      	lcd_1.setCursor(0,1);
      	lcd_1.setBacklight(0);
      	lcd_1.print("power off             ");
      	digitalWrite(LED_BUILTIN, LOW);
      	prev = false;
    }
	delay(100);
}