import time
from robomaster import robot

ep_robot = robot.Robot()
ep_robot.initialize(conn_type="sta")
ep_chassis = ep_robot.chassis
ep_gripper = ep_robot.gripper
speed = 2000
slp = 1


def go_straight(distance_cm):
    try:
        distance_m = distance_cm / 100.0
        linear_speed = 0.4
        time_needed = distance_m / linear_speed
        wheel_diameter = 0.100
        wheel_circumference = 3.14 * wheel_diameter
        wheel_rpm = (linear_speed * 60) / wheel_circumference
        wheel_rpm = -int(wheel_rpm)
        ep_chassis.drive_wheels(w1=wheel_rpm, w2=wheel_rpm, w3=wheel_rpm, w4=wheel_rpm, timeout = time_needed)
        return True
    except Exception as e:
        print(f"Error in go_straight: {e}")
        ep_chassis.drive_wheels(w1=0, w2=0, w3=0, w4=0)
        return False


def go_backward(distance_cm):
    try:
        distance_m = distance_cm / 100.0
        linear_speed = 0.4
        time_needed = distance_m / linear_speed
        wheel_diameter = 0.100
        wheel_circumference = 3.14 * wheel_diameter
        wheel_rpm = (linear_speed * 60) / wheel_circumference
        wheel_rpm = int(wheel_rpm)
        ep_chassis.drive_wheels(w1=wheel_rpm, w2=wheel_rpm, w3=wheel_rpm, w4=wheel_rpm)
        time.sleep(time_needed)
        ep_chassis.drive_wheels(w1=0, w2=0, w3=0, w4=0)
        print("stop please")
        print("do the next")
        return True
    except Exception as e:
        print(f"Error in go_straight: {e}")
        ep_chassis.drive_wheels(w1=0, w2=0, w3=0, w4=0)
        return False


def turn_right(angle):
    try:
        ep_chassis.move(x=0, y=0, z=-angle, z_speed=45)
        time.sleep(4)

        return True
    except Exception as e:
        print(f"Error in turn_right: {e}")
        ep_chassis.drive_wheels(w1=0, w2=0, w3=0, w4=0)
        return False

def turn_left(angle):
    try:
        ep_chassis.move(x=0, y=0, z=angle, z_speed=45)
        time.sleep(4)
        return True
    except Exception as e:
        print(f"Error in turn_right: {e}")
        ep_chassis.drive_wheels(w1=0, w2=0, w3=0, w4=0)
        return False


def grip_object(distance_cm):
        ep_robot.gripper.open(power=50)
        time.sleep(1)
        ep_arm = ep_robot.robotic_arm
        ep_arm.move(x=80, y=0)
        time.sleep(1)
        ep_arm.move(x=0, y=-200)
        time.sleep(1)


        ep_robot.gripper.close(power=50)
        time.sleep(2)

        ep_arm.move(x=0, y=100)

        time.sleep(3)
        ep_arm.move(x=0, y=80)
        ep_arm.move(x=-100, y=-80)
        time.sleep(3)
        ep_robot.gripper.pause()

        # ep_arm.move(x=0, y=80)
        # ep_arm.move(x=-100, y=0)
        # ep_arm.move(x=0, y=-80)


def release_object(distance_cm):
        ep_arm = ep_robot.robotic_arm
        ep_arm.move(x=80, y=-100)
        time.sleep(1)



        ep_arm.move(x=0, y=-100)
        time.sleep(1)



        ep_robot.gripper.open(power=50)

        ep_arm = ep_robot.robotic_arm
        ep_arm.move(x=0, y=-60)
        ep_chassis = ep_robot.chassis
        time.sleep(0.5)
     
        ep_arm.move(x=0, y=100)

        time.sleep(3)
        ep_arm.move(x=0, y=80)
        ep_arm.move(x=-100, y=-80)
        ep_robot.gripper.close(power=50)





