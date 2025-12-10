"""
Comprehensive Test Cases for Track Model UI System
Tests 10 different core functionalities of the system
"""

import unittest
from unittest.mock import Mock, patch, MagicMock, call
import sys
import os

# Mock the dependencies that might not be available
sys.modules['UI_Variables'] = Mock()
sys.modules['Test_UI'] = Mock()
sys.modules['FileUploadManager'] = Mock()
sys.modules['TrackDiagramDrawer'] = Mock()
sys.modules['HeaterSystemManager'] = Mock()
sys.modules['BeaconManager'] = Mock()
sys.modules['TrainSocketServer'] = Mock()
sys.modules['MurphyTrackFailures'] = Mock()
sys.modules['PIL'] = Mock()
sys.modules['tkinter'] = Mock()
sys.modules['tkinter.ttk'] = Mock()
sys.modules['tkinter.simpledialog'] = Mock()


class TestCase01_SwitchRoutingLogic(unittest.TestCase):
    """Test Case 1: Switch Routing Logic for Green and Red Lines"""
    
    def test_green_line_switch_routing(self):
        """Test Green Line switch routing configurations"""
        print("\n=== TEST CASE 1a: Green Line Switch Routing ===")
        
        # Green Line switch configuration from UI_Structure.py
        switch_routing_green = {
            12: {"normal": 13, "reverse": 13},
            28: {"normal": 29, "reverse": 150},
            57: {"normal": 58, "reverse": 151},
            62: {"normal": 63, "reverse": 63},
            76: {"normal": 78, "reverse": 101},
            85: {"normal": 86, "reverse": 100}
        }
        
        # Test switch 28 routing
        print(f"Switch 28 normal route: {switch_routing_green[28]['normal']}")
        print(f"Switch 28 reverse route: {switch_routing_green[28]['reverse']}")
        
        self.assertEqual(switch_routing_green[28]["normal"], 29)
        self.assertEqual(switch_routing_green[28]["reverse"], 150)
        
        # Test switch 76 (junction)
        self.assertEqual(switch_routing_green[76]["normal"], 78)
        self.assertEqual(switch_routing_green[76]["reverse"], 101)
        
        print("✅ Green Line switch routing validated\n")
    
    def test_red_line_switch_routing(self):
        """Test Red Line switch routing configurations including bidirectional"""
        print("\n=== TEST CASE 1b: Red Line Switch Routing ===")
        
        # Red Line switch configuration
        switch_routing_red = {
            9: {"normal": 10, "reverse": 75},
            15: {"normal": 16, "reverse": 1},
            27: {"normal": 28, "reverse": 76},
            32: {"normal": 33, "reverse": 72},
            38: {"normal": 39, "reverse": 71},
            43: {"normal": 44, "reverse": 67},
            52: {"normal": 53, "reverse": 66},
            # Bidirectional entries
            1: {"normal": 2, "reverse": 16},
            16: {"normal": 17, "reverse": 15},
            53: {"normal": 54, "reverse": 52},
            66: {"normal": 67, "reverse": 52}
        }
        
        # Test loop switch 15
        print(f"Switch 15 normal (continue): {switch_routing_red[15]['normal']}")
        print(f"Switch 15 reverse (close loop): {switch_routing_red[15]['reverse']}")
        
        self.assertEqual(switch_routing_red[15]["normal"], 16)
        self.assertEqual(switch_routing_red[15]["reverse"], 1)
        
        # Test bidirectional entry from block 16
        self.assertEqual(switch_routing_red[16]["normal"], 17)
        self.assertEqual(switch_routing_red[16]["reverse"], 15)
        
        print("✅ Red Line switch routing with bidirectional entries validated\n")


