from wdapy.actions import TouchActions, PointerAction, Origin
from unittest.mock import MagicMock
from wdapy import AppiumClient
from wdapy._proto import POST


def test_perform_actions():
    # Create a mock client
    client = AppiumClient("http://localhost:8100")
    client.session_request = MagicMock(return_value={"value": None})
    
    # Create test actions
    finger1 = TouchActions.pointer("finger1", actions=[
        PointerAction.move(100, 200),
        PointerAction.down(),
        PointerAction.move(150, 250, duration=500, origin=Origin.POINTER),
        PointerAction.up()
    ])
    
    # Call the method being tested
    client.perform_actions([finger1])
    
    # Verify the session_request was called with correct parameters
    client.session_request.assert_called_once()
    args = client.session_request.call_args.args
    
    # Check that the method, endpoint and payload structure are correct
    assert args[0] == POST
    assert args[1] == "/actions"
    
    # Verify the payload contains the expected actions
    payload = args[2]
    assert "actions" in payload
    actions = payload["actions"]
    assert len(actions) == 1
    
    # Verify the first action's properties
    action = actions[0]
    assert action["type"] == "pointer"
    assert action["id"] == "finger1"
    assert "parameters" in action
    assert action["parameters"]["pointerType"] == "touch"
    
    # Verify the action sequence
    action_sequence = action["actions"]
    assert len(action_sequence) == 4
    
    # Check first action (move)
    assert action_sequence[0]["type"] == "pointerMove"
    assert action_sequence[0]["x"] == 100
    assert action_sequence[0]["y"] == 200
    
    # Check second action (down)
    assert action_sequence[1]["type"] == "pointerDown"
    
    # Check third action (move with duration and origin)
    assert action_sequence[2]["type"] == "pointerMove"
    assert action_sequence[2]["x"] == 150
    assert action_sequence[2]["y"] == 250
    assert action_sequence[2]["duration"] == 500
    assert action_sequence[2]["origin"] == "pointer"
    
    # Check fourth action (up)
    assert action_sequence[3]["type"] == "pointerUp"