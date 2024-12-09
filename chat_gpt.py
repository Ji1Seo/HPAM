import openai
import main
import tof_data
from robomaster import robot
import time
import robomove
from llmapi import parsedGPT
import warnings

warnings.filterwarnings("ignore", category=FutureWarning)

class ActionPlanner:
    def __init__(self):
        # Initialize the OpenAI API key
        openai.api_key = 'insert your key'
        self.ep_robot = tof_data.initialize_robot()


    def generate_robot_movement_plan(self, user_input, image, dense_position, distance):
        # Extract distances for labels 'the coca cola' and 'the starbucks cup'
        coca_distance = None
        starbucks_distance = None
        
        for item in distance:
            if item['label'] == 'the coca cola':
                coca_distance = item['actual_distance']
            elif item['label'] == 'the starbucks cup':
                starbucks_distance = item['actual_distance']
        
        # Ensure both distances are found
        if coca_distance is None or starbucks_distance is None:
            raise ValueError("Distances for 'the coca cola' or 'the starbucks cup' not found in the provided distance data.")
        
        # Calculate the distance difference
        distance_difference = coca_distance - starbucks_distance
        
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert in robotic navigation and image analysis. "
                        "Your task is to interpret commands and analyze both the image context and object positions to create a precise, step-by-step movement plan for the robot. "
                        "The object positions are provided in the format: {'bboxes': [[x1, y1, x2, y2], ...], 'labels': ['object_name_1', 'object_name_2', ...]}. "
                        "Each object has a bounding box with coordinates corresponding to its position in the image. "
                        "To determine the necessary rotation, calculate the angle based on the object’s position relative to the robot’s current position. "
                        "Use the formula ((x1 + x2) / 2 - 320 or adjusted cola x ) / 5.9 to find the angle based on the object's center position. "
                        "If the result is positive, the robot should rotate right by the calculated angle; if negative, it should rotate left. "
                        "Each action should only contain the necessary 'rotate,' 'move forward,' or 'grip' or 'release' instruction and include the object's name and coordinates. "
                        
                        "Additionally, if the robot has already moved to an object, and a new calculation involves a second object further away, "
                        "adjust the X-axis position of the previously gripped object using the formula: "
                        "'new_x = previous_object_center_x + (distance_difference * scaling_factor)'. "
                        "Here, the `distance_difference` is calculated as the difference between the actual distances of two objects "
                        "provided in the format: 'Label: <object name>, Actual Distance: <value> meters'. "
                        "Automatically extract and calculate this difference (e.g., 'Coca Cola' - 'Starbucks Cup'). "
                        
                        "After each movement step, update the robot's position to reflect its new location, which should then influence any subsequent steps. "
                        "Each action should only contain 'rotate,' 'move forward,' or 'grip' or 'release' instruction and include the object's name and coordinates. "
                        "Focus on producing a clear and concise action plan that accounts for changes in the robot’s position after each step. "
                        "Only include commas between numbered steps to maintain clarity in the sequence."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"Generate a detailed, step-by-step action plan for the command: '{user_input}' "
                        f"using both the image context and object positions: {dense_position}. "
                        
                        f"The image data provided is: {image}. "
                        "Distances provided are as follows:\n"
                        f"Label: the coca cola\n"
                        f"Actual Distance: {coca_distance:.4f} meters\n"
                        f"Label: the starbucks cup\n"
                        f"Actual Distance: {starbucks_distance:.4f} meters\n"
                        "Automatically calculate `distance_difference` as:\n"
                        f"`distance_difference = abs({coca_distance:.4f} - {starbucks_distance:.4f})*250. "
                        "Use this `distance_difference` to adjust the Coca Cola's X-axis position by adding the `distance_difference` when calculating the angle to the Starbucks Cup. "
                        "Each action should only contain  'rotate,' 'move forward,' or 'grip' or 'release' instruction and include the object's name and coordinates. "

                        
                        "and include each object's name and coordinates in every step, adjusting for the robot's updated position as it moves. "
                        "Ensure all calculations for the robot's direction and angle are precise for accurate movement, and account for the updated position of the previously gripped object. "
                        "Ensure that each step is clearly numbered, replacing commas within numbers with periods to avoid ambiguity. Minimize the use of commas in the sequence, except as separators between steps for clarity."
                        "Do not include any actions or steps that are unnecessary for the movement."
                    )
                }
            ],
            max_tokens=1000,
            temperature=0
        )

        # Process the response to extract steps as individual action instructions
        steps = [
            step.strip() for step in response['choices'][0]['message']['content'].splitlines() 
            if step.strip() and not step.startswith('-')
        ]
        return steps

    def generate_disaster_evacuation_plan(self, user_input, image, dense_position, distance):
        coca_distance = None
        starbucks_distance = None

        # Extract distances for the objects
        for item in distance:
            if item['label'] == 'the coca cola':
                coca_distance = item['actual_distance']
            elif item['label'] == 'the starbucks cup':
                starbucks_distance = item['actual_distance']

        # OpenAI API call to generate the evacuation plan
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
               {
                "role": "system",
                "content": (
                    "You are an expert in robotic navigation and image analysis. "
                    "Your task is to interpret commands and analyze both the image context and object positions to create a precise, step-by-step movement plan for the robot. "
                    "The object positions are provided in the format: {'bboxes': [[x1, y1, x2, y2], ...], 'labels': ['object_name_1', 'object_name_2', ...]}. "
                    "Each object has a bounding box with coordinates corresponding to its position in the image. "
                    "To determine the necessary rotation, calculate the angle based on the object’s position relative to the robot’s current position. "
                    "Use the formula ((x1 + x2) / 2 - 320 or adjusted cola x) / 5.9 to find the angle based on the object's center position. "
                    "If the result is positive, the robot should rotate right by the calculated angle; if negative, it should rotate left. "
                    "Each action should only contain the necessary 'rotate,','move foward' , 'move backward,' 'grip,' or 'release' instruction and includeS the object's name and coordinates. "
                    
                    "The robot will grip the first object, move backward to safety, release the object, and then rotate to the second object. "
                    "During the second rotation, the robot should adjust its angle based on the X-axis difference between the two objects, "
                    "calculated as `delta_x = -abs(coca_cola_center_x - starbucks_cup_center_x)`. "
                    "After the second object is retrieved, the robot will move backward to the safety zone and release it. "
                    
                    "After each movement step, update the robot's position to reflect its new location, which should then influence any subsequent steps. "
                    "Ensure all calculations for the robot's direction and angle are precise for accurate movement, and account for the updated position of the previously gripped object. "
                    "Each step must include only 'rotate,','move foward','move backward,' or 'grip' or 'release' instruction, with the object's name and coordinates clearly specified."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Generate a detailed, step-by-step action plan for the command: '{user_input}' "
                    f"using both the image context and object positions: {dense_position}. "
                    
                    f"The image data provided is: {image}. "
                    "Distances provided are as follows:\n"
                    f"Label: the coca cola\n"
                    f"Actual Distance: {coca_distance:.4f} meters\n"
                    f"Label: the starbucks cup\n"
                    f"Actual Distance: {starbucks_distance:.4f} meters\n"
                    "Use this `distance_difference` to adjust the Coca Cola's X-axis position by adding the `distance_difference` when calculating the angle to the Starbucks Cup. "
                    "Each action should only contain 'rotate,' 'move backward,' 'grip,' or 'release' instruction and include the object's name and coordinates. "
                    "Ensure that the robot releases the first object before moving to the second and adjusts its rotation angle based on the X-axis difference between the two objects."
                    "Only include commas between numbered steps to maintain clarity in the sequence."

                )
            }
            ],
            max_tokens=1000,
            temperature=0
        )

        # Process the response to extract steps as individual action instructions
        steps = [
            step.strip() for step in response['choices'][0]['message']['content'].splitlines()
            if step.strip() and not step.startswith('-')
        ]
        return steps

  

    def forward_robot(self, step):
        # Use OpenAI API to check if 'move forward' command is present
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (

                        "Check if the action step contains the command 'move forward.' "
                        "If 'move forward' is present, respond with 'Move forward command detected.' "
                        "If 'move forward' is not present, respond with 'No movement command detected.'"
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"In the following action step: '{step}', check if there is a 'move forward' command. "
                        "If 'move forward' is detected, respond with 'Move forward command detected.' "
                        "If not, respond with 'No movement command detected.'"
                    )
                }
            ],
            max_tokens=1000,
            temperature=0
        )

        # Get response from GPT-4
        response_text = response['choices'][0]['message']['content'].strip()
        
        # If 'move forward' command is detected, initiate movement
        if "Move forward command detected" in response_text:
            ep_robot = tof_data.initialize_robot()
            
            try:
                print("Moving forward")
                # Start distance measurement and move forward
                tof_data.start_distance_subscription(ep_robot, freq=5, duration=10)
            finally:
                # Close robot connection
                tof_data.close_robot(ep_robot)



    def rotate_robot(self, step):
        # OpenAI API 호출
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "If the action step contains a rotation-related command with details, "
                        "return the details in the format: 'turn <direction> <angle>' (e.g., 'turn left 20'). "
                        "If no rotation-related details are found, return 'No rotation details found.'"
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"In the following action step: '{step}', check if there are any rotation-related details "
                        "(e.g., 'rotate', 'turn'). If such details are present, return only the rotation direction and angle "
                        "in the format: 'turn <direction> <angle>' (e.g., 'turn left 20'). "
                        "If no rotation-related details are found, return 'No rotation details found.'"
                    )
                }
            ],
            max_tokens=1000,
            temperature=0
        )
        
        # GPT-4로부터 응답 받아서 출력
        extracted_info = response['choices'][0]['message']['content'].strip()
        print(extracted_info)
        
        # "No rotation details found." 메시지가 있는 경우 호출 생략
        if "No rotation details found." in extracted_info:
            return
        else:
            robot = RobotController()
            return robot.main(extracted_info)
    def backward_robot(self, step):
        # OpenAI API 호출
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                    {
                "role": "system",
                "content": (
                    "You are an expert in extracting specific movement commands from instructions. "
                    "Your task is to check if the input contains any backward movement commands such as "
                    "'move backward,' 'move back,' 'reverse,' 'retreat,' or equivalent phrases. "
                    "If a backward movement command is present, extract the object name and associated instructions, "
                    "and respond in the following format: "
                    "'Move Backward: <Object Name>, <Instructions>' (e.g., 'Move Backward: Coca Cola, Move at least 1.5 meters from the fire hazard'). "
                    "If no such command is present, respond with 'No backward movement detected.' "
                    "Ensure your response only contains the exact extracted information or the detection result."
                )
            },
            {
                "role": "user",
                "content": (
                    f"In the following action step: '{step}', check for any backward movement commands. "
                    "If commands such as 'move backward,' 'move back,' 'reverse,' 'retreat,' or equivalent phrases are detected, "
                    "extract the object name and associated instructions. Respond in the format: "
                    "'Move Backward: <Object Name>, <Instructions>'. "
                    "If no such commands are present, respond with 'No backward movement detected.'"
                )
            }
            ],
            max_tokens=1000,
            temperature=0  # Slightly lower temperature for more deterministic responses
        )

        # GPT-4로부터 응답 받아서 출력
        extracted_info = response['choices'][0]['message']['content'].strip()
        print(extracted_info)

        # "No backward movement detected." 메시지가 있는 경우 호출 생략
        if "No backward movement detected" in extracted_info:
            return

        else:  # 뒤로 이동 명령 실행
            robot = RobotController()
            return robot.main("move backward 5 and turn right 40 and release 20 and turn left 45")



    def grip_robot(self, step):