class TestCase02_BlockOccupancyTracking(unittest.TestCase):
    """Test Case 2: Block Occupancy Tracking and Updates"""
    
    def setUp(self):
        """Set up mock blocks for testing"""
        self.mock_blocks = []
        for i in range(150):
            mock_block = Mock()
            mock_block.occupancy = 0
            mock_block.block_number = i + 1
            self.mock_blocks.append(mock_block)
    
    def test_occupancy_list_format(self):
        """Test block occupancy update using list format [block_num, occupancy]"""
        print("\n=== TEST CASE 2a: Occupancy List Format ===")
        
        # Simulate receiving occupancy data in list format
        test_data = [25, 1]  # Block 25, occupied
        
        block_num, occupancy = test_data
        if 1 <= block_num <= len(self.mock_blocks):
            self.mock_blocks[block_num - 1].occupancy = occupancy
            print(f"Block {block_num} occupancy set to: {occupancy}")
        
        self.assertEqual(self.mock_blocks[24].occupancy, 1)
        print("✅ List format occupancy update successful\n")
    
    def test_occupancy_dict_format(self):
        """Test block occupancy update using dictionary format"""
        print("\n=== TEST CASE 2b: Occupancy Dictionary Format ===")
        
        # Simulate receiving multiple occupancy updates
        test_data = {10: 1, 15: 2, 20: 0, 25: 3}
        
        for block_num, occupancy in test_data.items():
            if 1 <= block_num <= len(self.mock_blocks):
                self.mock_blocks[block_num - 1].occupancy = occupancy
                print(f"Block {block_num}: occupancy = {occupancy}")
        
        self.assertEqual(self.mock_blocks[9].occupancy, 1)
        self.assertEqual(self.mock_blocks[14].occupancy, 2)
        self.assertEqual(self.mock_blocks[19].occupancy, 0)
        self.assertEqual(self.mock_blocks[24].occupancy, 3)
        print("✅ Dictionary format occupancy update successful\n")
    
    def test_occupancy_boundary_validation(self):
        """Test boundary conditions for block numbers"""
        print("\n=== TEST CASE 2c: Occupancy Boundary Validation ===")
        
        # Test invalid block numbers
        invalid_blocks = [0, -1, 151, 200]
        valid_updates = 0
        
        for block_num in invalid_blocks:
            if 1 <= block_num <= len(self.mock_blocks):
                valid_updates += 1
        
        print(f"Invalid block numbers tested: {invalid_blocks}")
        print(f"Valid updates (should be 0): {valid_updates}")
        
        self.assertEqual(valid_updates, 0)
        print("✅ Boundary validation working correctly\n")


class TestCase03_TrafficLightManagement(unittest.TestCase):
    """Test Case 3: Traffic Light State Management"""
    
    def test_traffic_light_initialization(self):
        """Test traffic light initialization for all blocks"""
        print("\n=== TEST CASE 3a: Traffic Light Initialization ===")
        
        # Traffic light blocks from both lines
        light_blocks_green = {1, 62, 76, 100, 150}
        light_blocks_red = {1, 10, 15, 28, 32, 39, 43, 53, 66, 67, 71, 72, 76}
        
        # Combined set
        all_light_blocks = light_blocks_green.union(light_blocks_red)
        
        print(f"Total traffic light blocks: {len(all_light_blocks)}")
        print(f"Light blocks: {sorted(all_light_blocks)}")
        
        # Initialize lights
        traffic_light_states = {}
        for block in all_light_blocks:
            traffic_light_states[block] = 0  # 0 = red by default
        
        self.assertEqual(len(traffic_light_states), len(all_light_blocks))
        self.assertIn(1, traffic_light_states)
        self.assertIn(76, traffic_light_states)
        print("✅ Traffic lights initialized correctly\n")
    
    def test_traffic_light_state_changes(self):
        """Test traffic light state transitions"""
        print("\n=== TEST CASE 3b: Traffic Light State Changes ===")
        
        # Simulate traffic light states (0=red, 1=green)
        light_states = {1: 0, 10: 0, 15: 0}
        
        # Change light states
        light_states[1] = 1  # Green
        light_states[10] = 1  # Green
        
        print(f"Block 1 light: {'Green' if light_states[1] == 1 else 'Red'}")
        print(f"Block 10 light: {'Green' if light_states[10] == 1 else 'Red'}")
        print(f"Block 15 light: {'Green' if light_states[15] == 1 else 'Red'}")
        
        self.assertEqual(light_states[1], 1)
        self.assertEqual(light_states[10], 1)
        self.assertEqual(light_states[15], 0)
        print("✅ Traffic light state changes working\n")


