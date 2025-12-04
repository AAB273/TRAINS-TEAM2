import unittest
import tkinter as tk
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add the parent directory to the path to import Driver_UI
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock the socket server before importing Driver_UI
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
            self.app = Main_Window(self.root)
    
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
    
    def test_decrease_speed_switches_to_manual(self):
        """Test that decreasing speed switches from auto to manual mode"""
        # Ensure we start in auto mode
        self.app.mode_select.set_mode("auto")
        self.assertTrue(self.app.is_auto_mode, "Should start in auto mode")
        
        # Get initial speed
        initial_speed = self.app.set_speed
        
        # Decrease speed
        self.app.decrease_set_speed()
        
        # Verify mode switched to manual
        self.assertFalse(self.app.is_auto_mode,
                        "Mode should switch to manual after decreasing speed")
        self.assertEqual(self.app.mode_select.active_mode, "manual",
                        "Mode toggle should show 'manual' after speed decrease")
        
        # Verify speed was actually decreased
        self.assertEqual(self.app.set_speed, initial_speed - 5,
                        "Speed should be decreased by 5")
        self.assertEqual(self.app.set_speed_value.cget("text"), str(initial_speed - 5),
                        "Speed display should reflect the decrease")
    
    def test_multiple_speed_adjustments_stay_manual(self):
        """Test that multiple speed adjustments keep the mode in manual"""
        # Start in auto mode
        self.app.mode_select.set_mode("auto")
        
        # Make first adjustment
        self.app.increase_set_speed()
        self.assertFalse(self.app.is_auto_mode, "Should be manual after first adjustment")
        
        # Make second adjustment
        self.app.increase_set_speed()
        self.assertFalse(self.app.is_auto_mode, "Should stay manual after second adjustment")
        
        # Make third adjustment (decrease)
        self.app.decrease_set_speed()
        self.assertFalse(self.app.is_auto_mode, "Should stay manual after third adjustment")
    
    def test_speed_bounds_in_manual_mode(self):
        """Test that speed stays within bounds (0-80 mph) in manual mode"""
        self.app.mode_select.set_mode("manual")
        
        # Test upper bound
        self.app.set_speed = 75
        self.app.set_speed_value.config(text="75")
        self.app.increase_set_speed()
        self.assertEqual(self.app.set_speed, 80, "Speed should cap at 80")
        
        self.app.increase_set_speed()  # Try to exceed
        self.assertEqual(self.app.set_speed, 80, "Speed should not exceed 80")
        
        # Test lower bound
        self.app.set_speed = 5
        self.app.set_speed_value.config(text="5")
        self.app.decrease_set_speed()
        self.assertEqual(self.app.set_speed, 0, "Speed should not go below 0")
        
        self.app.decrease_set_speed()  # Try to go negative
        self.assertEqual(self.app.set_speed, 0, "Speed should not go below 0")
    
    def test_confirm_speed_in_manual_mode(self):
        """Test that confirming speed works correctly in manual mode"""
        # Switch to manual and set a speed
        self.app.mode_select.set_mode("manual")
        self.app.set_speed = 55
        self.app.set_speed_value.config(text="55")
        
        # Confirm the speed
        self.app.confirm_speed()
        
        # Verify commanded speed was updated
        self.assertEqual(self.app.commanded_speed_value.cget("text"), "55",
                        "Commanded speed should match confirmed speed")
        
        # Verify integral error was reset
        self.assertEqual(self.app.integral_error, 0.0,
                        "Integral error should be reset on speed confirmation")
    
    def test_mode_callback_is_called(self):
        """Test that the mode change callback is properly invoked"""
        callback_mock = Mock()
        
        # Create a new mode toggle with a callback
        test_frame = tk.Frame(self.root)
        mode_toggle = Mode_Toggle(test_frame, callback=callback_mock)
        
        # Change mode
        mode_toggle.set_mode("manual")
        
        # Verify callback was called with correct argument
        callback_mock.assert_called_once_with("manual")
        
        # Clean up
        test_frame.destroy()
    
    def test_auto_mode_uses_commanded_speed(self):
        """Test that auto mode uses commanded speed from track model"""
        # Set to auto mode
        self.app.mode_select.set_mode("auto")
        
        # Simulate receiving commanded speed
        self.app.commanded_speed_ms = 20.0  # 20 m/s
        commanded_speed_mph = 20.0 * 2.23694  # Convert to mph
        self.app.set_commanded_speed(round(commanded_speed_mph, 1))
        
        # Verify commanded speed is displayed
        self.assertEqual(self.app.commanded_speed_value.cget("text"), 
                        str(round(commanded_speed_mph, 1)),
                        "Commanded speed should be displayed in auto mode")
    
    def test_manual_mode_ignores_external_commanded_speed(self):
        """Test that manual mode ignores external commanded speed updates"""
        # Set to manual mode
        self.app.mode_select.set_mode("manual")
        
        # Set manual speed
        self.app.set_speed = 50
        self.app.set_speed_value.config(text="50")
        self.app.confirm_speed()
        
        initial_commanded = self.app.commanded_speed_value.cget("text")
        
        # Try to set commanded speed (as if from track model)
        self.app.commanded_speed_ms = 25.0
        self.app.set_commanded_speed(55)
        
        # In manual mode, the set_commanded_speed should not update display
        # because is_auto_mode is False
        self.assertEqual(self.app.commanded_speed_value.cget("text"), 
                        initial_commanded,
                        "Commanded speed display should not change in manual mode")


def run_tests():
    """Run all tests and print results"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestDriverMode)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    print("="*70)
    
    return result


if __name__ == "__main__":
    run_tests()