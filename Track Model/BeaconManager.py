#

class BeaconManager:
    """Class to manage beacon operations for track blocks."""

    @staticmethod
    def is_beacon_active(block):
        """Check if beacon has any bits set (not all zeros)."""
        if hasattr(block, 'beacon') and isinstance(block.beacon, list):
            if len(block.beacon) in (128, 256):
                return any(bit != 0 for bit in block.beacon)
        return False

    @staticmethod
    def get_beacon_bits(block, start_bit=0, num_bits=8):
        """Get a slice of beacon bits for display."""
        if hasattr(block, 'beacon') and isinstance(block.beacon, list):
            length = len(block.beacon)
            if length in (128, 256):
                end_bit = min(start_bit + num_bits, length)
                return block.beacon[start_bit:end_bit]
        return [0] * num_bits

    @staticmethod
    def set_beacon_bit(block, bit_position, value):
        """Set a specific beacon bit."""
        if (hasattr(block, 'beacon') and isinstance(block.beacon, list) and 
            len(block.beacon) in (128, 256) and 0 <= bit_position < len(block.beacon)):
            block.beacon[bit_position] = 1 if value else 0
            return True
        return False

    @staticmethod
    def set_beacon_bits(block, start_bit, bit_values):
        """Set multiple beacon bits starting from start_bit."""
        if (hasattr(block, 'beacon') and isinstance(block.beacon, list) and 
            len(block.beacon) in (128, 256) and 0 <= start_bit < len(block.beacon)):
            for i, value in enumerate(bit_values):
                if start_bit + i < len(block.beacon):
                    block.beacon[start_bit + i] = 1 if value else 0
            return True
        return False

    @staticmethod
    def beacon_to_hex(block):
        """Convert 256-bit beacon to 64-character hex string (or 128-bit to 32-char)."""
        if hasattr(block, 'beacon') and isinstance(block.beacon, list):
            length = len(block.beacon)
            if length in (128, 256):
                hex_string = ""
                for i in range(0, length, 8):
                    byte = 0
                    for j in range(8):
                        if i + j < length and block.beacon[i + j]:
                            byte |= (1 << (7 - j))
                    hex_string += f"{byte:02x}"
                return hex_string
        return "0" * (len(block.beacon)//4 if hasattr(block, 'beacon') else 64)

    @staticmethod
    def beacon_from_hex(block, hex_string):
        """Set beacon from hex string."""
        if (hasattr(block, 'beacon') and isinstance(block.beacon, list) and
            len(block.beacon) in (128, 256) and len(hex_string) == len(block.beacon)//4):
            for i in range(0, len(hex_string), 2):
                byte_val = int(hex_string[i:i+2], 16)
                for j in range(8):
                    bit_pos = (i // 2) * 8 + j
                    if bit_pos < len(block.beacon):
                        block.beacon[bit_pos] = 1 if (byte_val & (1 << (7 - j))) else 0
            return True
        return False
