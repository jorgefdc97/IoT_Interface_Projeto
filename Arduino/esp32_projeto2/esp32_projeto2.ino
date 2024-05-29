#include <WiFi.h>
#include <PubSubClient.h>
#include <HardwareSerial.h>

// Use Serial2 on the ESP32 for communication with the Arduino
HardwareSerial SerialPort(2);

// Update these with values suitable for your network.
const char* ssid = "DuckNet";
const char* password = "DuckieUPT";
const char* mqtt_server = "192.168.0.101";
#define mqtt_port 1883
#define TOPIC "/ic/Grupo3"
const char* topic1 = "/ic/#";

WiFiClient wifiClient;
PubSubClient mqttClient(wifiClient);

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
      boolean res = mqttClient.subscribe(topic1);
      Serial.print(topic1); 
      Serial.println(res ? "  true" : "  false");
    } else {
      Serial.print("failed, rc=");
      Serial.print(mqttClient.state());
      Serial.println(" try again in 5 seconds");
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  Serial.setTimeout(500);  // Set timeout for serial reading
  // Initialize Serial2 for communication with Arduino
  SerialPort.begin(19200, SERIAL_8N1, 16, 17);
  setup_wifi();
  mqttClient.setServer(mqtt_server, mqtt_port);
  mqttClient.setCallback(callback);
  reconnect();
}

void publishSerialData(const char* serialData) {
  if (!mqttClient.connected()) {
    reconnect();
  }
  mqttClient.publish(TOPIC, serialData);
  Serial.print("Publish : ");
  Serial.print(TOPIC);
  Serial.print(" : ");
  Serial.println(serialData);
}

void callback(char* topic, byte* payload, unsigned int length) {
  Serial.print("Message arrived [");
  Serial.print(topic);
  Serial.print("] ");
  for (unsigned int i = 0; i < length; i++) {
    Serial.print((char)payload[i]);
  }
  Serial.println();
}

void loop() {
  mqttClient.loop();
  Serial.println(".");
  if (SerialPort.available() > 0) {
    Serial.println("dados");
    char bfr[501];
    memset(bfr, 0, 501);
    SerialPort.readBytesUntil('\n', bfr, 500);
    String b = String(bfr);
    publishSerialData(bfr);
  }
  //Serial.print("ola");
  SerialPort.print("ola");
  delay(5000);
}
