import time
from llmapi import parsedGPT
from robomaster import robot
import robomove

ep_robot = robot.Robot()
ep_robot.initialize(conn_type="sta")
ep_chassis = ep_robot.chassis
ep_camera = ep_robot.camera
ep_gripper = ep_robot.gripper

# target_distance = float(None)

# def sub_data_handler(sub_info):
#     distance = sub_info
#     print("tof1:{0}".format(distance[0]))
#     target_distance = distance[0]/10

# def ir_distance():
#     ep_sensor = ep_robot.sensor
#     ep_sensor.sub_distance(freq=1, callback=sub_data_handler)
#     time.sleep(2)
#     return target_distance

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

command_mapping = {
    'go_straight': go_straight, # Need to Fix
    'go_backward': robomove.go_backward,
    'turn_left': robomove.turn_left,
    'turn_right': robomove.turn_right,
    'grip_object': robomove.grip_object,
    'release_object' :robomove.release_object
}

def execute_command(func, args):
    try:
        if args:
            return func(*args)
        return func()
    except Exception as e:
        print(f"Error executing command: {e}")
        return False

def robot_control(commands, index=0):
    if index >= len(commands):
        return

    cmd = commands[index]
    cmd_name = cmd["command"]
    parameters = cmd.get("parameters", {})

    func = command_mapping.get(cmd_name)
    if func:
        print(f"Executing {func.__name__} with parameters {parameters}")
        success = execute_command(func, list(parameters.values()))
        if success:
            print(f"Successfully executed {func.__name__}.")
            time.sleep(3)
        else:
            print(f"Failed to execute {func.__name__}.")
        robot_control(commands, index + 1)
    else:
        print(f"Unknown command: {cmd_name}")
        robot_control(commands, index + 1)

for i in range(10):

    userInput = input("Type the command: ")
    print(userInput)
    serverReceived = parsedGPT(userInput)
    print("Executing commands:", serverReceived)
    robot_control(serverReceived["commands"])





