/*
 * Pin layout:
 * ----------|------------|-------------|--------------------------------------------|
 *           |  Arduino   |   ESP32     |                 DESCRIPTION                |
 * Signal    |  Pin       |   Pin       |                                            |
 * ----------|------------|-------------|--------------------------------------------|
 * FLAME     |      A0    |             |
 * INFRARED  |      A1    |             |
 * TEMP      |      A2    |             |
 * RX        |      0     |      TX2    |
 * TX        |      1     |      RX2    |
 * BUTTON    |      4     |
 * LED BLUE  |      5     |
 * LED RED   |      6     |
 * LED GREEN |      7     |
 * BUZZER    |      8     |
 * BUZZER    |      9     |
*/
#include <IRremote.h>
#include <LiquidCrystal_I2C.h>
#include <dht.h>
#include <SoftwareSerial.h>

SoftwareSerial sw(0, 1); // RX, TX
const int FLAME_PIN = A0;
const int SENSOR_IR = A1;
const int SENSOR_TEMP = A2;

const int IR_RECEIVER_PIN = 3;
const int BUTTON_PIN = 4;
const int LED_BLUE_PIN = 5;
const int LED_RED_PIN = 6;
const int LED_GREEN_PIN = 7;
const int PIEZO_PIN = 8;
const int PIEZO_2_PIN = 9;

dht DHT;

LiquidCrystal_I2C lcd(0x27, 16, 2);
String system_status;
const String STATUS_OK = "OK";
const String STATUS_FIRE = "FIRE";
const String TOPIC = "/ic/Grupo3/";
unsigned long lcd_timestamp;
unsigned long alarm_timestamp;
int flame_value;
float celsius;
bool button_status;
float fire_timestamp;

void setup() {
    Serial.begin(115200);
    sw.begin(19200);
    // Inputs
    IrReceiver.begin(IR_RECEIVER_PIN, ENABLE_LED_FEEDBACK); // IR receiver
    pinMode(BUTTON_PIN, INPUT_PULLUP);
    pinMode(FLAME_PIN, INPUT);
    pinMode(SENSOR_TEMP, INPUT);

    // Outputs
    pinMode(LED_BLUE_PIN, OUTPUT);
    pinMode(LED_RED_PIN, OUTPUT);
    pinMode(LED_GREEN_PIN, OUTPUT);
    pinMode(PIEZO_PIN, OUTPUT);
    pinMode(PIEZO_2_PIN, OUTPUT);

    // Initialize LCD
    lcd.begin(16, 2);
    lcd.init();
    lcd.backlight();
    
    system_status = "FIRE";
    celsius = 0;
    button_status = false;
    flame_value = 1000;
}

void loop() {
    // Temperature translation from analog signal
    float input = analogRead(SENSOR_TEMP) * 5000.0 / 1024.0;
    celsius = (input - 500.0) / 10.0;

    // Refreshing LCD every 5 seconds
    if (millis() - lcd_timestamp > 5000) {
        refresh_lcd();

        lcd_timestamp = millis();

        Serial.print("temp:");
        Serial.println(celsius);
    }

    // Flame signal reading
    flame_value = analogRead(FLAME_PIN);

    // Turn on buzzer when detecting fire
    check_fire(flame_value);

    // Button handling
    button_pressed();


    if (sw.available() > 0) {
        char bfr[501];
        memset(bfr, 0, 501);  // cria um buffer para receber os dados
        sw.readBytesUntil('\n', bfr, 500);  // lê dados para o buffer, até receber \n
        String data = String(bfr);  // converte os dados do buffer para String
        String topic = extract_topic(data);
        if (topic.equals("/ic/Grupo3/led")) {
          button_pressed();
        }
  }
}

void check_fire(float flame_value) {
  if (flame_value < 940) {
    //sw.println(flame_value);
    if(system_status != STATUS_FIRE){
      turn_red();
      if (millis() - alarm_timestamp > 3000) {
          turn_on_alarm();
          alarm_timestamp = millis();
      }
      Serial.println("fire:1");
      sw.println("fire:1");
      system_status = STATUS_FIRE;
      fire_timestamp = millis();
    }
  }else{
    if(system_status == STATUS_FIRE && millis() - fire_timestamp > 5000){
      system_ok();
      Serial.println("fire:0");
      sw.println("fire:0");
    }
  }
} 

const char* extract_topic(String serialData){
  String sub_topic;
  String topic;
  int text_size = serialData.length() - 1;
  int index = serialData.indexOf(":");

  if(index >= 0){
    sub_topic = serialData.substring(0, index);
    topic = TOPIC + sub_topic;
    topic.trim();
    return topic.c_str();
  }

  return serialData.c_str();
}

void button_pressed(){
    if (digitalRead(BUTTON_PIN) == LOW) {
        if(button_status == false){
          button_status = true;
          turn_on_led(LED_BLUE_PIN);
          Serial.println("button:1");
          sw.println("button:1");
        }
    } else {
        if(button_status == true){
          button_status = false;
          turn_off_led(LED_BLUE_PIN);
          Serial.println("button:0");
          sw.println("button:0");
        }
    }
}

const char* extract_serial_data(String serialData){
  String data;
  int text_size = serialData.length() - 1;
  int index = serialData.indexOf(":");

  if(index >= 0){
    data = serialData.substring(index + 1, text_size);
    data.trim();
    return data.c_str();
  }

  return serialData.c_str();
}

//system is ok
void system_ok(){
    system_status = STATUS_OK; 
    refresh_lcd();
} 

void refresh_lcd(){
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print(system_status);
  lcd.setCursor(0,1);
  lcd.print(celsius);
  lcd.print(" Celsius");
}

void turn_red() {
    turn_off_blue();
    turn_off_green();
    turn_on_red();
}

void turn_green() {
    turn_off_blue();
    turn_on_green();
    turn_off_red();
}

void turn_blue() {
    turn_on_blue();
    turn_off_green();
    turn_off_red();
}

void turn_on_red() {
    digitalWrite(LED_RED_PIN, HIGH);
}

void turn_off_red() {
    digitalWrite(LED_RED_PIN, LOW);
}

void turn_on_green() {
    digitalWrite(LED_GREEN_PIN, HIGH);
}

void turn_off_green() {
    digitalWrite(LED_GREEN_PIN, LOW);
}

void turn_on_blue() {
    digitalWrite(LED_BLUE_PIN, HIGH);
}

void turn_off_blue() {
    digitalWrite(LED_BLUE_PIN, LOW);
}

void turn_on_alarm() {
    tone(PIEZO_PIN, 590, 2000);
    //Serial.println("alarm");
}

void turn_off_alarm() {
    noTone(PIEZO_PIN);
}

void turn_on_led(int pin) {
    digitalWrite(pin, HIGH);
}

void turn_off_led(int pin) {
    digitalWrite(pin, LOW);
}
