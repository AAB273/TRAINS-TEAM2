import unittest
from unittest.mock import MagicMock, patch
import sys
import timer

# Mock external dependencies
sys.modules['TrainSocketServer'] = MagicMock()
sys.modules['clock'] = MagicMock()
sys.modules['pygame'] = MagicMock()
sys.modules['tkinter'] = MagicMock()
sys.modules['tkinter.ttk'] = MagicMock()
sys.modules['PIL'] = MagicMock()
sys.modules['PIL.Image'] = MagicMock()
sys.modules['PIL.ImageTk'] = MagicMock()
sys.modules['GreenLineData'] = MagicMock()
sys.modules['RedLineData'] = MagicMock()

from train_data import Train, TrainManager


class Testing(unittest.TestCase):
    """Test that the passenger UI correctly processes socket server messages to set specific train variables.
       As well as testing moving train functionality through each of the functions"""
    
    def setUp(self):
        """Initialize train manager and get a train for testing."""
        self.train_manager = TrainManager(14)
        self.train = self.train_manager.getTrain(1)
        self.train.deployed = True
        self.train.active = True
    
    def test_commanded_speed_socket_message(self):
        """
        Test that when a 'Commanded Speed' command is received via socket,
        the train's commanded speed is set correctly.
        """
        # Simulate the socket message
        message = {
            'command': 'Commanded Speed',
            'value': 15.0,
            'train_id': 1
        }
        
        # Simulate what the UI's _processMessage method does
        command = message.get('command')
        value = message.get('value')
        train_id = message.get('train_id')
        
        train = self.train_manager.getTrain(train_id)
        
        if command == 'Commanded Speed':
            train.setCommandedSpeed(value)
        
        # Verify the train has the correct commanded speed
        print("\nTesting Commanded Speed")
        try:
            self.assertEqual(train.commandedSpeed, 15.0)
            print("Test passed: Commanded speed set correctly")
        except AssertionError:
            print("Test failed: Commanded speed not set correctly")
            raise

    def test_commanded_authority_socket_message(self):
        """
        Test that when a 'Commanded Authority' command is received via socket,
        the train's commanded Authority is set correctly.
        """
        # Simulate the socket message
        message = {
            'command': 'Commanded Authority',
            'value': 3.0,
            'train_id': 1
        }
        
        # Simulate what the UI's _processMessage method does
        command = message.get('command')
        value = message.get('value')
        train_id = message.get('train_id')
        
        train = self.train_manager.getTrain(train_id)
        
        if command == 'Commanded Authority':
            train.setAuthority(value)
        
        # Verify the train has the correct commanded speed
        print("\nTesting Commanded Authority")
        try:
            self.assertEqual(train.commandedAuthority, 3.0)
            print("Test passed: Commanded Authority set correctly")
        except AssertionError:
            print("Test failed: Commanded Authority not set correctly")
            raise

    def test_block_occupancy_socket_message(self):
        """
        Test that when a 'Block Occupancy' command is received via socket,
        the train's Block Occupancy is set correctly.
        """
        # Simulate the socket message
        message = {
            'command': 'Block Occupancy',
            'value': 5.0,
            'train_id': 1
        }
        
        # Simulate what the UI's _processMessage method does
        command = message.get('command')
        value = message.get('value')
        train_id = message.get('train_id')
        
        train = self.train_manager.getTrain(train_id)
        
        if command == 'Block Occupancy':
            train.setBlock(value)
        
        # Verify the train has the correct commanded speed
        print("\nTesting Block Occupancy")
        try:
            self.assertEqual(train.block, 5.0)
            print("Test passed:", message['command'], "set correctly")
        except AssertionError:
            print("Test failed:", message['command'], "not set correctly")
            raise

    def test_doors_lights_socket_message(self):
        """
        Test that when a 'Doors and Ligghts respective' commands are received via socket,
        """
        # Simulate the socket message
        message = {
            'command': 'Right Door Signal',
            'value': True,
            'train_id': 1
        }
        
        # Simulate what the UI's _processMessage method does
        command = message.get('command')
        value = message.get('value')
        train_id = message.get('train_id')
        
        train = self.train_manager.getTrain(train_id)
        
        if command == 'Right Door Signal':
            train.setRightDoor(value)
        
        # Verify the train has the correct commanded speed
        print("\nTesting message",message['command'])
        try:
            self.assertEqual(train.rightDoorOpen, True)
            print("Test passed:", message['command'], "set correctly")
        except AssertionError:
            print("Test failed:", message['command'], "not set correctly")
            raise


        message = {
            'command': 'Left Door Signal',
            'value': True,
            'train_id': 1
        }
        

        # Simulate what the UI's _processMessage method does
        command = message.get('command')
        value = message.get('value')
        train_id = message.get('train_id')
        
        train = self.train_manager.getTrain(train_id)
        
        if command == 'Left Door Signal':
            train.setLeftDoor(value)
        
        # Verify the train has the correct commanded speed
        print("\nTesting message",message['command'])
        try:
            self.assertEqual(train.leftDoorOpen, True)
            print("Test passed:", message['command'], "set correctly")
        except AssertionError:
            print("Test failed:", message['command'], "not set correctly")
            raise


        message = {
            'command': 'Headlights',
            'value': True,
            'train_id': 1
        }
        
        # Simulate what the UI's _processMessage method does
        command = message.get('command')
        value = message.get('value')
        train_id = message.get('train_id')
        
        train = self.train_manager.getTrain(train_id)
        
        if command == 'Headlights':
            train.setHeadlights(value)
        
        # Verify the train has the correct commanded speed
        print("\nTesting message",message['command'])
        try:
            self.assertEqual(train.headlightsOn, True)
            print("Test passed:", message['command'], "set correctly")
        except AssertionError:
            print("Test failed:", message['command'], "not set correctly")
            raise

        message = {
            'command': 'Cabin Lights',
            'value': True,
            'train_id': 1
        }
        
        # Simulate what the UI's _processMessage method does
        command = message.get('command')
        value = message.get('value')
        train_id = message.get('train_id')
        
        train = self.train_manager.getTrain(train_id)
        
        if command == 'Cabin Lights':
            train.setInteriorLights(value)
        
        # Verify the train has the correct commanded speed
        print("\nTesting message",message['command'])
        try:
            self.assertEqual(train.interiorLightsOn, True)
            print("Test passed:", message['command'], "set correctly")
        except AssertionError:
            print("Test failed:", message['command'], "not set correctly")
            raise


    def test_service_brake_socket_message(self):
        """
        Test that when a 'Service Brake' command is received through the socket, the train correctly sets its service brake bool.
        """
        # Simulate the socket message
        message = {
            'command': 'Service Brake',
            'value': True,
            'train_id': 1
        }
        
        # Simulate what the UI's _processMessage method does
        command = message.get('command')
        value = message.get('value')
        train_id = message.get('train_id')
        
        train = self.train_manager.getTrain(train_id)
        
        if command == 'Service Brake':
            train.setServiceBrake(value)
        
        # Verify the train has the correct commanded speed
        print("\nTesting message",message['command'])
        try:
            self.assertEqual(train.serviceBrakeActive, True)
            print("Test passed:", message['command'], "set correctly")
        except AssertionError:
            print("Test failed:", message['command'], "not set correctly")
            raise

    def test_e_brake_socket_message(self):
        """
        Test that when a 'Service Brake' command is received through the socket, the train correctly sets its service brake bool.
        """
        # Simulate the socket message
        message = {
            'command': 'Emergency Brake',
            'value': True,
            'train_id': 1
        }
        
        # Simulate what the UI's _processMessage method does
        command = message.get('command')
        value = message.get('value')
        train_id = message.get('train_id')
        
        train = self.train_manager.getTrain(train_id)
        
        if command == 'Emergency Brake':
            train.setEmergencyBrake(value)
        
        # Verify the train has the correct commanded speed
        print("\nTesting message",message['command'])
        try:
            self.assertEqual(train.emergencyBrakeActive, True)
            print("Test passed:", message['command'], "set correctly")
        except AssertionError:
            print("Test failed:", message['command'], "not set correctly")
            raise
    
    
    def test_ui_100ms_updates(self):
        """Test exactly what happens with 100ms UI updates."""
        # Enable movement
        self.train.powerCommand = 50000
        self.train.serviceBrakeActive = False
        
        # Store initial values
        initial_speed = self.train.speed
        
        print("\n=== Testing 100ms UI Updates ===")
        
        # Simulate 1 second of UI updates (10 x 100ms)
        for i in range(10):
            self.train.calculateForceSpeedAccelerationDistance(dt=0.1)
            print(f"After {i+1} updates: Speed={self.train.speed:.2f} m/s")
        
        # Assertions
        self.assertGreater(self.train.speed, initial_speed,
                          "Train should accelerate with power applied")
        
        print(f"\nResults:")
        print(f"  Speed increased from {initial_speed:.1f} to {self.train.speed:.1f} m/s")
        
        return True

    def test_ui_100ms_updates_with_speed_limit(self):
        """Test exactly what happens with 100ms UI updates."""
        # Enable movement
        self.train.powerCommand = 50000
        self.train.serviceBrakeActive = False
        self.train.speedLimitMps = 0.5
        
        # Store initial values
        initial_speed = self.train.speed
        
        print("\n=== Testing 100ms UI Updates ===")
        
        # Simulate 1 second of UI updates (10 x 100ms)
        for i in range(10):
            self.train.calculateForceSpeedAccelerationDistance(dt=0.1)
            print(f"After {i+1} updates: Speed={self.train.speed:.2f} m/s")
        
        # Assertions
        self.assertGreater(self.train.speed, initial_speed,
                          "Train should accelerate with power applied")
        
        print(f"\nResults:")
        print(f"  Speed increased from {initial_speed:.1f} to {self.train.speed:.1f} m/s")
        
        return True
    
    def test_ui_100ms_updates_with_murphy_failures(self):
        """Test exactly what happens with 100ms UI updates."""
        # Enable movement
        self.train.powerCommand = 50000
        self.train.serviceBrakeActive = False
        self.train.speedLimitMps = 0.5
        
        # Store initial values
        initial_speed = self.train.speed
        
        print("\n=== Testing 100ms UI Updates Power Failure ===")
        
        # Simulate 1 second of UI updates (10 x 100ms)
        for i in range(10):
            self.train.calculateForceSpeedAccelerationDistance(dt=0.1)
            print(f"After {i+1} updates: Speed={self.train.speed:.2f} m/s")
        
        self.train.setEngineFailure(True)
	    self.train.setPowerCommand(0)
	    self.train.setAcceleration(0)
        
        print(f"\nResults:")
        print(f"  Speed increased from {initial_speed:.1f} to {self.train.speed:.1f} m/s")
        
        return True

if __name__ == '__main__':
    unittest.main()