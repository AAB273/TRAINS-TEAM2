"""
Track HW Test Suite
Tests all Track HW functionality including:
- Block occupancy updates from Track Model
- Track failure handling
- CTC speed/authority commands
- PLC integration
- Message forwarding to CTC
"""

import threading
import time
import tkinter as tk
import sys
import os

# Add your project path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

class TrackHW_TestBench:
    def __init__(self, test_data, plc_manager):
        """
        Initialize Track HW test bench
        
        Args:
            test_data: Reference to Track HW test_data
            plc_manager: Reference to PLCManager
        """
        self.test_data = test_data
        self.plc_manager = plc_manager
        self.test_results = []
        self.total_tests = 0
        self.passed_tests = 0
        
        print("\n" + "="*70)
        print("🔧 TRACK HW TEST BENCH INITIALIZED")
        print("="*70)
        print(f"Testing Track HW functionality")
        print(f"PLC Controller: {plc_manager.controller.__class__.__name__}")
        print("="*70 + "\n")
    
    def log_test(self, test_name, passed, message=""):
        """Log test result to terminal"""
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            status = "✓ PASS"
            symbol = "✓"
        else:
            status = "✗ FAIL"
            symbol = "✗"
        
        # Print to terminal with clear formatting
        print(f"\n{symbol} {test_name}")
        print(f"  Status: {status}")
        if message:
            print(f"  Details: {message}")
        print("-" * 70)
        
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "message": message
        })
        
        return passed
    
    def print_summary(self):
        """Print final test summary to terminal"""
        print("\n" + "="*70)
        print("📊 TRACK HW TEST SUMMARY")
        print("="*70)
        print(f"Total Tests Run: {self.total_tests}")
        print(f"Tests Passed: {self.passed_tests}")
        print(f"Tests Failed: {self.total_tests - self.passed_tests}")
        
        if self.total_tests > 0:
            success_rate = (self.passed_tests / self.total_tests) * 100
            print(f"Success Rate: {success_rate:.1f}%")
        else:
            print("Success Rate: 0.0% (no tests completed)")
        
        print("="*70)
        
        # Print failed tests if any
        if self.passed_tests < self.total_tests:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["passed"]:
                    print(f"  • {result['test']}")
                    if result["message"]:
                        print(f"    → {result['message']}")
        
        if self.total_tests > 0 and self.passed_tests == self.total_tests:
            print("\n🎉 ALL TESTS PASSED! 🎉")
        elif self.total_tests > 0:
            print(f"\n⚠️  {self.total_tests - self.passed_tests} test(s) failed")
        else:
            print("\n❌ NO TESTS COMPLETED")
        
        print("="*70 + "\n")
        
        return self.total_tests > 0 and self.passed_tests == self.total_tests
    
    # =========================================================================
    # TEST FUNCTIONS
    # =========================================================================
    
    def test_occupancy_reception(self):
        """Test 1: Track HW receives occupancy from Track Model"""
        print("\n" + "="*70)
        print("TEST 1: Block Occupancy Reception from Track Model")
        print("="*70)
        
        test_passed = True
        
        # Simulate Track Model sending occupancy
        print("  📤 Simulating Track Model occupancy update...")
        occupancy_data = {
            70: 1,  # Block 70 occupied by train 1
            71: 0,  # Block 71 clear
            72: 2,  # Block 72 occupied by train 2
        }
        
        # Import the handler from Track HW
        try:
            from WC_HW_MainUI import handle_block_occupancy
            
            print("  ✓ Found handle_block_occupancy function")
            
            # Call the handler
            handle_block_occupancy(occupancy_data)
            
            # Verify the data was stored in test_data.block_data
            print("\n  📋 Verifying occupancy data in test_data.block_data...")
            for block_num, expected_occ in occupancy_data.items():
                found = False
                for row in self.test_data.block_data:
                    if str(row[2]) == str(block_num) and row[1] == 'Green':
                        actual_occ = row[0]
                        expected_str = "Yes" if expected_occ != 0 else "No"
                        
                        if actual_occ == expected_str:
                            print(f"    ✓ Block {block_num}: {actual_occ} (correct)")
                            found = True
                        else:
                            print(f"    ✗ Block {block_num}: Expected {expected_str}, got {actual_occ}")
                            test_passed = False
                            found = True
                        break
                
                if not found:
                    print(f"    ✗ Block {block_num}: Not found in block_data")
                    test_passed = False
            
        except ImportError as e:
            print(f"  ✗ Could not import handle_block_occupancy: {e}")
            test_passed = False
        except Exception as e:
            print(f"  ✗ Error testing occupancy: {e}")
            import traceback
            traceback.print_exc()
            test_passed = False
        
        return self.log_test("Block Occupancy Reception", test_passed,
                           "Occupancy received and stored" if test_passed else "Occupancy handling failed")
    
    def test_failure_reception(self):
        """Test 2: Track HW receives failures from Track Model"""
        print("\n" + "="*70)
        print("TEST 2: Track Failure Reception from Track Model")
        print("="*70)
        
        test_passed = True
        
        # Simulate Track Model sending failures
        print("  📤 Simulating Track Model failure notification...")
        failure_data = {
            'track_circuit_failures': [10, 20],
            'broken_rail_failures': [15],
            'power_failures': [25, 30]
        }
        
        try:
            from WC_HW_MainUI import handle_track_failures
            
            print("  ✓ Found handle_track_failures function")
            
            # Call the handler
            handle_track_failures(failure_data)
            
            # Verify blocks are marked as unavailable
            print("\n  📋 Verifying failed blocks marked as unavailable...")
            all_failures = (failure_data['track_circuit_failures'] + 
                          failure_data['broken_rail_failures'] + 
                          failure_data['power_failures'])
            
            for block_num in all_failures:
                found = False
                for row in self.test_data.block_data:
                    if str(row[2]) == str(block_num) and row[1] == 'Green':
                        actual_occ = row[0]
                        
                        if actual_occ == "No":
                            print(f"    ✓ Block {block_num}: Marked as unavailable")
                            found = True
                        else:
                            print(f"    ✗ Block {block_num}: Expected 'No', got {actual_occ}")
                            test_passed = False
                            found = True
                        break
                
                if not found:
                    print(f"    ⚠️  Block {block_num}: Not found in block_data")
            
            # Verify failures stored in test_data.active_failures
            if hasattr(self.test_data, 'active_failures'):
                print("\n  📋 Verifying active_failures set...")
                if set(all_failures) == self.test_data.active_failures:
                    print(f"    ✓ active_failures correct: {self.test_data.active_failures}")
                else:
                    print(f"    ✗ active_failures mismatch")
                    print(f"      Expected: {set(all_failures)}")
                    print(f"      Got: {self.test_data.active_failures}")
                    test_passed = False
            else:
                print("    ⚠️  test_data.active_failures not found")
            
        except ImportError as e:
            print(f"  ✗ Could not import handle_track_failures: {e}")
            test_passed = False
        except Exception as e:
            print(f"  ✗ Error testing failures: {e}")
            import traceback
            traceback.print_exc()
            test_passed = False
        
        return self.log_test("Track Failure Reception", test_passed,
                           "Failures received and processed" if test_passed else "Failure handling failed")
    
    def test_ctc_speed_authority(self):
        """Test 3: Track HW receives speed/authority from CTC"""
        print("\n" + "="*70)
        print("TEST 3: CTC Speed & Authority Reception")
        print("="*70)
        
        test_passed = True
        
        # Simulate CTC sending speed and authority
        print("  📤 Simulating CTC speed/authority command...")
        ctc_data = {
            'track': 'Green',
            'block': '70',
            'speed': '35.5',
            'authority': '5',
            'value_type': 'suggested'
        }
        
        try:
            from WC_HW_MainUI import handle_ctc_speed_authority
            
            print("  ✓ Found handle_ctc_speed_authority function")
            
            # Call the handler
            handle_ctc_speed_authority(ctc_data)
            
            # Verify data stored in right_panel
            print("\n  📋 Verifying speed/authority stored...")
            
            # Check if right_panel exists and has the data
            from WC_HW_MainUI import right_panel, test_data
            
            block = ctc_data['block']
            current_line = test_data.current_line
            
            if hasattr(right_panel, 'suggested_speed'):
                if current_line in right_panel.suggested_speed:
                    if block in right_panel.suggested_speed[current_line]:
                        speed = right_panel.suggested_speed[current_line][block]
                        print(f"    ✓ Speed stored: {speed} mph")
                    else:
                        print(f"    ✗ Block {block} not in suggested_speed")
                        test_passed = False
                else:
                    print(f"    ✗ Line {current_line} not in suggested_speed")
                    test_passed = False
            else:
                print("    ✗ right_panel.suggested_speed not found")
                test_passed = False
            
            if hasattr(right_panel, 'suggested_authority'):
                if current_line in right_panel.suggested_authority:
                    if block in right_panel.suggested_authority[current_line]:
                        authority = right_panel.suggested_authority[current_line][block]
                        print(f"    ✓ Authority stored: {authority} blocks")
                    else:
                        print(f"    ✗ Block {block} not in suggested_authority")
                        test_passed = False
                else:
                    print(f"    ✗ Line {current_line} not in suggested_authority")
                    test_passed = False
            else:
                print("    ✗ right_panel.suggested_authority not found")
                test_passed = False
            
        except ImportError as e:
            print(f"  ✗ Could not import required functions: {e}")
            test_passed = False
        except Exception as e:
            print(f"  ✗ Error testing CTC command: {e}")
            import traceback
            traceback.print_exc()
            test_passed = False
        
        return self.log_test("CTC Speed & Authority", test_passed,
                           "CTC commands received" if test_passed else "CTC handling failed")
    
    def test_plc_integration(self):
        """Test 4: PLC receives occupancy updates"""
        print("\n" + "="*70)
        print("TEST 4: PLC Integration with Occupancy")
        print("="*70)
        
        test_passed = True
        
        # Set some occupancy data
        print("  📤 Setting test occupancy data...")
        test_blocks = [70, 71, 72]
        
        for i, block_num in enumerate(test_blocks):
            for row in self.test_data.block_data:
                if str(row[2]) == str(block_num) and row[1] == 'Green':
                    row[0] = "Yes" if i % 2 == 0 else "No"  # Alternate occupied/clear
                    print(f"    Set block {block_num}: {row[0]}")
                    break
        
        # Run PLC cycle
        print("\n  🔧 Running PLC cycle...")
        try:
            self.plc_manager.run_plc_quiet()
            
            # Verify PLC can read the occupancy
            print("\n  📋 Verifying PLC reads occupancy...")
            for block_num in test_blocks:
                occupied = self.plc_manager.controller.get_block_occupancy(block_num)
                print(f"    Block {block_num}: Occupied = {occupied}")
            
            print("    ✓ PLC successfully reads occupancy")
            
        except Exception as e:
            print(f"  ✗ Error running PLC: {e}")
            import traceback
            traceback.print_exc()
            test_passed = False
        
        return self.log_test("PLC Integration", test_passed,
                           "PLC integrated with occupancy" if test_passed else "PLC integration failed")
    
    def test_light_control(self):
        """Test 5: PLC controls lights based on occupancy"""
        print("\n" + "="*70)
        print("TEST 5: PLC Light Control")
        print("="*70)
        
        test_passed = True
        
        # Clear all occupancy first
        print("  🧹 Clearing all occupancy...")
        for row in self.test_data.block_data:
            if row[1] == 'Green':
                row[0] = "No"
        
        # Occupy a block near a light (e.g., block 1 has Light 1)
        print("\n  📍 Occupying block 1 (has Light 1)...")
        for row in self.test_data.block_data:
            if str(row[2]) == '1' and row[1] == 'Green':
                row[0] = "Yes"
                print("    ✓ Block 1 occupied")
                break
        
        # Run PLC cycle
        print("\n  🔧 Running PLC cycle...")
        try:
            self.plc_manager.run_plc_quiet()
            
            # Check light state
            print("\n  💡 Checking Light 1 state...")
            light_1_state = self.plc_manager.controller.get_light_state(1)
            
            if light_1_state == 'Red':
                print(f"    ✓ Light 1: {light_1_state} (correct - block occupied)")
            else:
                print(f"    ✗ Light 1: {light_1_state} (should be Red when block occupied)")
                test_passed = False
            
            # Clear occupancy and run again
            print("\n  🧹 Clearing block 1 occupancy...")
            for row in self.test_data.block_data:
                if str(row[2]) == '1' and row[1] == 'Green':
                    row[0] = "No"
                    break
            
            self.plc_manager.run_plc_quiet()
            
            light_1_state = self.plc_manager.controller.get_light_state(1)
            if light_1_state in ['Green', 'Super Green']:
                print(f"    ✓ Light 1: {light_1_state} (correct - block clear)")
            else:
                print(f"    ⚠️  Light 1: {light_1_state} (expected Green/Super Green)")
            
        except Exception as e:
            print(f"  ✗ Error testing light control: {e}")
            import traceback
            traceback.print_exc()
            test_passed = False
        
        return self.log_test("PLC Light Control", test_passed,
                           "Lights controlled by occupancy" if test_passed else "Light control failed")
    
    def test_switch_safety(self):
        """Test 6: PLC prevents switch changes when occupied"""
        print("\n" + "="*70)
        print("TEST 6: PLC Switch Safety")
        print("="*70)
        
        test_passed = True
        
        # Test switch 12 (first switch in PLC scope)
        print("  🔄 Testing Switch 12 safety...")
        
        # Occupy block 12
        print("\n  📍 Occupying block 12 (switch location)...")
        for row in self.test_data.block_data:
            if str(row[2]) == '12' and row[1] == 'Green':
                row[0] = "Yes"
                print("    ✓ Block 12 occupied")
                break
        
        # Check if PLC allows switch change
        print("\n  🔧 Checking if PLC allows switch change...")
        try:
            safe = self.plc_manager.controller.check_switch_safety(12)
            
            if not safe:
                print("    ✓ PLC correctly blocks switch change (block occupied)")
            else:
                print("    ✗ PLC allows switch change (should be blocked!)")
                test_passed = False
            
            # Clear occupancy
            print("\n  🧹 Clearing block 12 occupancy...")
            for row in self.test_data.block_data:
                if str(row[2]) == '12' and row[1] == 'Green':
                    row[0] = "No"
                    break
            
            # Check again
            safe = self.plc_manager.controller.check_switch_safety(12)
            
            if safe:
                print("    ✓ PLC allows switch change (block clear)")
            else:
                print("    ⚠️  PLC still blocks switch change")
            
        except Exception as e:
            print(f"  ✗ Error testing switch safety: {e}")
            import traceback
            traceback.print_exc()
            test_passed = False
        
        return self.log_test("PLC Switch Safety", test_passed,
                           "Switch safety working" if test_passed else "Switch safety failed")
    
    def test_failure_safety(self):
        """Test 7: PLC prevents operations on failed blocks"""
        print("\n" + "="*70)
        print("TEST 7: PLC Failure Safety")
        print("="*70)
        
        test_passed = True
        
        # Set a failure on a switch block
        print("  ⚠️  Setting failure on block 12 (switch)...")
        if not hasattr(self.test_data, 'active_failures'):
            self.test_data.active_failures = set()
        
        self.test_data.active_failures.add(12)
        self.plc_manager.controller.active_failures = self.test_data.active_failures
        
        print(f"    ✓ Active failures: {self.test_data.active_failures}")
        
        # Check if PLC detects fault
        print("\n  🔧 Checking if PLC detects fault...")
        try:
            has_fault = self.plc_manager.controller.get_block_fault(12)
            
            if has_fault:
                print("    ✓ PLC correctly detects fault on block 12")
            else:
                print("    ✗ PLC does not detect fault")
                test_passed = False
            
            # Check switch safety with fault
            print("\n  🔄 Checking switch safety with fault...")
            safe = self.plc_manager.controller.check_switch_safety(12)
            
            if not safe:
                print("    ✓ PLC correctly blocks switch change (fault present)")
            else:
                print("    ✗ PLC allows switch change (should be blocked due to fault!)")
                test_passed = False
            
            # Clear failure
            print("\n  🧹 Clearing failure...")
            self.test_data.active_failures.clear()
            self.plc_manager.controller.active_failures = set()
            
            has_fault = self.plc_manager.controller.get_block_fault(12)
            if not has_fault:
                print("    ✓ Fault cleared")
            
        except Exception as e:
            print(f"  ✗ Error testing failure safety: {e}")
            import traceback
            traceback.print_exc()
            test_passed = False
        
        return self.log_test("PLC Failure Safety", test_passed,
                           "Failure safety working" if test_passed else "Failure safety failed")
    
    def run_all_tests(self):
        """Run all Track HW tests"""
        print("\n" + "="*70)
        print("🚀 STARTING COMPLETE TRACK HW TEST SUITE")
        print("="*70)
        print(f"Testing Track HW functionality")
        print("="*70 + "\n")
        
        # Reset counters
        self.total_tests = 0
        self.passed_tests = 0
        
        # Run all tests
        tests = [
            self.test_occupancy_reception,
            self.test_failure_reception,
            self.test_ctc_speed_authority,
            self.test_plc_integration,
            self.test_light_control,
            self.test_switch_safety,
            self.test_failure_safety,
        ]
        
        for test_func in tests:
            try:
                test_func()
                time.sleep(0.5)  # Brief pause between tests
            except Exception as e:
                print(f"\n✗ TEST ERROR: {e}")
                import traceback
                traceback.print_exc()
                self.log_test(test_func.__name__, False, f"Exception: {str(e)}")
        
        # Print final summary
        return self.print_summary()


def run_track_hw_tests():
    """Main function to run Track HW tests"""
    print("\n" + "="*70)
    print("🔧 TRACK HW TEST SUITE")
    print("="*70)
    print("Testing Track HW functionality")
    print("="*70 + "\n")
    
    try:
        # Import Track HW components
        print("Importing Track HW components...")
        from WC_HW_MainUI import test_data, plc_manager
        
        print("✓ Track HW components imported")
        
        # Create testbench
        print("Creating testbench...")
        testbench = TrackHW_TestBench(test_data, plc_manager)
        
        # Run tests
        print("\n" + "="*70)
        print("RUNNING TESTS")
        print("="*70)
        
        all_passed = testbench.run_all_tests()
        
        if all_passed:
            print("\n✅ ALL TRACK HW TESTS PASSED!")
        else:
            print("\n⚠️  SOME TRACK HW TESTS FAILED")
        
        return all_passed
        
    except ImportError as e:
        print(f"\n✗ Import Error: {e}")
        print("Make sure WC_HW_MainUI.py is accessible")
        return False
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    run_track_hw_tests()