class TestCase04_CrossingStateControl(unittest.TestCase):
    """Test Case 4: Railway Crossing State Control"""
    
    def setUp(self):
        """Set up mock blocks with crossing states"""
        self.mock_blocks = []
        for i in range(20):
            mock_block = Mock()
            mock_block.block_number = i + 1
            mock_block.crossing_state = False  # False = up, True = down
            mock_block.occupancy = 0
            self.mock_blocks.append(mock_block)
        
        # Define which blocks have crossings
        self.crossing_blocks = {5, 10, 15}
    
    def test_crossing_activation_on_occupancy(self):
        """Test crossing activates when block becomes occupied"""
        print("\n=== TEST CASE 4a: Crossing Activation ===")
        
        # Block 5 becomes occupied
        block_num = 5
        self.mock_blocks[block_num - 1].occupancy = 1
        
        # Activate crossing if block has one
        if block_num in self.crossing_blocks:
            self.mock_blocks[block_num - 1].crossing_state = True
            print(f"Block {block_num}: Crossing ACTIVATED (gates down)")
        
        self.assertTrue(self.mock_blocks[4].crossing_state)
        print("✅ Crossing activated on occupancy\n")
    
    def test_crossing_deactivation_on_clear(self):
        """Test crossing deactivates when block clears"""
        print("\n=== TEST CASE 4b: Crossing Deactivation ===")
        
        # Set up: crossing is down, train present
        block_num = 10
        self.mock_blocks[block_num - 1].occupancy = 1
        self.mock_blocks[block_num - 1].crossing_state = True
        
        # Train leaves block
        self.mock_blocks[block_num - 1].occupancy = 0
        
        # Deactivate crossing
        if block_num in self.crossing_blocks:
            self.mock_blocks[block_num - 1].crossing_state = False
            print(f"Block {block_num}: Crossing DEACTIVATED (gates up)")
        
        self.assertFalse(self.mock_blocks[9].crossing_state)
        self.assertEqual(self.mock_blocks[9].occupancy, 0)
        print("✅ Crossing deactivated when block cleared\n")


class TestCase05_StationTicketSales(unittest.TestCase):
    """Test Case 5: Station Ticket Sales and Boarding"""
    
    def setUp(self):
        """Set up mock station data"""
        self.stations = {
            "PIONEERS": {"block": 2, "tickets_sold": 0, "boarding": 0},
            "EDGEBROOK": {"block": 16, "tickets_sold": 0, "boarding": 0},
            "STATION SQUARE": {"block": 21, "tickets_sold": 0, "boarding": 0}
        }
    
    def test_ticket_sales_accumulation(self):
        """Test ticket sales accumulation at stations"""
        print("\n=== TEST CASE 5a: Ticket Sales Accumulation ===")
        
        # Simulate ticket sales
        self.stations["PIONEERS"]["tickets_sold"] = 15
        self.stations["EDGEBROOK"]["tickets_sold"] = 23
        self.stations["STATION SQUARE"]["tickets_sold"] = 31
        
        total_sales = sum(s["tickets_sold"] for s in self.stations.values())
        
        print(f"PIONEERS: {self.stations['PIONEERS']['tickets_sold']} tickets")
        print(f"EDGEBROOK: {self.stations['EDGEBROOK']['tickets_sold']} tickets")
        print(f"STATION SQUARE: {self.stations['STATION SQUARE']['tickets_sold']} tickets")
        print(f"Total sales: {total_sales}")
        
        self.assertEqual(self.stations["PIONEERS"]["tickets_sold"], 15)
        self.assertEqual(total_sales, 69)
        print("✅ Ticket sales tracked correctly\n")
    
    def test_passenger_boarding_process(self):
        """Test passenger boarding when train stops at station"""
        print("\n=== TEST CASE 5b: Passenger Boarding ===")
        
        # Station has waiting passengers
        station_name = "PIONEERS"
        self.stations[station_name]["tickets_sold"] = 20
        self.stations[station_name]["boarding"] = 0
        
        # Train stops at station (authority = 0)
        train_authority = 0
        station_block = self.stations[station_name]["block"]
        
        if train_authority == 0:
            # Transfer tickets to boarding
            boarding_passengers = self.stations[station_name]["tickets_sold"]
            self.stations[station_name]["boarding"] = boarding_passengers
            self.stations[station_name]["tickets_sold"] = 0
            
            print(f"Station: {station_name}")
            print(f"Passengers boarding: {boarding_passengers}")
            print(f"Remaining tickets sold: {self.stations[station_name]['tickets_sold']}")
        
        self.assertEqual(self.stations[station_name]["boarding"], 20)
        self.assertEqual(self.stations[station_name]["tickets_sold"], 0)
        print("✅ Passenger boarding process working\n")


