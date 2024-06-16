# IoT_Interface_Projeto

## Project Overview

The `IoT_Interface_Projeto` is a comprehensive project integrating Arduino, ESP32, and a graphical user interface (GUI) to create an IoT system. This system includes local and remote applications, MQTT communication, and data visualization. 

## Directory Structure

The project is organized into several directories, each serving a specific purpose:

```
IoT_Interface_Projeto
├── Arduino_and_MQTT
│   ├── arduino_projeto2
│   │   └── arduino_projeto2.ino
│   └── esp32_projeto2
│       └── esp32_projeto2.ino
├── Interface
│   ├── Local
│   │   ├── Application.py
│   │   └── PublisherMenu.py
│   ├── Remote
│   │   ├── Application_Remote.py
│   └── resources
├── MQTT_Simulator
│   ├── Publisher_Remote.py
│   └── Subscriber_Remote.py
└── requirements.txt
```

### Arduino_and_MQTT

This directory contains the Arduino and ESP32 sketches used in the project.

- **arduino_projeto2/arduino_projeto2.ino**: The Arduino sketch for the project. It includes code for sensors and actuators used in the IoT system.
- **esp32_projeto2/esp32_projeto2.ino**: The ESP32 sketch for the project. It handles WiFi connectivity and MQTT communication.

### Interface

This directory contains the local and remote applications along with the necessary resources.

#### Local

- **Application.py**: The main application file for the local GUI. It sets up the interface and handles MQTT subscriptions to display real-time data and alerts.
- **PublisherMenu.py**: A script to publish data or commands to the MQTT broker, useful for testing and managing the IoT devices.

#### Remote

- **Application_Remote.py**: The main application file for the remote GUI. It serves a similar purpose to `Application.py` but is intended for use in a remote environment.

#### resources

This directory contains images and other resources needed by the applications. Ensure that the necessary images (e.g., thermometer.png) are present in this directory for the GUI to function correctly.

### MQTT_Simulator

This directory contains scripts for simulating MQTT messages, useful for testing the system without actual hardware.

- **Publisher_Remote.py**: A script to simulate publishing messages from remote devices.
- **Subscriber_Remote.py**: A script to simulate subscribing to MQTT messages, useful for testing how the system reacts to incoming data.

### requirements.txt

This file lists the Python dependencies required for the project. Use the following command to install them:

```sh
pip install -r requirements.txt
```

## Getting Started

1. **Setup the Hardware**:
   - Upload the `arduino_projeto2.ino` sketch to the Arduino board.
   - Upload the `esp32_projeto2.ino` sketch to the ESP32 board.

2. **Install Dependencies**:
   - Navigate to the project directory and install the necessary Python packages:
     ```sh
     pip install -r requirements.txt
     ```

3. **Run the Local Application for testing locally**:
   - Navigate to the `Interface/Local` directory and run the `Application.py` and `PublisherMenu.py` scripts:
     ```sh
     python Application.py
     python PublisherMenu.py
     ```

4. **Run the Remote Application for testing with boards**:
   - Navigate to the `Interface/Remote` directory and run the `Application_Remote.py` script:
     ```sh
     python Application_Remote.py
     ```

5. **Simulate MQTT Messages**:
   - Use the scripts in the `MQTT_Simulator` directory to simulate MQTT messages for testing purposes:
     ```sh
     python Publisher_Remote.py
     python Subscriber_Remote.py
     ```

## Topics

### MQTT Topics Used in the Subscriber

The `Subscriber` class in the `Application.py` script handles various MQTT topics to manage and monitor the IoT system. Below is a detailed description of each topic:

#### General Topics

1. **`/ic/#`**
   - **Description**: This is a wildcard topic that subscribes to all messages under the `/ic` topic hierarchy.
   - **Purpose**: Used for broad subscription to capture all relevant messages for the IoT system, allowing the application to process a wide range of data and commands.

2. **`/ic/Grupo3/#`**
   - **Description**: Another wildcard topic, but more specific to the `Grupo3` group.
   - **Purpose**: Focuses on capturing all messages related to the `Grupo3` group, ensuring the application receives and processes only the relevant group-specific messages.

#### Specific Topics

3. **`/ic/Grupo3/test`**
   - **Description**: A specific topic for testing purposes.
   - **Purpose**: Used to send and receive test messages, useful for debugging and ensuring the MQTT setup is working correctly.

4. **`/ic/Grupo3/temp`**
   - **Description**: A topic dedicated to temperature data.
   - **Purpose**: Used to receive temperature readings from sensors. The application processes these readings to update the temperature display and graph in the GUI.

5. **`/ic/Grupo3/fire`**
   - **Description**: A topic for fire alarm status.
   - **Purpose**: Used to receive fire alarm signals. Depending on the message (`0` or `1`), the application updates the GUI to show whether there is a fire alert, activating or deactivating the corresponding visual indicators.

6. **`/ic/+/alarme`**
   - **Description**: A wildcard topic to capture alarm messages from any sub-topic under `/ic`.
   - **Purpose**: This is useful for handling alarm messages from different sources or groups dynamically, ensuring comprehensive monitoring of alarm signals.

7. **`/ic/Grupo3/alarme`**
   - **Description**: A topic for general alarm status.
   - **Purpose**: Used to receive general alarm signals. Similar to the fire alarm, the application updates the visual indicators based on the message payload (`0` or `1`).
    
8. **`/ic/[a-zA-Z]+[0-24-9]/alarme`**
   - **Description**: A pattern-based topic for group-specific alarm messages.
   - **Purpose**: Allows the application to capture and process alarm signals from various dynamically named groups. The regular expression ensures that messages from groups with alphanumeric names followed by digits (except 1) are captured and processed.

### How These Topics Are Used

1. **Connection and Subscription**
   - When the client connects to the MQTT broker, it subscribes to the general and specific topics to ensure it receives all necessary messages.
   - The `on_connect` method handles the subscription logic.

2. **Message Handling**
   - The `on_message` method processes incoming messages based on their topics.
   - For each specific topic, the method decodes the payload and updates the application state accordingly.
   - For temperature updates (`/ic/Grupo3/temp`), it refreshes the temperature display and graph.
   - For fire and alarm updates (`/ic/Grupo3/fire`, `/ic/Grupo3/alarme`), it updates the visual indicators on the GUI.
   - For dynamic group-specific alarms, it adjusts the corresponding group messages and visual cues.

By using these topics, the `Subscriber` class ensures that the IoT application can effectively monitor and respond to various signals and data points, maintaining an accurate and responsive interface for the users.


## Notes

- Ensure that the MQTT broker address and credentials in the application scripts match your setup.
- The GUI requires certain images to be present in the `resources` directory. Make sure these images are correctly placed and named as expected by the application.
- The correct display of some fonts needs to match `Digital-7`

## License

This project is licensed under the MIT License. See the LICENSE file for details.

---

This README provides a clear and detailed overview of the project, guiding users through the directory structure, setup, and usage.
