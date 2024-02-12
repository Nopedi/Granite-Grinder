#include <ArduinoBLE.h>
#include <Servo.h>
#include <Ramp.h>

rampFloat ramp_h, ramp_r, ramp_c;

Servo servo_h, servo_r, servo_c;

const int8_t drill_pin = 5;
const int8_t servo_h_pin = 7;
const int8_t servo_r_pin = 9;
const int8_t servo_c_pin = 11;
const int8_t led_pin = 13;

const int shb = 90;   //servo_h_base
const int srb = 85;   //servo_r_base
const int scb = 160;  //servo_c_base

int walking_speed = 0;
int step_size = 0;
int slide_size_L = 0;
int slide_size_R = 0;
int rollcage_value = 0;
bool drill_status = 0;
bool led_status = 0;

int goal_h = 90;
int goal_r = 90;

String input = "";

BLEService granite_grinder("5B12"); // BLE LED Service

BLEByteCharacteristic walking_speed_characteristic("1111", BLEWrite);
BLEByteCharacteristic step_size_characteristic("1112", BLEWrite);
BLEByteCharacteristic slide_size_L_characteristic("1116", BLEWrite);
BLEByteCharacteristic slide_size_R_characteristic("1117", BLEWrite);
BLEByteCharacteristic servo_c_characteristic("1113", BLEWrite);
BLEBoolCharacteristic drill_characteristic("1114", BLEWrite);
BLEBoolCharacteristic led_characteristic("1115", BLEWrite);
BLEBoolCharacteristic reset_characteristic("1118", BLEWrite);

void(* resetFunc) (void) = 0;

void setup() {
  Serial.begin(9600);

  pinMode(drill_pin, OUTPUT);
  pinMode(led_pin, OUTPUT);
  pinMode(servo_h_pin, OUTPUT);
  pinMode(servo_r_pin, OUTPUT);
  pinMode(servo_c_pin, OUTPUT);

  // set LED's pin to output mode
  pinMode(LEDR, OUTPUT);
  pinMode(LEDG, OUTPUT);
  pinMode(LEDB, OUTPUT);
  pinMode(LED_BUILTIN, OUTPUT);

  digitalWrite(LED_BUILTIN, LOW);         // when the central disconnects, turn off the LED
  digitalWrite(LEDR, HIGH);               // will turn the LED off
  digitalWrite(LEDG, HIGH);               // will turn the LED off
  digitalWrite(LEDB, HIGH);                // will turn the LED off

  servo_h.attach(servo_h_pin);
  servo_r.attach(servo_r_pin);
  servo_c.attach(servo_c_pin);

  servo_h.write(shb);
  servo_r.write(srb);
  servo_c.write(scb);

  ramp_h.go(shb);
  ramp_r.go(srb);
  ramp_c.go(scb);

  // begin initialization
  if (!BLE.begin()) {
    Serial.println("starting Bluetooth® Low Energy failed!");

    while (1);
  }

  // set advertised local name and service UUID:
  BLE.setConnectionInterval(0x0006, 0x0c80);
  BLE.setLocalName("Granite Grinder");
  BLE.setAdvertisedService(granite_grinder);

  // add the characteristic to the service
  granite_grinder.addCharacteristic(walking_speed_characteristic);
  granite_grinder.addCharacteristic(step_size_characteristic);
  granite_grinder.addCharacteristic(servo_c_characteristic);
  granite_grinder.addCharacteristic(drill_characteristic);
  granite_grinder.addCharacteristic(led_characteristic);
  granite_grinder.addCharacteristic(slide_size_L_characteristic);
  granite_grinder.addCharacteristic(slide_size_R_characteristic);
  granite_grinder.addCharacteristic(reset_characteristic);
  // add service
  BLE.addService(granite_grinder);

  // start advertising
  BLE.advertise();

  Serial.println("Time for some Granite Grinding");
  Serial.print("My address is: ");
  Serial.println(BLE.address());
}

