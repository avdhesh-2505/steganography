def bytes_to_binary(data_bytes):
    """
    Convert bytes to a binary string (e.g., b'A' -> '01000001').
    """
    return ''.join(format(byte, '08b') for byte in data_bytes)
def binary_to_bytes(binary_string):
    """
    Convert a binary string to bytes (e.g., '01000001' -> b'A').
    """
    bytes_list = []
    for i in range(0, len(binary_string), 8):
        byte_str = binary_string[i:i+8]
        if len(byte_str) < 8:
            break
        bytes_list.append(int(byte_str, 2))
    return bytes(bytes_list)
# --- Error Correction (Channel Coding) ---
# Since Neural Networks define a "Noisy Channel", we use Recurisve/Repetition codes
# to ensure data integrity.
def add_error_correction(binary_string, n=5):
    """
    Repeat every bit n times.
    '1' -> '11111'
    """
    return "".join([bit * n for bit in binary_string])
def remove_error_correction(binary_string, n=5):
    """
    Recover bits using Majority Vote.
    '11101' -> Encoded '1' (4 ones vs 1 zero)
    """
    decoded = []
    for i in range(0, len(binary_string), n):
        chunk = binary_string[i:i+n]
        ones = chunk.count('1')
        zeroes = chunk.count('0')
        if ones > zeroes:
            decoded.append('1')
        else:
            decoded.append('0')
    return "".join(decoded)