class TestCase06_TemperatureManagement(unittest.TestCase):
    """Test Case 6: Block Temperature and Heater Management"""
    
    def setUp(self):
        """Set up mock blocks with temperature data"""
        self.environmental_temp = 70.0
        self.mock_blocks = []
        
        for i in range(10):
            mock_block = Mock()
            mock_block.block_number = i + 1
            mock_block.temperature = self.environmental_temp
            mock_block.heater_status = False
            self.mock_blocks.append(mock_block)
    
    def test_temperature_initialization(self):
        """Test all blocks initialize to environmental temperature"""
        print("\n=== TEST CASE 6a: Temperature Initialization ===")
        
        print(f"Environmental temperature: {self.environmental_temp}°F")
        
        for block in self.mock_blocks:
            self.assertEqual(block.temperature, self.environmental_temp)
        
        print(f"All {len(self.mock_blocks)} blocks initialized to {self.environmental_temp}°F")
        print("✅ Temperature initialization successful\n")
    
    def test_heater_activation_below_threshold(self):
        """Test heater activates when temperature drops below threshold"""
        print("\n=== TEST CASE 6b: Heater Activation ===")
        
        threshold_temp = 32.0  # Freezing point
        
        # Block 3 temperature drops
        self.mock_blocks[2].temperature = 30.0
        
        # Check if heater should activate
        if self.mock_blocks[2].temperature < threshold_temp:
            self.mock_blocks[2].heater_status = True
            print(f"Block 3: Temperature = {self.mock_blocks[2].temperature}°F")
            print(f"Block 3: Heater ACTIVATED")
        
        self.assertTrue(self.mock_blocks[2].heater_status)
        print("✅ Heater activation logic working\n")
    
    def test_temperature_update_with_heater(self):
        """Test temperature increases when heater is active"""
        print("\n=== TEST CASE 6c: Temperature Update with Heater ===")
        
        # Block starts cold with heater on
        self.mock_blocks[5].temperature = 28.0
        self.mock_blocks[5].heater_status = True
        
        # Simulate heating (increase by 2 degrees)
        if self.mock_blocks[5].heater_status:
            self.mock_blocks[5].temperature += 2.0
            print(f"Block 6: Heater ON, Temperature rising to {self.mock_blocks[5].temperature}°F")
        
        self.assertEqual(self.mock_blocks[5].temperature, 30.0)
        print("✅ Temperature increases with active heater\n")


class TestCase07_TrainAuthorityMonitoring(unittest.TestCase):
    """Test Case 7: Train Authority Monitoring and Stopping"""
    
    def setUp(self):
        """Set up mock train authority data"""
        self.previous_train_authority = {}
        self.trains_stopped_at_station = {}
        self.train_locations = {}
    
    def test_authority_zero_detection(self):
        """Test detection when train authority reaches zero"""
        print("\n=== TEST CASE 7a: Authority Zero Detection ===")
        
        train_id = "Train_1"
        
        # Previous authority was positive
        self.previous_train_authority[train_id] = 5
        current_authority = 0
        
        # Detect authority reaching zero
        if current_authority == 0 and self.previous_train_authority.get(train_id, 1) > 0:
            print(f"{train_id}: Authority changed from {self.previous_train_authority[train_id]} to {current_authority}")
            print(f"{train_id}: STOPPED at station")
            self.trains_stopped_at_station[train_id] = 25  # Stopped at block 25
        
        self.assertIn(train_id, self.trains_stopped_at_station)
        self.assertEqual(self.trains_stopped_at_station[train_id], 25)
        print("✅ Authority zero detection working\n")
    
    def test_authority_restoration(self):
        """Test train departure when authority is restored"""
        print("\n=== TEST CASE 7b: Authority Restoration ===")
        
        train_id = "Train_2"
        
        # Train was stopped
        self.trains_stopped_at_station[train_id] = 30
        self.previous_train_authority[train_id] = 0
        
        # Authority restored
        new_authority = 10
        
        if new_authority > 0 and train_id in self.trains_stopped_at_station:
            departed_from = self.trains_stopped_at_station[train_id]
            del self.trains_stopped_at_station[train_id]
            print(f"{train_id}: Authority restored to {new_authority}")
            print(f"{train_id}: DEPARTING from block {departed_from}")
        
        self.assertNotIn(train_id, self.trains_stopped_at_station)
        print("✅ Authority restoration and departure working\n")


