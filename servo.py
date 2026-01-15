#TODO SERVO: Implement servo motor control functions

class TrashcanLidController:
    def __init__(self, lid_id, servo_motor1, servo_motor2):
        self.lid_id = lid_id
        self.servo_motor1 = servo_motor1
        self.servo_motor2 = servo_motor2

    def open_lid(self):
        print(f"Opening lid {self.lid_id}")

    def close_lid(self):
        print(f"Closing lid {self.lid_id}")

class MovementController:
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