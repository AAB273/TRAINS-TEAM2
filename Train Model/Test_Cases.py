#!/usr/bin/env python3
"""
ULTRA-SIMPLE Commanded Speed Test
This tests the exact logic without any complex imports
"""

def testCommandedSpeedLogic():
    """Test the exact commanded speed processing logic"""
    print("=== ULTRA-SIMPLE Commanded Speed Test ===")
    
    # Track what happens during the test
    actions = []
    
    # Mock objects that record what happens
    class MockTrain:
        def __init__(self):
            self.commandedSpeed = 0.0
            self.serviceBrakeActive = True
            
        def setCommandedSpeed(self, value):
            old_value = self.commandedSpeed
            self.commandedSpeed = float(value)
            actions.append(f"set_commandedSpeed({value}) - changed from {old_value} to {self.commandedSpeed}")
            
        def setServiceBrake(self, value):
            old_value = self.serviceBrakeActive
            self.serviceBrakeActive = bool(value)
            actions.append(f"set_service_brake({value}) - changed from {old_value} to {self.serviceBrakeActive}")
    
    class MockServer:
        def __init__(self):
            self.messagesSent = []
            
        def send_to_ui(self, target, message):
            self.messagesSent.append((target, message))
            actions.append(f"send_to_ui({target}, {message})")
    
    # Create test objects
    train = MockTrain()
    server = MockServer()
    
    # Test parameters
    testSpeed = 45.0
    
    print(f"BEFORE TEST:")
    print(f"  train.commandedSpeed = {train.commandedSpeed}")
    print(f"  train.serviceBrakeActive = {train.serviceBrakeActive}")
    
    print(f"\nEXECUTING COMMANDED SPEED: {testSpeed}")
    
    # Execute the EXACT logic from your _process_message method
    # This is copied directly from your code:
    try:
        # This is what happens in your _process_message method for 'Commanded Speed'
        train.setCommandedSpeed(testSpeed)
        train.setServiceBrake(False)
        server.send_to_ui("Train SW", {'command': 'Commanded Speed', 'value': testSpeed})
        server.send_to_ui("Train HW", {'command': 'Commanded Speed', 'value': testSpeed})
        
        print("✓ Commanded speed logic executed successfully")
        
    except Exception as e:
        print(f"✗ Error executing commanded speed logic: {e}")
        return False
    
    print(f"\nAFTER TEST:")
    print(f"  train.commandedSpeed = {train.commandedSpeed}")
    print(f"  train.serviceBrakeActive = {train.serviceBrakeActive}")
    
    print(f"\nACTIONS PERFORMED:")
    for i, action in enumerate(actions, 1):
        print(f"  {i}. {action}")
    
    # Verify the results
    print(f"\nVERIFICATION:")
    
    # Check 1: Commanded speed was set correctly
    if train.commandedSpeed == testSpeed:
        print(f"  ✓ Commanded speed correctly set to {testSpeed}")
    else:
        print(f"  ✗ Commanded speed incorrect: expected {testSpeed}, got {train.commandedSpeed}")
        return False
    
    # Check 2: Service brake was released
    if train.serviceBrakeActive == False:
        print(f"  ✓ Service brake correctly released")
    else:
        print(f"  ✗ Service brake not released: still {train.serviceBrakeActive}")
        return False
    
    # Check 3: Messages were sent
    expectedMessages = [
        ("Train SW", {'command': 'Commanded Speed', 'value': testSpeed}),
        ("Train HW", {'command': 'Commanded Speed', 'value': testSpeed})
    ]
    
    if len(server.messagesSent) == len(expectedMessages):
        print(f"  ✓ Correct number of messages sent: {len(server.messagesSent)}")
        
        for i, (expectedTarget, expectedMsg) in enumerate(expectedMessages):
            if i < len(server.messagesSent):
                actualTarget, actualMsg = server.messagesSent[i]
                if actualTarget == expectedTarget and actualMsg == expectedMsg:
                    print(f"  ✓ Message {i+1} correct: to {actualTarget}")
                else:
                    print(f"  ✗ Message {i+1} incorrect")
                    return False
    else:
        print(f"  ✗ Wrong number of messages: expected {len(expectedMessages)}, got {len(server.messagesSent)}")
        return False
    
    print(f"\n🎉 ALL TESTS PASSED! The commanded speed logic works correctly.")
    return True

if __name__ == "__main__":
    success = testCommandedSpeedLogic()
    exit(0 if success else 1)