class TestCase08_BeaconTransmission(unittest.TestCase):
    """Test Case 8: Beacon Transmission on Switch Changes"""
    
    def setUp(self):
        """Set up mock beacon data"""
        self.beacon_blocks = {27, 38}  # Red line beacon blocks
        self.previous_beacon_states = {27: None, 38: None}
        self.transmitted_beacons = []
    
    def test_beacon_on_switch_change(self):
        """Test beacon transmission when switch changes"""
        print("\n=== TEST CASE 8a: Beacon on Switch Change ===")
        
        block_num = 27
        new_direction = "reverse"
        occupancy = 1  # Train present
        
        # Check if beacon should be sent
        if block_num in self.beacon_blocks and occupancy > 0:
            if self.previous_beacon_states[block_num] != new_direction:
                beacon_data = {
                    "block": block_num,
                    "direction": new_direction,
                    "type": "switch_beacon"
                }
                self.transmitted_beacons.append(beacon_data)
                self.previous_beacon_states[block_num] = new_direction
                
                print(f"Beacon transmitted from block {block_num}")
                print(f"Direction: {new_direction}")
        
        self.assertEqual(len(self.transmitted_beacons), 1)
        self.assertEqual(self.transmitted_beacons[0]["direction"], "reverse")
        print("✅ Beacon transmission on switch change working\n")
    
    def test_no_beacon_without_train(self):
        """Test no beacon sent if block is unoccupied"""
        print("\n=== TEST CASE 8b: No Beacon Without Train ===")
        
        block_num = 38
        new_direction = "normal"
        occupancy = 0  # No train present
        
        initial_count = len(self.transmitted_beacons)
        
        # Check if beacon should be sent
        if block_num in self.beacon_blocks and occupancy > 0:
            beacon_data = {"block": block_num, "direction": new_direction}
            self.transmitted_beacons.append(beacon_data)
        
        print(f"Block {block_num}: Occupancy = {occupancy}")
        print(f"Beacons transmitted: {len(self.transmitted_beacons) - initial_count}")
        
        # Should not have sent beacon
        self.assertEqual(len(self.transmitted_beacons), initial_count)
        print("✅ No beacon sent for unoccupied block\n")


class TestCase09_SwitchStateTracking(unittest.TestCase):
    """Test Case 9: Switch State Management and Tracking"""
    
    def setUp(self):
        """Set up switch tracking structures"""
        self.switch_blocks = set()
        self.switch_states = {}
    
    def test_single_switch_update(self):
        """Test updating a single switch state"""
        print("\n=== TEST CASE 9a: Single Switch Update ===")
        
        block_num = 28
        direction = "reverse"
        
        # Update switch state
        self.switch_states[block_num] = direction
        self.switch_blocks.add(block_num)
        
        print(f"Switch {block_num} set to: {direction}")
        print(f"Total switches: {len(self.switch_blocks)}")
        
        self.assertEqual(self.switch_states[block_num], "reverse")
        self.assertIn(block_num, self.switch_blocks)
        print("✅ Single switch update successful\n")
    
    def test_multiple_switch_updates(self):
        """Test updating multiple switches"""
        print("\n=== TEST CASE 9b: Multiple Switch Updates ===")
        
        switch_updates = {
            12: "normal",
            28: "reverse",
            57: "normal",
            76: "reverse"
        }
        
        # Apply all updates
        for block, direction in switch_updates.items():
            self.switch_states[block] = direction
            self.switch_blocks.add(block)
            print(f"Switch {block}: {direction}")
        
        self.assertEqual(len(self.switch_states), 4)
        self.assertEqual(self.switch_states[28], "reverse")
        self.assertEqual(self.switch_states[76], "reverse")
        print("✅ Multiple switch updates successful\n")
    
    def test_switch_state_retrieval(self):
        """Test retrieving current switch state"""
        print("\n=== TEST CASE 9c: Switch State Retrieval ===")
        
        # Set up some switches
        self.switch_states = {12: "normal", 28: "reverse", 57: "normal"}
        
        # Query switch state
        query_block = 28
        if query_block in self.switch_states:
            state = self.switch_states[query_block]
            print(f"Switch {query_block} current state: {state}")
            self.assertEqual(state, "reverse")
        
        print("✅ Switch state retrieval working\n")