# OpenAI API 호출
        response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
        {
        "role": "system",
        "content": (
        "If an object and coordinates are mentioned with grip-related details, "
        "return them in the format: 'Object: <object_name>, Coordinates: <coordinates>'. "
        "If no grip-related details are found, return 'No grip details found.'"
        )
        },
        {
        "role": "user",
        "content": (
        f"In the following action step: '{step}', check if there are any grip-related details "
        "(e.g., 'grip', 'hold', 'grab','picking'). If such details are present, return the object and its coordinates in the format: "
        "'Object: <object_name>, Coordinates: <coordinates>'. "
        "If no grip-related details are found, return 'No grip details found.'"
        )
        }
        ],
        max_tokens=1000,
        temperature=0.5
        )

        # GPT-4로부터 응답 받아서 출력
        extracted_info = response['choices'][0]['message']['content'].strip()
        print(extracted_info)

        # "No grip details found." 메시지가 있는 경우 호출 생략
        if "No grip details found." in extracted_info:
            return

            
        else:   # 추출된 정보에서 객체 이름과 좌표를 분리
            robot = RobotController()
            return robot.main("grip 50")
        
    def release_robot(self, step):
        # OpenAI API 호출
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
               
                          {
                    "role": "system",
                    "content": (
                        "If an object and coordinates are mentioned with release-related details, "
                        "return them in the format: 'Object: <object_name>, Coordinates: <coordinates>'. "
                        "If no release-related details are found, return 'No release details found.'"
                    )
                },
                {
                    "role": "user",
                    "content": (
                        f"In the following action step: '{step}', check if there are any release-related details "
                        "(e.g., 'release', 'let go'). If such details are present, return the object and its coordinates in the format: "
                        "'Object: <object_name>, Coordinates: <coordinates>'. "
                        "If no release-related details are found, return 'No release details found.'"
                    )
                }
            ],
            max_tokens=1000,
            temperature=0
        )

        # GPT-4로부터 응답 받아서 출력
        extracted_info = response['choices'][0]['message']['content'].strip()
        print(extracted_info)

        # "No release details found." 메시지가 있는 경우 호출 생략
        if "No release details found." in extracted_info:
            return

        else:
            # 추출된 정보에서 객체 이름과 좌표를 분리하여 로봇 release 명령 실행
            robot = RobotController()
            return robot.main("release 50")



    def analyze_with_gpt4(self, vlm_output):
        gpt4_response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are an assistant that analyzes outputs from a vision-language model. You always assume that any indication of fire, flames, smoke, or burning in the given output represents a fire hazard, and respond with 'yes'. Additionally, you analyze if the robot is being harmed or if there are any disaster situations such as floods, earthquakes, or other hazards."
                },
                {
                    "role": "user",
                    "content": f"Given the following output from a vision-language model: '{vlm_output}', is there any aggressive behavior or disaster situation present? If fire, flames, or smoke are mentioned, always answer 'yes' and provide a brief explanation of the situation."
                }
            ],
            max_tokens=150,
            temperature=0.5
        )

        analysis = gpt4_response['choices'][0]['message']['content']
        print(analysis)
        return analysis




                




    def plan_actions(self, action_steps):
    
    

            for step in action_steps:

                self.rotate_robot(step)
                self.forward_robot(step)
                self.grip_robot(step)
                self.release_robot(step)
                self.backward_robot(step)
        

                
                 

                
                 

                
            
            
            # self.execute_action(action_type, object_name, position)

    def parse_step(self, step):
        # Simplified parsing of an action step (step format: "Move [object] to [position]")
        words = step.split()
        action_type = words[0]
        object_name = words[1]
        position = words[-1]  # e.g., "table" in "Move juice to table"
        return action_type, object_name, position

    def execute_action(self, action_type, object_name, position):
        # Detailed execution of a single action based on its type
        if action_type == "Move":
            if self.locate_object(object_name):
                self.move_to_position(object_name, position)
            else:
                print(f"Failed to locate {object_name} for moving.")



    def move_to_position(self, object_name, position):
        # Define robot movement commands based on Florence model output for object location
        print(f"Moving {object_name} to {position}.")
        # Here, add detailed robot control code for moving objects

    def check_completion(self, target_position):
        # Verify if the object has reached the intended position
        # Could involve additional image analysis or sensor data if available
        pass
