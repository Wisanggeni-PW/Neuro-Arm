import serial
import time

SERVO_PORT = 'COM7' 
BAUD_RATE = 9600

try:
    ser = serial.Serial(SERVO_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
    print(f"--- Connected to Arduino on {SERVO_PORT} at {BAUD_RATE} baud ---")

except serial.SerialException as e:
    print(f"Error connecting to serial port {SERVO_PORT}: {e}")
    print("Please check the port name and ensure the Arduino IDE Serial Monitor is closed.")

def rotate(angle):
    data_to_send = f"{angle}\n".encode('utf-8')
    ser.write(data_to_send)
    print(f"Modify angle by: {angle} degrees.")

if __name__ == "__main__":
    rotate()