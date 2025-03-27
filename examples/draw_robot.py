from wdapy import AppiumClient, AppiumUSBClient
from wdapy.actions import TouchActions, PointerAction, Origin


def draw_robot(client: AppiumClient):
    # Calculate usable area with 20% padding
    width, height = client.window_size()
    padding_x = width * 0.2
    padding_y = height * 0.2
    usable_width = width - 2 * padding_x
    usable_height = height - 2 * padding_y
    
    # Starting position (center of usable area)
    center_x = width / 2
    center_y = height / 2
    
    # Draw the robot head (square)
    head_size = usable_width * 0.3
    head_top = center_y - head_size * 0.8
    head_left = center_x - head_size / 2
    
    # Draw the head (square)
    head = TouchActions.pointer("robot_finger", actions=[
        PointerAction.move(int(head_left), int(head_top), origin=Origin.VIEWPORT),
        PointerAction.down(),
        PointerAction.move(int(head_left + head_size), int(head_top), origin=Origin.VIEWPORT),
        PointerAction.move(int(head_left + head_size), int(head_top + head_size), origin=Origin.VIEWPORT),
        PointerAction.move(int(head_left), int(head_top + head_size), origin=Origin.VIEWPORT),
        PointerAction.move(int(head_left), int(head_top), origin=Origin.VIEWPORT),
        PointerAction.up()
    ])
    
    # Draw the eyes (two small circles)
    eye_left = TouchActions.pointer("robot_finger", actions=[
        # Left eye
        PointerAction.move(int(head_left + head_size * 0.25), int(head_top + head_size * 0.3), origin=Origin.VIEWPORT),
        PointerAction.down(),
        PointerAction.pause(500),
        PointerAction.up()
    ])
    eye_right = TouchActions.pointer("robot_finger", actions=[
        # Right eye
        PointerAction.move(int(head_left + head_size * 0.75), int(head_top + head_size * 0.3), origin=Origin.VIEWPORT),
        PointerAction.down(),
        PointerAction.pause(500),
        PointerAction.up()
    ])
    
    # Draw the mouth (horizontal line)
    mouth = TouchActions.pointer("robot_finger", actions=[
        PointerAction.move(int(head_left + head_size * 0.25), int(head_top + head_size * 0.7), origin=Origin.VIEWPORT),
        PointerAction.down(),
        PointerAction.move(int(head_left + head_size * 0.75), int(head_top + head_size * 0.7), origin=Origin.VIEWPORT),
        PointerAction.up()
    ])
    
    # Draw the body (rectangle)
    body = TouchActions.pointer("robot_finger", actions=[
        PointerAction.move(int(center_x - head_size * 0.4), int(head_top + head_size), origin=Origin.VIEWPORT),
        PointerAction.down(),
        PointerAction.move(int(center_x + head_size * 0.4), int(head_top + head_size), origin=Origin.VIEWPORT),
        PointerAction.move(int(center_x + head_size * 0.4), int(head_top + head_size * 2), origin=Origin.VIEWPORT),
        PointerAction.move(int(center_x - head_size * 0.4), int(head_top + head_size * 2), origin=Origin.VIEWPORT),
        PointerAction.move(int(center_x - head_size * 0.4), int(head_top + head_size), origin=Origin.VIEWPORT),
        PointerAction.up()
    ])
    
    # Draw the arms (two horizontal lines)
    arm_left = TouchActions.pointer("robot_finger", actions=[
        # Left arm
        PointerAction.move(int(center_x - head_size * 0.4), int(head_top + head_size * 1.3), origin=Origin.VIEWPORT),
        PointerAction.down(),
        PointerAction.move(int(center_x - head_size * 0.9), int(head_top + head_size * 1.3), origin=Origin.VIEWPORT),
        PointerAction.up()
    ])
    arm_right = TouchActions.pointer("robot_finger", actions=[
        PointerAction.move(int(center_x + head_size * 0.4), int(head_top + head_size * 1.3), origin=Origin.VIEWPORT),
        PointerAction.down(),
        PointerAction.move(int(center_x + head_size * 0.9), int(head_top + head_size * 1.3), origin=Origin.VIEWPORT),
        PointerAction.up()
    ])
    
    # Draw the legs (two vertical lines)
    leg_left = TouchActions.pointer("robot_finger", actions=[
        PointerAction.move(int(center_x - head_size * 0.2), int(head_top + head_size * 2), origin=Origin.VIEWPORT),
        PointerAction.down(),
        PointerAction.move(int(center_x - head_size * 0.2), int(head_top + head_size * 2.5), origin=Origin.VIEWPORT),
        PointerAction.up()
    ])
    leg_right = TouchActions.pointer("robot_finger", actions=[
        PointerAction.move(int(center_x + head_size * 0.2), int(head_top + head_size * 2), origin=Origin.VIEWPORT),
        PointerAction.down(),
        PointerAction.move(int(center_x + head_size * 0.2), int(head_top + head_size * 2.5), origin=Origin.VIEWPORT),
        PointerAction.up()
    ])
    
    for action in [head, eye_left, eye_right, mouth, body, arm_left, arm_right, leg_left, leg_right]:
        client.perform_actions([action])
    

if __name__ == '__main__':
    client = AppiumUSBClient()
    draw_robot(client)
    
    