class RobotController:
    def __init__(self):
        self.ep_robot = robot.Robot()
        self.ep_robot.initialize(conn_type="sta")
        self.ep_chassis = self.ep_robot.chassis
        self.ep_camera = self.ep_robot.camera
        self.ep_gripper = self.ep_robot.gripper

        # Command mapping dictionary for various robot actions
        self.command_mapping = {
            'go_straight': self.go_straight,
            'go_backward': robomove.go_backward,
            'turn_left': robomove.turn_left,
            'turn_right': robomove.turn_right,
            'grip_object': robomove.grip_object,
            "release_object" : robomove.release_object
        }

    def go_straight(self, distance_cm):
        try:
            distance_m = distance_cm / 100.0
            linear_speed = 0.4
            time_needed = distance_m / linear_speed
            wheel_diameter = 0.100
            wheel_circumference = 3.14 * wheel_diameter
            wheel_rpm = (linear_speed * 60) / wheel_circumference
            wheel_rpm = -int(wheel_rpm)
            self.ep_chassis.drive_wheels(w1=wheel_rpm, w2=wheel_rpm, w3=wheel_rpm, w4=wheel_rpm, timeout=time_needed)
            return True
        except Exception as e:
            print(f"Error in go_straight: {e}")
            self.ep_chassis.drive_wheels(w1=0, w2=0, w3=0, w4=0)
            return False

    def execute_command(self, func, args):
        try:
            if args:
                return func(*args)
            return func()
        except Exception as e:
            print(f"Error executing command: {e}")
            return False

    def robot_control(self, commands, index=0):
        if index >= len(commands):
            return

        cmd = commands[index]
        cmd_name = cmd["command"]
        parameters = cmd.get("parameters", {})

        func = self.command_mapping.get(cmd_name)
        if func:
            print(f"Executing {func.__name__} with parameters {parameters}")
            success = self.execute_command(func, list(parameters.values()))
            print(success)
            if success:
                print(f"Successfully executed {func.__name__}.")
                time.sleep(3)
            else:
                print(f"Failed to execute {func.__name__}.")
            self.robot_control(commands, index + 1)
        else:
            print(f"Unknown command: {cmd_name}")
            self.robot_control(commands, index + 1)

    def main(self, user_input):
        serverReceived = parsedGPT(user_input)
        print("Executing commands:", serverReceived)
        self.robot_control(serverReceived["commands"])

