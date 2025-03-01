import RPi.GPIO as GPIO
import time
import csv

# Servo pin setup
servo_pin = 12  # GPIO pin for the servo
GPIO.setmode(GPIO.BCM)  # BCM numbering
GPIO.setup(servo_pin, GPIO.OUT)  # Set as output

# Rotary encoder pin setup
encoder_a = 20  # GPIO pin for encoder channel A
encoder_b = 16 # GPIO pin for encoder channel B
GPIO.setup(encoder_a, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Set as input with pull-up
GPIO.setup(encoder_b, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Set as input with pull-up

# PWM setup for servo
pwm = GPIO.PWM(servo_pin, 50)  # 50Hz frequency
pwm.start(0)  # Initialize at 0% duty cycle

# CSV file setup
csv_filename = 'encoder_test.csv'

# Rotary encoder position tracking
encoder_position = 0

def rotary_encoder_callback(channel):
    """Callback function to update encoder position."""
    global encoder_position
    if GPIO.input(encoder_a) == GPIO.input(encoder_b):
        encoder_position += 1  # Clockwise rotation
    else:
        encoder_position -= 1  # Counter-clockwise rotation

# Attach interrupt for the encoder
GPIO.add_event_detect(encoder_a, GPIO.BOTH, callback=rotary_encoder_callback)

def set_angle(angle, writer):
    """Set servo angle and record angle with encoder position."""
    global encoder_position
    duty_cycle = 3 + (angle / 18)  # Maps 0-180 to 2-12 duty cycle
    print(f"Setting angle: {angle} deg -> Duty cycle: {duty_cycle:.2f}%, Encoder: {encoder_position}")
    writer.writerow([angle, duty_cycle, encoder_position])
    pwm.ChangeDutyCycle(duty_cycle)
    time.sleep(1)
    pwm.ChangeDutyCycle(0)  # Minimize jitter

try:
    with open(csv_filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Angle (deg)', 'Duty Cycle (%)', 'Encoder Position'])

        # Sweep servo angles while recording encoder data
        for angle in range(0, 181, 10):  # From 0 to 180 degrees
            set_angle(angle, writer)
            time.sleep(0.5)

        for angle in range(180, -1, -10):  # Back down from 180 to 0 degrees
            set_angle(angle, writer)
            time.sleep(0.5)

finally:
    pwm.stop()  # Stop the servo PWM signal
    GPIO.cleanup()  # Reset GPIO settings
 




import RPi.GPIO as GPIO
import time
import csv


# Servo pin setup

GPIO.setmode(GPIO.BCM)  # BCM numbering

GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

encoder_a = 20  # GPIO pin for encoder channel A
encoder_b = 16 # GPIO pin for encoder channel B

# Rotary encoder position tracking
encoder_position = 0



while True:
	if GPIO.input(encoder_a) != GPIO.input(encoder_b):
		if encoder_a > encoder_b:
			encoder_position += 1  # Clockwise rotation
			print(encoder_position)
		elif encoder_a < encoder_b:
			encoder_position -= 1  # Counter-clockwise rotation
			print(encoder_position)
	elif GPIO.input(encoder_a) == GPIO.input(encoder_b):
		encoder_position = 0
		print(encoder_position)		
				
				

import RPi.GPIO as GPIO
import time

# Servo pin setup
GPIO.setmode(GPIO.BCM)  # BCM numbering

GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(16, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

encoder_a = 20  # GPIO pin for encoder channel A
encoder_b = 16  # GPIO pin for encoder channel B

# Rotary encoder position tracking
encoder_position = 0

# Initial states
last_state_a = GPIO.input(encoder_a)
last_state_b = GPIO.input(encoder_b)

try:
	while True:
		current_state_a = GPIO.input(encoder_a)
		current_state_b = GPIO.input(encoder_b)

		if current_state_a != last_state_a or current_state_b != last_state_b:
			if current_state_a == current_state_b:
				encoder_position += 1  # Clockwise rotation
			else:
				encoder_position -= 1  # Counter-clockwise rotation

			print(encoder_position)

		last_state_a = current_state_a
		last_state_b = current_state_b

		time.sleep(0.01)  # Small delay to debounce

except KeyboardInterrupt:
	GPIO.cleanup()		
