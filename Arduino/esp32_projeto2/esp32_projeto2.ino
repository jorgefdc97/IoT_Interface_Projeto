#include <WiFi.h>
#include <PubSubClient.h>
#include <HardwareSerial.h>
#include <iostream>
#include <string>

// Use Serial2 on the ESP32 for communication with the Arduino
HardwareSerial SerialPort(2);

// Update these with values suitable for your network.
//const char* ssid = "upt-convidados";
//const char* password = "welcome2upt";
const char* ssid = "upt-convidados";
const char* password = "welcome2upt";
const char* mqtt_server = "192.168.0.100";
#define mqtt_port 1883
#define TOPIC "/ic/Grupo3/"
const char* topic1 = "/ic/#";

WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);


void setup() {
  Serial.begin(19200);
  Serial.setTimeout(500);  // Set timeout for serial reading
  // Initialize Serial2 for communication with Arduino
  SerialPort.begin(115200, SERIAL_8N1, 16, 17);
  setup_wifi();
  mqttClient.setServer(mqtt_server, mqtt_port);
  mqttClient.setCallback(callback);
  reconnect();
}


void loop() {
  mqttClient.loop();
  //Serial.println(".");
  if (SerialPort.available() > 0) {
    char bfr[501];
    memset(bfr, 0, 501);
    SerialPort.readBytesUntil('\n', bfr, 500);
    String b = String(bfr);
    Serial.println("SERIAL DATA: ");
    publishSerialData(bfr); // Publish : /ic/Grupo3 : temp:14.45
    Serial.println("========== ");
  }
  //Serial.print("ola");
  //SerialPort.print("ola");
  delay(15000);
}


void publishSerialData(const char* serialData) {
  if (!mqttClient.connected()) {
    reconnect();
  }
  //extract data
  const char* data = extract_serial_data(serialData);
  // Construct topic
  const char* topic = extract_topic(serialData);
  //publish data
  mqttClient.publish(topic, data);
  //debug
  Serial.print("Publish : ");
  Serial.print(topic);
  Serial.print(" : ");
  Serial.println(data);
}


void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (unsigned int i = 0; i < length; i++) {
    SerialPort.print((char)payload[i]);
  }
  Serial.println();
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


void setup_wifi() {
  delay(10);
  // Start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.println("WiFi connected");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}


void reconnect() {
  // Loop until we're reconnected
  while (!mqttClient.connected()) {
    Serial.print("Attempting MQTT connection...");
    char* clientId = "Grupo3_ESP32";
    if (mqttClient.connect(clientId)) {
      Serial.println("mqttClient connected");
      mqttClient.publish(TOPIC, "hello world");
      Serial.print("Publish : ");
      Serial.print(TOPIC);
      Serial.print(" : ");
      Serial.println("hello world");
      //boolean res = mqttClient.subscribe(topic1);
      Serial.print(topic1); 
      //Serial.println(res ? "  true" : "  false");
    } else {
      Serial.print("failed, rc=");
      Serial.print(mqttClient.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}



