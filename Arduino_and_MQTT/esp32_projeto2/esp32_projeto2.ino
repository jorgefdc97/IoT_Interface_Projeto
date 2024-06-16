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
const char* ssid = "DuckNet";
const char* password = "DuckieUPT";
const char* mqtt_server = "192.168.0.101";
#define mqtt_port 1883
#define TOPIC "/ic/Grupo3/"
#define TOPIC_APP "/ic/Grupo3_APP/#"
const char* topic1 = "/ic/+/alarme";

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
  if (SerialPort.available() > 0) {
    char bfr[501];
    memset(bfr, 0, 501);
    SerialPort.readBytesUntil('\n', bfr, 500);
    String b = String(bfr);
    publishSerialData(bfr); // Publish : /ic/Grupo3 : temp:14.45
  }
  //Serial.print("ola");
  //SerialPort.print("ola");
}


void publishSerialData(const String& serialData) {
  if (!mqttClient.connected()) {
    reconnect();
  }
  // Extract data
  String data = extract_serial_data(serialData);
  // Construct topic
  String topic = extract_topic(serialData);
  // Publish data
  mqttClient.publish(topic.c_str(), data.c_str());
  // Debug
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


String extract_topic(const String& serialData) {
  int index = serialData.indexOf(":");
  if (index >= 0) {
    String sub_topic = serialData.substring(0, index);
    String topic = String(TOPIC) + sub_topic;
    topic.trim();
    return topic;
  }
  return serialData;
}


String extract_serial_data(const String& serialData) {
  int index = serialData.indexOf(":");
  if (index >= 0) {
    String data = serialData.substring(index + 1);
    data.trim();
    return data;
  }
  return serialData;
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
    if (mqttClient.connect("Grupo3_ESP32")) {
      Serial.println("mqttClient connected");
      mqttClient.publish(TOPIC, "hello world");
      Serial.print("Publish : ");
      Serial.print(TOPIC);
      Serial.print(" : ");
      Serial.println("hello world");
      boolean res = mqttClient.subscribe(topic1);
      boolean res1 = mqttClient.subscribe(TOPIC_APP);
      Serial.print(topic1);
      Serial.println(res ? "  true" : "  false");
      Serial.print(TOPIC_APP);
      Serial.println(res1 ? "  true" : "  false");
    } else {
      Serial.print("failed, rc=");
      Serial.print(mqttClient.state());
      Serial.println(" try again in 5 seconds");
      delay(2000);
    }
  }
}