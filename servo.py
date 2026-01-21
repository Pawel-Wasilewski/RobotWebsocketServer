import time
import pigpio


class TrashcanLidController:
    def __init__(self, lid_id, servoPWM, servo5V, servoGND):
        self.lid_id = lid_id
        self.servoPWM = servoPWM
        self.servo5V = servo5V
        self.servoGND = servoGND

        self.pi = pigpio.pi()
        self.pi.set_mode(self.servoPWM, pigpio.OUTPUT)
        # PULSES
        self.MIN_PULSE = 500
        self.MAX_PULSE = 2500
        self.NEUTRAL = 1500

    def angle_to_pulse(self, angle):
        pulse = int(self.MIN_PULSE + (angle / 180.0) * (self.MAX_PULSE - self.MIN_PULSE))
        return pulse

    def set_angle(self, angle):
        pulse = self.angle_to_pulse(angle)
        self.pi.set_servo_pulsewidth(self.servoPWM, pulse)
        print(f"Setting lid {self.lid_id} to angle {angle} (pulse: {pulse})")

    def stopServo(self):
        self.pi.set_servo_pulsewidth(self.servoPWM, 0)
        print(f"Stopping servo for lid {self.lid_id}")

    def open_lid(self):
        print(f"Opening lid {self.lid_id}")
        self.set_angle(60)
        time.sleep(1)


    def close_lid(self):
        print(f"Closing lid {self.lid_id}")
        self.set_angle(0)
        time.sleep(1)

class MovementController:
    def __init__(self, DIR_LEFT, DIR_RIGHT, PWM_LEFT, PWM_RIGHT, GND):
        self.DIR_LEFT = DIR_LEFT
        self.DIR_RIGHT = DIR_RIGHT
        self.PWM_LEFT = PWM_LEFT
        self.PWM_RIGHT = PWM_RIGHT
        self.GND = GND

        self.pi = pigpio.pi()

        self.pi.set_mode(DIR_LEFT, pigpio.OUTPUT)
        self.pi.set_mode(DIR_RIGHT, pigpio.OUTPUT)

        FREQ = 20000

        self.pi.set_PWM_frequency(PWM_LEFT, FREQ)
        self.pi.set_PWM_frequency(PWM_RIGHT, FREQ)

    def turn_left_wheels(self):
        # TODO LOGIC
        print("Turning left wheels")
    def turn_right_wheels(self):
        # TODO LOGIC
        print("Turning right wheels")

    def move_forward(self):
        print("Moving forward")

    def move_backward(self):
        print("Moving backward")

    def turn_left(self):
        print("Turning left")

    def turn_right(self):
        print("Turning right")

    def stop(self):
        print("Stopping movement")

class ServoMotor:
    def __init__(self, pin):
        self.pin = pin

    def set_angle(self, angle):
        print(f"Setting servo on pin {self.pin} to angle {angle}")