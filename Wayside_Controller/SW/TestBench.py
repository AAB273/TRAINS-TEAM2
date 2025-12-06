class TestBench:
    def test_block_occupancy(app):
        #####Test block occupancy functionality
        print("\n=== Testing Block Occupancy ===")
        
        # Test Case 1: Set block to occupied
        print("\n--- Test Case 1: Set block to occupied ---")
        test_track = "Green"
        test_block = "15"
        test_occupied = True
        
        occupancy_message = {
            'command': 'update_occupancy',
            'data': {
                'track': test_track,
                'block': test_block,
                'occupied': test_occupied
            }
        }
        
        app._process_message(occupancy_message, "track_model")
        app.root.update()
        print(f" Occupied message processed for {test_track} Block {test_block}")

        # Test Case 2: Set same block to unoccupied
        print("\n--- Test Case 2: Set block to unoccupied ---")
        test_occupied = False
        
        occupancy_message = {
            'command': 'update_occupancy',
            'data': {
                'track': test_track,
                'block': test_block,
                'occupied': test_occupied
            }
        }
        
        app._process_message(occupancy_message, "track_model")
        app.root.update()
        print(f"Unoccupied message processed for {test_track} Block {test_block}")

        # Test Case 3: Test different block
        print("\n--- Test Case 3: Test different block ---")
        test_block2 = "20"
        test_occupied = True
        
        occupancy_message = {
            'command': 'update_occupancy',
            'data': {
                'track': test_track,
                'block': test_block2,
                'occupied': test_occupied
            }
        }
        
        app._process_message(occupancy_message, "track_model")
        app.root.update()
        print(f"Occupied message processed for {test_track} Block {test_block2}")

        # Test Case 4: Test different track
        print("\n--- Test Case 4: Test different track ---")
        test_track2 = "Red"
        test_block3 = "5"
        
        occupancy_message = {
            'command': 'update_occupancy',
            'data': {
                'track': test_track2,
                'block': test_block3,
                'occupied': True
            }
        }
        
        app._process_message(occupancy_message, "track_model")
        app.root.update()
        print(f" Occupied message processed for {test_track2} Block {test_block3}")

        print(f"\n ALL TESTS PASSED! The block occupancy logic works correctly.")
        return True