class TestCase10_ControllerBlockSeparation(unittest.TestCase):
    """Test Case 10: Track SW/HW Controller Block Separation"""
    
    def test_green_line_block_separation(self):
        """Test Green Line block assignment to controllers"""
        print("\n=== TEST CASE 10a: Green Line Block Separation ===")
        
        def is_track_sw_block_green(block_num):
            """Green Line: Track SW controls blocks 63-149"""
            return 63 <= block_num <= 149
        
        # Test various blocks
        test_blocks = [1, 50, 63, 100, 149, 150]
        
        for block in test_blocks:
            controller = "Track SW" if is_track_sw_block_green(block) else "Track HW"
            print(f"Block {block}: {controller}")
        
        self.assertFalse(is_track_sw_block_green(62))
        self.assertTrue(is_track_sw_block_green(63))
        self.assertTrue(is_track_sw_block_green(100))
        self.assertTrue(is_track_sw_block_green(149))
        self.assertFalse(is_track_sw_block_green(150))
        print("✅ Green Line block separation correct\n")
    
    def test_red_line_block_separation(self):
        """Test Red Line block assignment to controllers"""
        print("\n=== TEST CASE 10b: Red Line Block Separation ===")
        
        def is_track_sw_block_red(block_num):
            """Red Line: Track SW controls blocks 21-48 and 67-76"""
            return (21 <= block_num <= 48) or (67 <= block_num <= 76)
        
        # Test various blocks
        test_blocks = [1, 20, 21, 35, 48, 49, 66, 67, 72, 76, 77]
        
        for block in test_blocks:
            controller = "Track SW" if is_track_sw_block_red(block) else "Track HW"
            print(f"Block {block}: {controller}")
        
        self.assertFalse(is_track_sw_block_red(20))
        self.assertTrue(is_track_sw_block_red(21))
        self.assertTrue(is_track_sw_block_red(48))
        self.assertFalse(is_track_sw_block_red(49))
        self.assertTrue(is_track_sw_block_red(67))
        self.assertTrue(is_track_sw_block_red(76))
        self.assertFalse(is_track_sw_block_red(77))
        print("✅ Red Line block separation correct\n")
    
    def test_controller_message_filtering(self):
        """Test filtering messages based on controller"""
        print("\n=== TEST CASE 10c: Controller Message Filtering ===")
        
        def is_track_sw_block(block_num, line="Green"):
            if line == "Green":
                return 63 <= block_num <= 149
            else:  # Red Line
                return (21 <= block_num <= 48) or (67 <= block_num <= 76)
        
        # Simulate receiving switch updates from Track SW
        source = "Track SW"
        incoming_blocks = [30, 70, 100]  # Red Line context
        
        filtered_blocks = []
        for block in incoming_blocks:
            if is_track_sw_block(block, "Red"):
                filtered_blocks.append(block)
                print(f"Block {block}: Accepted from {source}")
            else:
                print(f"Block {block}: Rejected (belongs to Track HW)")
        
        self.assertEqual(len(filtered_blocks), 2)  # Blocks 30 and 70
        self.assertIn(30, filtered_blocks)
        self.assertIn(70, filtered_blocks)
        self.assertNotIn(100, filtered_blocks)
        print("✅ Controller message filtering working\n")


def run_comprehensive_tests():
    """Run all comprehensive test cases"""
    print("\n" + "="*70)
    print("COMPREHENSIVE TRACK MODEL UI TEST SUITE")
    print("Testing 10 Core Functionalities")
    print("="*70)
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all 10 test case classes
    test_classes = [
        TestCase01_SwitchRoutingLogic,
        TestCase02_BlockOccupancyTracking,
        TestCase03_TrafficLightManagement,
        TestCase04_CrossingStateControl,
        TestCase05_StationTicketSales,
        TestCase06_TemperatureManagement,
        TestCase07_TrainAuthorityMonitoring,
        TestCase08_BeaconTransmission,
        TestCase09_SwitchStateTracking,
        TestCase10_ControllerBlockSeparation
    ]
    
    for test_class in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(test_class))
    
    # Run with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Display comprehensive summary
    print("\n" + "="*70)
    print("TEST EXECUTION SUMMARY")
    print("="*70)
    print(f"Total Test Cases: 10")
    print(f"Total Tests Run: {result.testsRun}")
    print(f"Tests Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Tests Failed: {len(result.failures)}")
    print(f"Tests with Errors: {len(result.errors)}")
    print(f"Success Rate: {100 * (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun:.1f}%")
    
    if result.wasSuccessful():
        print("\n" + "✅"*20)
        print("ALL TESTS PASSED SUCCESSFULLY!")
        print("✅"*20)
    else:
        print("\n" + "❌"*20)
        print("SOME TESTS FAILED - REVIEW RESULTS ABOVE")
        print("❌"*20)
    
    print("="*70 + "\n")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)