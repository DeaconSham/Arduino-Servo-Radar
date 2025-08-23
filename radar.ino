#include <Servo.h>
#include <LiquidCrystal.h>

LiquidCrystal lcd(12, 11, 5, 4, 3, 2); //initialize the LiquidCrystal library with the numbers of the interface pins
Servo myServo; //servo object

//pins for the ultrasonic sensor
const int echoPin = 6;
const int triggerPin = 7;

//global variables for the sensor reading
long duration;
int distance;

// Define radar parameters
const int MIN_DIST = 5; //closer than this is max strength
const int MAX_DIST = 60; //further is out of range

//custom char for the bar segment
byte barSegment[8] = {
  B11111,
  B11111,
  B11111,
  B11111,
  B11111,
  B11111,
  B11111,
  B11111
};

void setup() {
  Serial.begin(9600); //start serial communication at baud rate of 9600
  lcd.begin(16, 2); //setup the lcd number of col and rows
  lcd.createChar(0, barSegment); //create the custom characters for the strength bar
  myServo.attach(9); //attach servo on pin 9
  pinMode(triggerPin, OUTPUT); //ultrasonic sensor trig pin 7
  pinMode(echoPin, INPUT);

  //to print startup message
  lcd.print("Radar System");
  lcd.setCursor(0,1);
  lcd.print("Initializing...");
  delay(2000);
  lcd.clear();
}

void loop() {
  //sweep servo from 0 to 180 degrees
  for (int i = 0; i <= 180; i += 1) { 
    myServo.write(i);
    distance = measureDistance();
    updateLcdDisplay(i, distance); //send angle and distance to lcd function
    sendData(i, distance); //send the data to the serial port
    delay(20); 
  }

  //sweep servo from 180 to 0 degrees
  for (int i = 180; i >= 0; i -= 1) { 
    myServo.write(i);
    distance = measureDistance();
    updateLcdDisplay(i, distance);
    sendData(i, distance);
    delay(20);
  }
}

//function to perform a distance measurement and return the value.
int measureDistance() {
  digitalWrite(triggerPin, LOW);
  delayMicroseconds(2);
  digitalWrite(triggerPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(triggerPin, LOW);
  duration = pulseIn(echoPin, HIGH); 
  return duration * 0.034 / 2;
}

//function updates the lcd display
void updateLcdDisplay(int angle, int dist) {
  int segments = 0;
  if (dist > 0 && dist < MAX_DIST) {
    segments = map(dist, MIN_DIST, MAX_DIST, 16, 1);
  }
  
  lcd.setCursor(0, 0);
  for (int i = 0; i < 16; i++) {
    if (i < segments) {
      lcd.write(byte(0)); //print a bar segment
    } else {
      lcd.print(" "); //print a space to clear the rest of the bar
    }
  }

  lcd.setCursor(0, 1);
  char displayString[17]; //character array to hold the formatted text
    sprintf(displayString, "A:%-3d   D:%-4dcm", angle, dist); 
  
  lcd.print(displayString);
}


//function to send data over serial for radar software
void sendData(int angle, int dist) {
  //send angle and distance over serial
  Serial.print(angle);
  Serial.print(",");
  Serial.println(dist);
}