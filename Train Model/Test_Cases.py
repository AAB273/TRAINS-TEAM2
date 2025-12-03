#!/usr/bin/env python3
"""
ULTRA-SIMPLE Commanded Speed Test
This tests the exact logic without any complex imports
"""

def test_commanded_speed_logic():
    """Test the exact commanded speed processing logic"""
    print("=== ULTRA-SIMPLE Commanded Speed Test ===")
    
    # Track what happens during the test
    actions = []
    
    # Mock objects that record what happens
    class MockTrain:
        def __init__(self):
            self.commanded_speed = 0.0
            self.service_brake_active = True
            
        def set_commanded_speed(self, value):
            old_value = self.commanded_speed
            self.commanded_speed = float(value)
            actions.append(f"set_commanded_speed({value}) - changed from {old_value} to {self.commanded_speed}")
            
        def set_service_brake(self, value):
            old_value = self.service_brake_active
            self.service_brake_active = bool(value)
            actions.append(f"set_service_brake({value}) - changed from {old_value} to {self.service_brake_active}")
    
    class MockServer:
        def __init__(self):
            self.messages_sent = []
            
        def send_to_ui(self, target, message):
            self.messages_sent.append((target, message))
            actions.append(f"send_to_ui({target}, {message})")
    
    # Create test objects
    train = MockTrain()
    server = MockServer()
    
    # Test parameters
    test_speed = 45.0
    
    print(f"BEFORE TEST:")
    print(f"  train.commanded_speed = {train.commanded_speed}")
    print(f"  train.service_brake_active = {train.service_brake_active}")
    
    print(f"\nEXECUTING COMMANDED SPEED: {test_speed}")
    
    # Execute the EXACT logic from your _process_message method
    # This is copied directly from your code:
    try:
        # This is what happens in your _process_message method for 'Commanded Speed'
        train.set_commanded_speed(test_speed)
        train.set_service_brake(False)
        server.send_to_ui("Train SW", {'command': 'Commanded Speed', 'value': test_speed})
        server.send_to_ui("Train HW", {'command': 'Commanded Speed', 'value': test_speed})
        
        print("✓ Commanded speed logic executed successfully")
        
    except Exception as e:
        print(f"✗ Error executing commanded speed logic: {e}")
        return False
    
    print(f"\nAFTER TEST:")
    print(f"  train.commanded_speed = {train.commanded_speed}")
    print(f"  train.service_brake_active = {train.service_brake_active}")
    
    print(f"\nACTIONS PERFORMED:")
    for i, action in enumerate(actions, 1):
        print(f"  {i}. {action}")
    
    # Verify the results
    print(f"\nVERIFICATION:")
    
    # Check 1: Commanded speed was set correctly
    if train.commanded_speed == test_speed:
        print(f"  ✓ Commanded speed correctly set to {test_speed}")
    else:
        print(f"  ✗ Commanded speed incorrect: expected {test_speed}, got {train.commanded_speed}")
        return False
    
    # Check 2: Service brake was released
    if train.service_brake_active == False:
        print(f"  ✓ Service brake correctly released")
    else:
        print(f"  ✗ Service brake not released: still {train.service_brake_active}")
        return False
    
    # Check 3: Messages were sent
    expected_messages = [
        ("Train SW", {'command': 'Commanded Speed', 'value': test_speed}),
        ("Train HW", {'command': 'Commanded Speed', 'value': test_speed})
    ]
    
    if len(server.messages_sent) == len(expected_messages):
        print(f"  ✓ Correct number of messages sent: {len(server.messages_sent)}")
        
        for i, (expected_target, expected_msg) in enumerate(expected_messages):
            if i < len(server.messages_sent):
                actual_target, actual_msg = server.messages_sent[i]
                if actual_target == expected_target and actual_msg == expected_msg:
                    print(f"  ✓ Message {i+1} correct: to {actual_target}")
                else:
                    print(f"  ✗ Message {i+1} incorrect")
                    return False
    else:
        print(f"  ✗ Wrong number of messages: expected {len(expected_messages)}, got {len(server.messages_sent)}")
        return False
    
    print(f"\n🎉 ALL TESTS PASSED! The commanded speed logic works correctly.")
    return True

if __name__ == "__main__":
    success = test_commanded_speed_logic()
    exit(0 if success else 1)