void setup() {
  Serial.begin(9600);
}

void loop() {
  int sensorValue = analogRead(A0); // Reading from A0
  Serial.print("a0: ");
  Serial.println(sensorValue);
  delay(500); // Adjust the delay as needed
}
