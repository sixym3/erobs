// Arduino RS485 Receiver using Arduino RS485 Library
// Install library: Tools -> Manage Libraries -> Search "RS485" -> Install "RS485" by Arduino
// Note: Cannot use Serial Monitor as RS485 uses pins 0 (RX) and 1 (TX)

#include <ArduinoRS485.h>
#include <Adafruit_NeoPixel.h>

#ifdef __AVR__
  #include <avr/power.h>
#endif
#define PIN      12
#define NUMPIXELS 7

Adafruit_NeoPixel pixels(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);
#define DELAYVAL 500

#define LED_BUILTIN 13      // Built-in LED pin

// Timing constants
#define STARTUP_FLASH_DELAY 50     // Fast flash on startup
#define HEARTBEAT_INTERVAL 5000    // Heartbeat every 5 seconds
#define HEARTBEAT_DURATION 50      // Duration of heartbeat pulse

// Global variables
unsigned long lastHeartbeat = 0;
String receiveBuffer = "";
bool ledState = false;
unsigned long startTime = 0;

void setup() {
  // Initialize LED
  pinMode(LED_BUILTIN, OUTPUT);
  
  // Flash LED 10 times quickly to indicate ready
  for(int i = 0; i < 10; i++) {
    digitalWrite(LED_BUILTIN, HIGH);
    delay(STARTUP_FLASH_DELAY);
    digitalWrite(LED_BUILTIN, LOW);
    delay(STARTUP_FLASH_DELAY);
  }
  
  // Start RS485 communication
  // Uses hardware serial (pins 0 and 1) at 115200 baud
  RS485.begin(115200);
  
  // Set receive mode
  RS485.receive();
  
  // Send startup message
  sendMessage("Arduino RS485 Receiver Ready");
  sendMessage("Using pins 0 (RX) and 1 (TX)");
  sendMessage("Heartbeat interval: 5 seconds");
  
  // Record start time
  startTime = millis();
  pixels.begin();
}

void loop() {
  // Check for incoming RS485 data
  while(RS485.available()) {
    char c = RS485.read();
    
    // Build command string until newline
    if(c == '\n' || c == '\r') {
      if(receiveBuffer.length() > 0) {
        // Process the received command
        processCommand(receiveBuffer);
        receiveBuffer = "";  // Clear buffer
      }
    } else {
      receiveBuffer += c;
    }
  }
  
  // Heartbeat - send message every 5 seconds
  unsigned long currentMillis = millis();
  if(currentMillis - lastHeartbeat >= HEARTBEAT_INTERVAL) {
    lastHeartbeat = currentMillis;
    
    // Send heartbeat message
    unsigned long uptime = (currentMillis - startTime) / 1000;
    String heartbeatMsg = "Heartbeat - Uptime: " + String(uptime) + " seconds, LED: " + (ledState ? "ON" : "OFF");
    sendMessage(heartbeatMsg);
    
    // Brief LED pulse for heartbeat (only if LED is off)
    if(!ledState) {
      digitalWrite(LED_BUILTIN, HIGH);
      delay(HEARTBEAT_DURATION);
      digitalWrite(LED_BUILTIN, LOW);
    }
  }
}

void processCommand(String command) {
  // Trim whitespace
  command.trim();
  
  // Echo the received command
  sendMessage("Received command: " + command);
  
  // Check for specific commands
  if(command == "V" || command == "v") {
    // Toggle LED
    ledState = !ledState;
    digitalWrite(LED_BUILTIN, ledState);
    sendMessage("LED toggled - Now: " + String(ledState ? "ON" : "OFF"));
  } else if(command == "TEST") {
    sendMessage("Test command acknowledged");
    pixels.clear();
    for(int i=0; i<NUMPIXELS; i++) {
      pixels.setPixelColor(i, pixels.Color(0, 150, 0));
      pixels.show();
      delay(DELAYVAL);
    }
  } else if(command == "HELLO") {
    sendMessage("Hello from Arduino!");
  } else if(command.startsWith("CMD")) {
    sendMessage("Processing command: " + command);
    pixels.clear();
    pixels.show();
  } else if(command == "STATUS") {
    // Status command to check system state
    unsigned long uptime = (millis() - startTime) / 1000;
    sendMessage("Status: LED=" + String(ledState ? "ON" : "OFF") + ", Uptime=" + String(uptime) + "s");
  } else {
    sendMessage("Unknown command: " + command);
  }
}

void sendMessage(String message) {
  RS485.beginTransmission();
  RS485.println(message);
  RS485.endTransmission();
}