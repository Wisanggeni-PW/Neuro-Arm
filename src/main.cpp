#include <Arduino.h>
#include <Servo.h>

// Define the pin where your servo's data line is connected
#define SERVO_PIN 9

// Create a Servo object
Servo myservo;

// Variable to store the current angle of the servo
int currentAngle = 90; // Renamed from incomingAngle for clarity

void setup()
{
    // Start the serial communication at the same baud rate as the Python script
    Serial.begin(9600);
    Serial.println("Arduino Relative Servo Controller Ready. Waiting for delta data...");

    // Attach the servo object to the pin
    myservo.attach(SERVO_PIN);
    myservo.write(currentAngle); // Set initial position
    Serial.print("Initial angle set to: ");
    Serial.print(currentAngle);
    Serial.println(" degrees.");
}

void loop()
{
    // Check if there is data available to be read from the serial port
    if (Serial.available() > 0)
    {
        // Read the incoming string until a newline character ('\n') is received.
        String receivedString = Serial.readStringUntil('\n');

        // Clean up the string (remove any leading/trailing whitespace)
        receivedString.trim();

        // Check if the received string is not empty
        if (receivedString.length() > 0)
        {
            // Convert the string to an integer. This is the CHANGE (delta) in angle.
            int deltaAngle = receivedString.toInt();

            // Calculate the new angle by applying the change to the current angle
            int newAngle = currentAngle + deltaAngle;

            // --- Angle Validation and Movement ---

            // Check if the calculated new angle is within the valid servo range (0-180)
            if (newAngle >= 0 && newAngle <= 180)
            {
                // Update the current angle
                currentAngle = newAngle;

                // Move the servo to the new angle
                myservo.write(currentAngle);

                // Echo the received command and the new angle back for debugging
                Serial.print("Received delta: ");
                Serial.print(deltaAngle);
                Serial.print(". New angle: ");
                Serial.print(currentAngle);
                Serial.println(" degrees.");
            }
            else
            {
                // Inform the user if the command would move the servo out of range
                Serial.print("Error: Delta of ");
                Serial.print(deltaAngle);
                Serial.print(" would result in angle ");
                Serial.print(newAngle);
                Serial.println(", which is out of 0-180 range. Movement ignored.");
            }
        }
    }
}