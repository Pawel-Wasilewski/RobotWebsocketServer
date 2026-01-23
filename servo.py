import asyncio
import pigpio


# ================= TRASHCAN LID =================

class TrashcanLidController:
    def __init__(self, lid_id, servoPWM, servo5V, servoGND):
        self.lid_id = lid_id
        self.servoPWM = servoPWM
        self.servo5V = servo5V
        self.servoGND = servoGND

        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise RuntimeError("pigpio not running – start with: sudo pigpiod")

        self.pi.set_mode(self.servoPWM, pigpio.OUTPUT)

        # PULSES
        self.MIN_PULSE = 500
        self.MAX_PULSE = 2500
        self.NEUTRAL = 1500

    def angle_to_pulse(self, angle):
        return int(self.MIN_PULSE + (angle / 180.0) *
                   (self.MAX_PULSE - self.MIN_PULSE))

    def set_angle(self, angle):
        pulse = self.angle_to_pulse(angle)
        self.pi.set_servo_pulsewidth(self.servoPWM, pulse)
        print(f"Lid {self.lid_id} → {angle}° (pulse {pulse})")

    def stop_servo(self):
        self.pi.set_servo_pulsewidth(self.servoPWM, 0)
        print(f"Lid {self.lid_id} stopped")

    async def open_lid(self):
        print(f"Opening lid {self.lid_id}")
        self.set_angle(60)
        await asyncio.sleep(1)
        self.stop_servo()

    async def close_lid(self):
        print(f"Closing lid {self.lid_id}")
        self.set_angle(0)
        await asyncio.sleep(1)
        self.stop_servo()


# ================= MOVEMENT =================

class MovementController:
    def __init__(self, DIR_LEFT, DIR_RIGHT, PWM_LEFT, PWM_RIGHT, GND):
        self.DIR_LEFT = DIR_LEFT
        self.DIR_RIGHT = DIR_RIGHT
        self.PWM_LEFT = PWM_LEFT
        self.PWM_RIGHT = PWM_RIGHT
        self.GND = GND

        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise RuntimeError("pigpio not running – start with: sudo pigpiod")

        for pin in [DIR_LEFT, DIR_RIGHT]:
            self.pi.set_mode(pin, pigpio.OUTPUT)

        for pin in [PWM_LEFT, PWM_RIGHT]:
            self.pi.set_mode(pin, pigpio.OUTPUT)
            self.pi.set_PWM_frequency(pin, 20000)
            self.pi.set_PWM_range(pin, 255)

        self.stop()

    def _drive(self, pwm_pin, dir_pin, speed):
        speed = int(max(min(speed, 255), -255))

        if speed >= 0:
            self.pi.write(dir_pin, 0)
            self.pi.set_PWM_dutycycle(pwm_pin, speed)
        else:
            self.pi.write(dir_pin, 1)
            self.pi.set_PWM_dutycycle(pwm_pin, -speed)

    def stop(self):
        print("Motors STOP")
        self.pi.set_PWM_dutycycle(self.PWM_LEFT, 0)
        self.pi.set_PWM_dutycycle(self.PWM_RIGHT, 0)

    def move_forward(self, speed=180):
        print(f"Forward {speed}")
        self._drive(self.PWM_LEFT, self.DIR_LEFT, speed)
        self._drive(self.PWM_RIGHT, self.DIR_RIGHT, speed)

    def move_backward(self, speed=180):
        print(f"Backward {speed}")
        self._drive(self.PWM_LEFT, self.DIR_LEFT, -speed)
        self._drive(self.PWM_RIGHT, self.DIR_RIGHT, -speed)

    def turn_left(self, speed=160):
        print(f"Turn left {speed}")
        self._drive(self.PWM_LEFT, self.DIR_LEFT, speed // 2)
        self._drive(self.PWM_RIGHT, self.DIR_RIGHT, speed)

    def turn_right(self, speed=160):
        print(f"Turn right {speed}")
        self._drive(self.PWM_LEFT, self.DIR_LEFT, speed)
        self._drive(self.PWM_RIGHT, self.DIR_RIGHT, speed // 2)

    def shutdown(self):
        print("Shutting down motors")
        self.stop()
        self.pi.stop()