void loop() {
  bluetoothZeug();
  digitalWrite(drill_pin, drill_status);
  digitalWrite(led_pin, led_status);
  servo_c.write(ramp_c.update());
  if (walking_speed > 5) {
    doStep(walking_speed, step_size, slide_size_L, slide_size_R);
  }
}

void doStep(int step_speed_in, int step_length, int slide_length_L, int slide_length_R) {
  goal_h = shb - slide_length_L;
  //Serial.println("1");
  ramp_h.go(goal_h, step_speed_in, QUADRATIC_INOUT);
  while (abs(ramp_h.update() - goal_h) > 1) {
    servo_h.write(ramp_h.getValue());
    //Serial.println(ramp_h.getValue());
  }
  //Serial.println("2");
  goal_r = srb - step_length;
  ramp_r.go(goal_r, step_speed_in, QUADRATIC_INOUT);
  while (abs(ramp_r.update() - goal_r) > 1) {
    servo_r.write(ramp_r.getValue());
    //Serial.println(ramp_r.getValue());
  }
  //Serial.println("3");
  goal_h = shb + slide_length_R;
  ramp_h.go(goal_h, step_speed_in, QUADRATIC_INOUT);
  while (abs(ramp_h.update() - goal_h) > 1) {
    servo_h.write(ramp_h.getValue());
    //Serial.println(ramp_h.getValue());
  }
  //Serial.println("4");
  goal_r = srb + step_length;
  ramp_r.go(goal_r, step_speed_in, QUADRATIC_INOUT);
  while (abs(ramp_r.update() - goal_r) > 1) {
    servo_r.write(ramp_r.getValue());
    //Serial.println(ramp_r.getValue());
  }
}

void bluetoothZeug() {
  BLE.poll();
  if (BLE.connected()) {
    digitalWrite(LEDR, LOW);         // will turn the LED off
    digitalWrite(LEDG, LOW);         // will turn the LED off
    digitalWrite(LEDB, LOW);         // will turn the LED off
    if (walking_speed_characteristic.written()) {
      walking_speed = int(walking_speed_characteristic.value()) * 10;
      //Serial.print("Walking Speed: ");
      //Serial.println(walking_speed);
    } else if (step_size_characteristic.written()) {
      step_size = int(step_size_characteristic.value());
      //Serial.print("Step Size: ");
      //Serial.println(step_size);
    } else if (slide_size_L_characteristic.written()) {
      slide_size_L = int(slide_size_L_characteristic.value());
      //Serial.print("Slide Size L: ");
      //Serial.println(slide_size_L);
    } else if (slide_size_R_characteristic.written()) {
      slide_size_R = int(slide_size_R_characteristic.value());
      //Serial.print("Slide Size R: ");
      //Serial.println(slide_size_R);
    } else if (servo_c_characteristic.written()) {
      rollcage_value = int(servo_c_characteristic.value());
      //Serial.print("Collcage Value: ");
      //Serial.println(rollcage_value);
      ramp_c.go(rollcage_value, 2500);
    } else if (drill_characteristic.written()) {
      drill_status = int(drill_characteristic.value());
      //Serial.print("Drill Status: ");
      //Serial.println(drill_status);
    } else if (led_characteristic.written()) {
      led_status = int(led_characteristic.value());
      //Serial.print("Led_ Status: ");
      //Serial.println(led_status);
    } else if (reset_characteristic.written()) {
      walking_speed = 0;
      step_size = 0;
      slide_size_L = 0;
      slide_size_R = 0;
      rollcage_value = 0;
      //drill_status = 0;
      //led_status = 0;
      servo_h.write(shb);
      servo_r.write(srb);
      servo_c.write(scb);
    }
  } else {
    digitalWrite(LEDR, HIGH);         // will turn the LED off
    digitalWrite(LEDG, HIGH);         // will turn the LED off
    digitalWrite(LEDB, HIGH);         // will turn the LED off
  }
  //digitalWrite(LEDR, HIGH);         // will turn the LED off
  //digitalWrite(LEDG, HIGH);         // will turn the LED off
  //digitalWrite(LEDB, HIGH);         // will turn the LED off
}
