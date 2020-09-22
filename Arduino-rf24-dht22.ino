/*  1111 - The Arduino Node Sketch
 *  From Raspberry Pi Full Stack Raspbian
 *  https://app.techexplorations.com/courses/raspberry-pi-full-stack-raspbian/ 
 * 
 *  This sketch allows an Arduino to transmit DHT22 data to the Raspberry Pi
 *  base node, using the nRF24 transceiver.
 *  The sketch places the Arduino in low-power mode when it is not doing 
 *  useful work.
 * 
 * 
 * Components
 * ----------
 *  - Arduino Uno
 *  - nRF24 transciever
 *  - a 22uF or similar bypass capacitor
 *  - A DHT22 sensor
 *  - A 10KOhm pull up resistor for the sensor
 *  - 
 *  - 
 *  
 *  Libraries
 *  ---------
 *  - RF24Network.h
 *  - RF24.h
 *  - DHT.h
 *  - LowPower.h
 *
 * Connections
 * -----------
 *  
 * Refer to lecture 1110.
 *  
 * Created on March 6 2020 by Peter Dalmaris
 * 
 */

#include "LowPower.h"
#include <RF24Network.h>
#include <RF24.h>
#include <DHT.h>

// The DHT data line is connected to pin 2 on the Arduino
#define DHTPIN 2

#define DHTPIN_POWER 5

// Leave as is if you're using the DHT22. Change if not.
//#define DHTTYPE DHT11   // DHT 11 
#define DHTTYPE DHT22     // DHT 22  (AM2302)
//#define DHTTYPE DHT21   // DHT 21 (AM2301)

DHT dht(DHTPIN, DHTTYPE);

// Radio with CE & CSN connected to 9 & 10
RF24 radio(9, 10);
RF24Network network(radio);

// Constants that identify this node and the node to send data to
const uint16_t this_node = 3;
const uint16_t parent_node = 0;

// The network header initialized for this node
RF24NetworkHeader header(parent_node);

void send_data() {

    digitalWrite(LED_BUILTIN, HIGH);
    digitalWrite(DHTPIN_POWER, HIGH); // Turn on the sensor
    
    delay(2000); // Wait for the sensor and RF22 to power up.
    data_tx();
    delay(10);
    digitalWrite(DHTPIN_POWER, LOW); // Turn off the sensor
    digitalWrite(LED_BUILTIN, LOW);
}

void setup(void)
{
  
  // Initialize all radio related modules
  SPI.begin();
  radio.begin();
  delay(5);
  network.begin(90, this_node); // In this example, we use channel "90". All members of
                                // the same netowork must use the same channel.

  pinMode(DHTPIN_POWER, OUTPUT); 
  
  // Use the internal pull up for the DHT
  pinMode(DHTPIN, INPUT);           
  digitalWrite(DHTPIN, HIGH);

  // Initialize the DHT library
  dht.begin();

  // Set up the Serial Monitor
  Serial.begin(9600);
  Serial.println("Starting");
  pinMode(LED_BUILTIN, OUTPUT);

}

void loop() {
  LowPower.idle(SLEEP_8S, ADC_OFF, TIMER2_OFF, TIMER1_OFF, TIMER0_OFF, 
                SPI_OFF, USART0_OFF, TWI_OFF);

  digitalWrite(LED_BUILTIN, HIGH);
  digitalWrite(DHTPIN_POWER, HIGH); // Turn on the sensor
    
  delay(2000); // Wait for the sensor and RF22 to power up.
  data_tx();
  delay(10);
  digitalWrite(DHTPIN_POWER, LOW); // Turn off the sensor
  digitalWrite(LED_BUILTIN, LOW);
}

void data_tx()
{
    // Update network data
  network.update();

  // Read humidity (percent)
  float h = dht.readHumidity();
  // Read temperature as Celsius
  float t = dht.readTemperature();
  // Read temperature as Fahrenheit
  float f = dht.readTemperature(true);

  String values_string = "";
  values_string        += String(h);
  values_string        += ",";
  values_string        += String(t);
  
  // Headers will always be Temperature for this node
  // We set it again each loop iteration because fragmentation of the messages might change this between loops
  header.type = 't';
  char payload[12];  //Give this char array enough space to accomodate the two float values converted to string
  values_string.toCharArray(payload,sizeof(payload));

  // Writing the message to the network means sending it
  if (network.write(header, payload, sizeof(payload))) {     //if (network.write(header, &message, sizeof(message))) {
    Serial.print("Message sent\n"); 
  } else {
    Serial.print("Could not send message\n"); 
  }

  network.update();
}
