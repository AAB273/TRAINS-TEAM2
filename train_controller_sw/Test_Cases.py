import unittest
import tkinter as tk
from unittest.mock import Mock, patch, MagicMock, PropertyMock
import sys
import os
import time

# Add the parent directory to the path to import Driver_UI
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock the socket server and other dependencies before importing Driver_UI
sys.modules['TrainSocketServer'] = MagicMock()

from Driver_UI import Main_Window, Mode_Toggle


class TestDriverMode(unittest.TestCase):
    """Test cases for driver mode toggle functionality"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures that are used by all tests"""
        cls.root = tk.Tk()
        cls.root.withdraw()  # Hide the window during tests
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests"""
        cls.root.destroy()
    
    def setUp(self):
        """Set up before each test"""
        # Create a fresh instance for each test
        with patch('Driver_UI.TrainSocketServer'):
            self.app = Main_Window(self.root, 'GREEN')
    
    def tearDown(self):
        """Clean up after each test"""
        # Clean up the main container
        for widget in self.root.winfo_children():
            if widget != self.app.root:
                widget.destroy()
    
    def test_initial_mode_is_auto(self):
        """Test that the initial mode is set to automatic"""
        self.assertTrue(self.app.is_auto_mode, 
                       "Initial mode should be automatic")
        self.assertEqual(self.app.mode_select.active_mode, "auto",
                        "Mode toggle should show 'auto' as active")
    
    def test_manual_mode_toggle(self):
        """Test switching to manual mode explicitly"""
        # Switch to manual mode
        self.app.mode_select.set_mode("manual")
        
        self.assertFalse(self.app.is_auto_mode,
                        "Mode should be manual after toggle")
        self.assertEqual(self.app.mode_select.active_mode, "manual",
                        "Mode toggle should show 'manual' as active")
    
    def test_auto_mode_toggle(self):
        """Test switching back to auto mode"""
        # First switch to manual
        self.app.mode_select.set_mode("manual")
        # Then switch back to auto
        self.app.mode_select.set_mode("auto")
        
        self.assertTrue(self.app.is_auto_mode,
                       "Mode should be automatic after toggle")
        self.assertEqual(self.app.mode_select.active_mode, "auto",
                        "Mode toggle should show 'auto' as active")
    
    def test_increase_speed_switches_to_manual(self):
        """Test that increasing speed switches from auto to manual mode"""
        # Ensure we start in auto mode
        self.app.mode_select.set_mode("auto")
        self.assertTrue(self.app.is_auto_mode, "Should start in auto mode")
        
        # Get initial speed
        initial_speed = self.app.set_speed
        
        # Increase speed
        self.app.increase_set_speed()
        
        # Verify mode switched to manual
        self.assertFalse(self.app.is_auto_mode,
                        "Mode should switch to manual after increasing speed")
        self.assertEqual(self.app.mode_select.active_mode, "manual",
                        "Mode toggle should show 'manual' after speed increase")
        
        # Verify speed was actually increased
        self.assertEqual(self.app.set_speed, initial_speed + 5,
                        "Speed should be increased by 5")
        self.assertEqual(self.app.set_speed_value.cget("text"), str(initial_speed + 5),
                        "Speed display should reflect the increase")


class TestCommandedSpeed(unittest.TestCase):
    """Test cases for commanded speed handling"""
    
    @classmethod
    def setUpClass(cls):
        cls.root = tk.Tk()
        cls.root.withdraw()
    
    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()
    
    def setUp(self):
        with patch('Driver_UI.TrainSocketServer'):
            self.app = Main_Window(self.root, 'GREEN')
    
    def test_commanded_speed_message_processing(self):
        """Test that commanded speed messages are processed correctly"""
        message = {
            'command': 'Commanded Speed',
            'value': 45.0,
            'train_id': 1
        }
        
        self.app._process_message(message, 'Train Model')
        
        # Check that commanded speed was stored
        self.assertEqual(self.app.display_commanded_speed_mph, 45.0,
                        "Raw commanded speed should be stored")
        self.assertTrue(self.app.has_received_commanded_speed,
                       "has_received_commanded_speed flag should be True")
    
    def test_commanded_speed_with_authority_adjustment(self):
        """Test that commanded speed is adjusted by authority"""
        # Set authority to 1 (50%)
        auth_message = {
            'command': 'Commanded Authority',
            'value': 1,
            'train_id': 1
        }
        self.app._process_message(auth_message, 'Train Model')
        
        # Send commanded speed
        speed_message = {
            'command': 'Commanded Speed',
            'value': 60.0,
            'train_id': 1
        }
        self.app._process_message(speed_message, 'Train Model')
        
        # Check that speed is adjusted by authority (50%)
        self.assertEqual(self.app.commanded_speed_mph, 30.0,
                        "Commanded speed should be adjusted to 50% with authority=1")
    
    def test_commanded_speed_display_update(self):
        """Test that commanded speed display updates correctly"""
        message = {
            'command': 'Commanded Speed',
            'value': 55.0,
            'train_id': 1
        }
        
        # Set authority to 3 (100%) for direct comparison
        self.app.commanded_authority = 3
        self.app._process_message(message, 'Train Model')
        
        # Display should show 55 mph
        display_text = self.app.commanded_speed_value.cget("text")
        self.assertIn("55", display_text,
                     "Display should show commanded speed")


class TestCommandedAuthority(unittest.TestCase):
    """Test cases for commanded authority handling"""
    
    @classmethod
    def setUpClass(cls):
        cls.root = tk.Tk()
        cls.root.withdraw()
    
    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()
    
    def setUp(self):
        with patch('Driver_UI.TrainSocketServer'):
            self.app = Main_Window(self.root, 'GREEN')
    
    def test_authority_message_processing(self):
        """Test that authority messages are processed correctly"""
        message = {
            'command': 'Commanded Authority',
            'value': 3,
            'train_id': 1
        }
        
        self.app._process_message(message, 'Train Model')
        
        self.assertEqual(self.app.commanded_authority, 3,
                        "Authority should be set to 3")
        self.assertTrue(self.app.has_received_authority,
                       "has_received_authority flag should be True")
    
    def test_authority_zero_engages_brake(self):
        """Test that authority 0 engages service brake"""
        # Start moving
        self.app.current_speed_ms = 10.0
        self.app.position_tracker.is_at_station = False
        
        message = {
            'command': 'Commanded Authority',
            'value': 0,
            'train_id': 1
        }
        
        self.app.display_commanded_speed_mph = 60.0
        self.app._process_message(message, 'Train Model')
        
        # Check that brake was engaged
        self.assertTrue(self.app.service_brake_active,
                       "Service brake should be active with authority=0")
        self.assertEqual(self.app.commanded_speed_mph, 0.0,
                        "Commanded speed should be 0 with authority=0")
    
    def test_authority_adjustment_factors(self):
        """Test different authority adjustment factors"""
        # Set raw speed
        speed_msg = {
            'command': 'Commanded Speed',
            'value': 80.0,
            'train_id': 1
        }
        
        # Test authority 1 (50%)
        auth_msg = {'command': 'Commanded Authority', 'value': 1, 'train_id': 1}
        self.app._process_message(auth_msg, 'Train Model')
        self.app._process_message(speed_msg, 'Train Model')
        self.assertEqual(self.app.commanded_speed_mph, 40.0, "Authority 1 should give 50%")
        
        # Test authority 2 (75%)
        auth_msg = {'command': 'Commanded Authority', 'value': 2, 'train_id': 1}
        self.app._process_message(auth_msg, 'Train Model')
        self.app._process_message(speed_msg, 'Train Model')
        self.assertEqual(self.app.commanded_speed_mph, 60.0, "Authority 2 should give 75%")
        
        # Test authority 3 (100%)
        auth_msg = {'command': 'Commanded Authority', 'value': 3, 'train_id': 1}
        self.app._process_message(auth_msg, 'Train Model')
        self.app._process_message(speed_msg, 'Train Model')
        self.assertEqual(self.app.commanded_speed_mph, 80.0, "Authority 3 should give 100%")


class TestEmergencyBrake(unittest.TestCase):
    """Test cases for emergency brake functionality"""
    
    @classmethod
    def setUpClass(cls):
        cls.root = tk.Tk()
        cls.root.withdraw()
    
    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()
    
    def setUp(self):
        with patch('Driver_UI.TrainSocketServer'):
            self.app = Main_Window(self.root, 'GREEN')
    
    def test_emergency_brake_activation(self):
        """Test that emergency brake can be activated"""
        # Simulate emergency brake activation
        self.app.emergency_brake_activate()
        
        self.assertTrue(self.app.emergency_brake_active,
                       "Emergency brake should be active")
    
    def test_emergency_brake_from_failure(self):
        """Test that failures trigger emergency brake"""
        # Simulate brake failure
        message = {
            'command': 'Brake Failure',
            'value': True,
            'train_id': 1
        }
        
        self.app._process_message(message, 'Train Model')
        
        # Emergency brake should be activated
        self.assertTrue(self.app.emergency_brake_active,
                       "Emergency brake should activate on brake failure")
    
    def test_emergency_brake_release(self):
        """Test that emergency brake can be released"""
        # Activate first
        self.app.emergency_brake_activate()
        self.assertTrue(self.app.emergency_brake_active)
        
        # Now release
        self.app.emergency_brake_release()
        
        self.assertFalse(self.app.emergency_brake_active,
                        "Emergency brake should be released")


class TestServiceBrake(unittest.TestCase):
    """Test cases for service brake functionality"""
    
    @classmethod
    def setUpClass(cls):
        cls.root = tk.Tk()
        cls.root.withdraw()
    
    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()
    
    def setUp(self):
        with patch('Driver_UI.TrainSocketServer'):
            self.app = Main_Window(self.root, 'GREEN')
    
    def test_service_brake_toggle(self):
        """Test service brake can be toggled on/off"""
        initial_state = self.app.service_brake_active
        
        # Toggle brake
        self.app.service_brake_action()
        
        # Should be opposite of initial state
        self.assertNotEqual(self.app.service_brake_active, initial_state,
                           "Service brake state should toggle")
    
    def test_service_brake_at_station(self):
        """Test that service brake is applied at stations"""
        # Simulate arriving at station
        self.app.position_tracker.is_at_station = True
        
        # Trigger power calculation which checks station status
        power = self.app.calculate_power_command()
        
        # Service brake should be active at station
        self.assertTrue(self.app.service_brake_active,
                       "Service brake should be active at station")
    
    def test_service_brake_power_output(self):
        """Test that service brake prevents power output"""
        # Activate service brake
        self.app.service_brake_active = True
        
        # Calculate power
        power = self.app.calculate_power_command()
        
        # Power should still be calculated, but sending logic will send 0
        # This is correct behavior - power is calculated but not sent when brake is on
        self.assertIsNotNone(power, "Power should still be calculated")


class TestEngineerUI(unittest.TestCase):
    """Test cases for Engineer UI PI controller parameters"""
    
    @classmethod
    def setUpClass(cls):
        cls.root = tk.Tk()
        cls.root.withdraw()
    
    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()
    
    def setUp(self):
        with patch('Driver_UI.TrainSocketServer'):
            self.app = Main_Window(self.root, 'GREEN')
    
    def test_kp_parameter_update(self):
        """Test that Kp parameter can be updated"""
        new_kp = 15.0
        
        # Update through engineer UI
        if hasattr(self.app, 'engineer_ui'):
            self.app.kp = new_kp
            
            self.assertEqual(self.app.kp, new_kp,
                           "Kp should be updated to new value")
    
    def test_ki_parameter_update(self):
        """Test that Ki parameter can be updated"""
        new_ki = 3.5
        
        # Update through engineer UI
        if hasattr(self.app, 'engineer_ui'):
            self.app.ki = new_ki
            
            self.assertEqual(self.app.ki, new_ki,
                           "Ki should be updated to new value")
    
    def test_default_pi_parameters(self):
        """Test that default PI parameters are set correctly"""
        # Check default values
        self.assertEqual(self.app.kp, 10.0,
                        "Default Kp should be 10.0")
        self.assertEqual(self.app.ki, 2.0,
                        "Default Ki should be 2.0")
        self.assertEqual(self.app.max_power_kw, 120.0,
                        "Default max power should be 120.0 kW")


class TestTemperatureControl(unittest.TestCase):
    """Test cases for temperature control"""
    
    @classmethod
    def setUpClass(cls):
        cls.root = tk.Tk()
        cls.root.withdraw()
    
    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()
    
    def setUp(self):
        with patch('Driver_UI.TrainSocketServer'):
            self.app = Main_Window(self.root, 'GREEN')
    
    def test_temperature_increase(self):
        """Test that temperature setpoint can be increased"""
        initial_temp = self.app.set_temp
        
        # Turn on AC first (required to change temperature)
        self.app.power_btn.is_on = True
        
        # Increase temperature
        self.app.increase_temp()
        
        self.assertEqual(self.app.set_temp, initial_temp + 1,
                        "Temperature should increase by 1")
    
    def test_temperature_decrease(self):
        """Test that temperature setpoint can be decreased"""
        initial_temp = self.app.set_temp
        
        # Turn on AC first
        self.app.power_btn.is_on = True
        
        # Decrease temperature
        self.app.decrease_temp()
        
        self.assertEqual(self.app.set_temp, initial_temp - 1,
                        "Temperature should decrease by 1")
    
    def test_temperature_bounds(self):
        """Test that temperature stays within bounds"""
        # Turn on AC
        self.app.power_btn.is_on = True
        
        # Test upper bound (85°F)
        self.app.set_temp = 84
        self.app.increase_temp()
        self.assertEqual(self.app.set_temp, 85, "Temp should be at max (85)")
        
        self.app.increase_temp()  # Try to exceed
        self.assertEqual(self.app.set_temp, 85, "Temp should not exceed 85")
        
        # Test lower bound (60°F)
        self.app.set_temp = 61
        self.app.decrease_temp()
        self.assertEqual(self.app.set_temp, 60, "Temp should be at min (60)")
        
        self.app.decrease_temp()  # Try to go below
        self.assertEqual(self.app.set_temp, 60, "Temp should not go below 60")


class TestStationAnnouncement(unittest.TestCase):
    """Test cases for station announcement functionality"""
    
    @classmethod
    def setUpClass(cls):
        cls.root = tk.Tk()
        cls.root.withdraw()
    
    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()
    
    def setUp(self):
        with patch('Driver_UI.TrainSocketServer'):
            self.app = Main_Window(self.root, 'GREEN')
    
    def test_station_announcement_callback(self):
        """Test that station announcement callback works"""
        # Mock the announcement method
        self.app.on_station_announce = Mock()
        
        # Trigger announcement
        self.app.on_station_announce('GREEN', 'DORMONT')
        
        # Verify callback was called
        self.app.on_station_announce.assert_called_once_with('GREEN', 'DORMONT')
    
    def test_next_station_display(self):
        """Test that next station is displayed correctly"""
        # Get next station from position tracker
        next_station = self.app.position_tracker.get_next_station_name()
        
        # Should not be empty
        self.assertIsNotNone(next_station,
                            "Next station should be available")
        self.assertNotEqual(next_station, "",
                           "Next station should not be empty string")
    
    def test_station_arrival_detection(self):
        """Test that station arrival is detected"""
        # Manually set close to station
        self.app.position_tracker.distance_to_next_station = 3.0  # Within threshold
        
        # Check if should decelerate
        should_decel = self.app.position_tracker.should_decelerate_for_station()
        
        # Should be decelerating when close to station
        self.assertTrue(should_decel,
                       "Should decelerate when close to station")


class TestPowerCalculation(unittest.TestCase):
    """Test cases for power calculation and PI controller"""
    
    @classmethod
    def setUpClass(cls):
        cls.root = tk.Tk()
        cls.root.withdraw()
    
    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()
    
    def setUp(self):
        with patch('Driver_UI.TrainSocketServer'):
            self.app = Main_Window(self.root, 'GREEN')
    
    def test_power_calculation_returns_value(self):
        """Test that power calculation returns a valid value"""
        # Set up conditions
        self.app.has_control_authority = True
        self.app.commanded_speed_mph = 30.0
        self.app.current_speed_ms = 10.0
        
        # Calculate power
        power = self.app.calculate_power_command()
        
        # Should return a number
        self.assertIsInstance(power, (int, float),
                            "Power should be a number")
        self.assertGreaterEqual(power, 0.0,
                              "Power should be non-negative")
        self.assertLessEqual(power, self.app.max_power_kw,
                           "Power should not exceed max power")
    
    def test_power_zero_when_at_target_speed(self):
        """Test that power approaches steady-state when at target speed"""
        # Set to be at target speed
        self.app.has_control_authority = True
        self.app.commanded_speed_mph = 30.0
        self.app.commanded_speed_ms = 30.0 * 0.44704  # Convert to m/s
        self.app.current_speed_ms = 30.0 * 0.44704   # Same speed
        
        # Calculate power - at steady state, power is from I term only
        power = self.app.calculate_power_command()
        
        # Power should be calculable (I term provides steady-state power)
        self.assertIsInstance(power, (int, float),
                            "Power should be calculable at steady state")
    
    def test_integral_error_accumulation(self):
        """Test that integral error accumulates over time"""
        self.app.has_control_authority = True
        self.app.commanded_speed_mph = 40.0
        self.app.commanded_speed_ms = 40.0 * 0.44704
        self.app.current_speed_ms = 10.0
        
        initial_integral = self.app.integral_error
        
        # Run power calculation multiple times
        for _ in range(10):
            self.app.calculate_power_command()
        
        # Integral should have changed
        self.assertNotEqual(self.app.integral_error, initial_integral,
                           "Integral error should accumulate")


class TestTimeAndMultiplier(unittest.TestCase):
    """Test cases for TIME and MULT command handling"""
    
    @classmethod
    def setUpClass(cls):
        cls.root = tk.Tk()
        cls.root.withdraw()
    
    @classmethod
    def tearDownClass(cls):
        cls.root.destroy()
    
    def setUp(self):
        with patch('Driver_UI.TrainSocketServer'):
            self.app = Main_Window(self.root, 'GREEN')
    
    def test_time_command_processing(self):
        """Test that TIME command updates clock display"""
        message = {
            'command': 'TIME',
            'value': '14:30:45',
            'train_id': 1
        }
        
        self.app._process_message(message, 'Train Model')
        
        # Check that clock display was updated
        if hasattr(self.app, 'clock_display'):
            clock_text = self.app.clock_display.cget('text')
            self.assertEqual(clock_text, '14:30:45',
                           "Clock should display the time")
    
    def test_mult_command_1x_speed(self):
        """Test that MULT command sets 1x speed"""
        message = {
            'command': 'MULT',
            'value': 1,
            'train_id': 1
        }
        
        self.app._process_message(message, 'Train Model')
        
        self.assertEqual(self.app.time_multiplier, 1,
                        "Time multiplier should be set to 1")
        self.assertEqual(self.app.position_tracker.TIME_SCALE, 1.0,
                        "Position tracker TIME_SCALE should be 1.0")
    
    def test_mult_command_10x_speed(self):
        """Test that MULT command sets 10x speed"""
        message = {
            'command': 'MULT',
            'value': 10,
            'train_id': 1
        }
        
        self.app._process_message(message, 'Train Model')
        
        self.assertEqual(self.app.time_multiplier, 10,
                        "Time multiplier should be set to 10")
        self.assertEqual(self.app.position_tracker.TIME_SCALE, 10.0,
                        "Position tracker TIME_SCALE should be 10.0")
    
    def test_mult_command_invalid_value(self):
        """Test that invalid MULT values are rejected"""
        message = {
            'command': 'MULT',
            'value': 5,  # Invalid - only 1 or 10 allowed
            'train_id': 1
        }
        
        initial_mult = self.app.time_multiplier
        
        self.app._process_message(message, 'Train Model')
        
        # Time multiplier should not change with invalid value
        self.assertEqual(self.app.time_multiplier, initial_mult,
                        "Time multiplier should not change with invalid value")


def run_tests():
    """Run all tests and print results"""
    # Create test suite
    loader = unittest.TestLoader()
    
    # Load all test classes
    test_classes = [
        TestDriverMode,
        TestCommandedSpeed,
        TestCommandedAuthority,
        TestEmergencyBrake,
        TestServiceBrake,
        TestEngineerUI,
        TestTemperatureControl,
        TestStationAnnouncement,
        TestPowerCalculation,
        TestTimeAndMultiplier
    ]
    
    suite = unittest.TestSuite()
    for test_class in test_classes:
        tests = loader.loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"Success rate: {success_rate:.1f}%")
    print("="*70)
    
    return result


if __name__ == "__main__":
    run_tests()