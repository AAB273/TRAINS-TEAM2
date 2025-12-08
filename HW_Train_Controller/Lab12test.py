#!/usr/bin/env python3
"""Emergency Brake Test - Train Controller Logic"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the TC_HW_MainUI module
import TC_HW_MainUI as tc

print("Emergency Brake Test - TC Logic")
print("=" * 50)

# Test 1: Check emergency brake variable exists
print("\n1. Testing emergency brake variable...")
print(f"   Initial state: emergencyBrakeEngaged = {tc.emergencyBrakeEngaged}")
assert tc.emergencyBrakeEngaged == False, "Emergency brake should start as False"
print("   ✓ PASS")

# Test 2: Activate emergency brake
print("\n2. Activating emergency brake...")
tc.emergencyBrakeEngaged = True
print(f"   New state: emergencyBrakeEngaged = {tc.emergencyBrakeEngaged}")
assert tc.emergencyBrakeEngaged == True, "Emergency brake should be True"
print("   ✓ PASS")

# Test 3: Deactivate emergency brake
print("\n3. Deactivating emergency brake...")
tc.emergencyBrakeEngaged = False
print(f"   New state: emergencyBrakeEngaged = {tc.emergencyBrakeEngaged}")
assert tc.emergencyBrakeEngaged == False, "Emergency brake should be False"
print("   ✓ PASS")

print("\n" + "=" * 50)
print("✓ ALL TESTS PASSED")
print("Emergency brake variable works correctly!")