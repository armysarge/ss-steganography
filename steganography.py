"""
steganography.py - Simplified and optimized steganography implementation for SS Steganography
"""

import os
import numpy as np
from PIL import Image
import base64
import random
import hashlib
import struct
import time

class AdvancedSteganography:
    """
    A class implementing steganography techniques with reliable
    encoding and decoding of messages in images.
    """

    def __init__(self):
        self.marker = b'SSSTEGO'  # Marker to identify our encoding
        self.debug = False  # Set to True to enable debug prints

    def _log(self, message):
        """Print debug messages if debugging is enabled"""
        if self.debug:
            print(f"[Stego] {message}")

    def _embed_bit(self, value, bit):
        """Embed a single bit into a byte value"""
        # Ensure value is a positive integer in range 0-255
        value = max(0, min(255, int(value)))
        bit = int(bit) & 1  # Ensure bit is 0 or 1

        # Clear the least significant bit and set it to our data bit
        return (value & 0xFE) | bit

    def _extract_bit(self, value):
        """Extract a single bit from a byte value"""
        # Return the least significant bit
        return value & 1

    def encode(self, image_path, message, password=None, output_path=None):
        """
        Hide a message in an image file

        Args:
            image_path: Path to the carrier image
            message: The secret message to hide
            password: Optional password (used for pixel selection)
            output_path: Where to save the stego-image (defaults to adding "_stego" to filename)

        Returns:
            Path to the output stego-image
        """
        start_time = time.time()

        # Open and convert image to RGB if necessary
        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Get image data as a numpy array
        img_array = np.array(img, dtype=np.uint8)
        height, width, _ = img_array.shape

        # Create message payload with fixed header format for easier detection
        # Format: MARKER + LENGTH(4 bytes) + DATA
        message_data = message.encode()
        message_bytes = self.marker + struct.pack("<I", len(message_data)) + message_data

        # Check if the image is large enough for the message
        required_bits = len(message_bytes) * 8
        available_bits = width * height * 3  # 3 channels per pixel

        if required_bits > available_bits:
            raise ValueError(f"Image too small to hide message. Need {required_bits} bits, have {available_bits}.")

        self._log(f"Message size: {len(message_bytes)} bytes / {required_bits} bits")
        self._log(f"Image capacity: {width}x{height} pixels / {available_bits} bits")

        # Create a pixel mapping based on password or default sequence
        pixel_coords = []
        if password:
            # Seed random with the password hash for deterministic sequence
            seed = int.from_bytes(hashlib.sha256(password.encode()).digest()[:4], 'big')
            random.seed(seed)

            # Generate coordinates
            pixels = list(range(width * height))
            random.shuffle(pixels)
            pixel_coords = [(i % width, i // width) for i in pixels]
        else:
            # Simple sequential coordinates in a pattern that's less noticeable
            pixel_coords = [(x, y) for y in range(height) for x in range(width)]

        # Create a copy of the image array for modification
        stego_array = img_array.copy()

        # Convert message to bits
        bits = []
        for b in message_bytes:
            for i in range(8):
                bits.append((b >> i) & 1)

        # Embed bits in the pixels
        bit_index = 0
        for x, y in pixel_coords:
            if bit_index >= len(bits):
                break

            # Get the pixel
            r, g, b = stego_array[y, x]

            # Embed up to 3 bits in this pixel (one per channel)
            if bit_index < len(bits):
                r = self._embed_bit(r, bits[bit_index])
                bit_index += 1

            if bit_index < len(bits) and bit_index < len(bits):
                g = self._embed_bit(g, bits[bit_index])
                bit_index += 1

            if bit_index < len(bits) and bit_index < len(bits):
                b = self._embed_bit(b, bits[bit_index])
                bit_index += 1

            # Update the pixel
            stego_array[y, x] = [r, g, b]

        # Create stego image from modified array
        stego_img = Image.fromarray(stego_array)

        # Save the image
        if output_path is None:
            base, ext = os.path.splitext(image_path)
            output_path = f"{base}_stego.png"

        stego_img.save(output_path, 'PNG')

        elapsed = time.time() - start_time
        self._log(f"Encoding completed in {elapsed:.2f} seconds")

        return output_path

    def decode(self, image_path, password=None):
        """
        Extract a hidden message from a stego-image

        Args:
            image_path: Path to the stego-image
            password: Password for pixel selection (must match encoding password)

        Returns:
            Decoded message or None if extraction failed
        """
        start_time = time.time()

        # Open the image
        img = Image.open(image_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Get image data as a numpy array
        img_array = np.array(img, dtype=np.uint8)
        height, width, _ = img_array.shape

        self._log(f"Decoding image: {width}x{height} pixels")

        # Try to decode with the provided password
        result = self._decode_image(img_array, width, height, password)
        if result:
            elapsed = time.time() - start_time
            self._log(f"Decoding successful in {elapsed:.2f} seconds")
            return result

        # If decoding with password failed, try without password
        if password:
            self._log("Decoding with password failed. Trying without password...")
            result = self._decode_image(img_array, width, height, None)
            if result:
                elapsed = time.time() - start_time
                self._log(f"Decoding successful in {elapsed:.2f} seconds")
                return result

        elapsed = time.time() - start_time
        self._log(f"Decoding failed after {elapsed:.2f} seconds")
        return None

    def _decode_image(self, img_array, width, height, password=None):
        """
        Internal method to extract message from image array

        Args:
            img_array: NumPy array of image data
            width: Image width
            height: Image height
            password: Optional password for pixel mapping

        Returns:
            Decoded message or None if extraction failed
        """
        try:
            # Create the same pixel mapping as used for encoding
            if password:
                # Use password to generate the same sequence
                seed = int.from_bytes(hashlib.sha256(password.encode()).digest()[:4], 'big')
                random.seed(seed)

                pixels = list(range(width * height))
                random.shuffle(pixels)
                pixel_coords = [(i % width, i // width) for i in pixels]
            else:
                # Simple sequential coordinates in same pattern as encoding
                pixel_coords = [(x, y) for y in range(height) for x in range(width)]

            # Extract bits from pixels - we'll read enough to find the header first
            extracted_bits = []
            marker_size = len(self.marker)
            header_size = marker_size + 4  # Marker + 4 bytes for length
            needed_bits = header_size * 8

            # Read enough bits for the header
            for idx, (x, y) in enumerate(pixel_coords):
                if len(extracted_bits) >= needed_bits:
                    break

                r, g, b = img_array[y, x]
                extracted_bits.append(self._extract_bit(r))
                extracted_bits.append(self._extract_bit(g))
                extracted_bits.append(self._extract_bit(b))

                # Progress indicator every 10000 pixels
                if idx % 10000 == 0 and idx > 0:
                    self._log(f"Processed {idx} pixels...")

            # Convert header bits to bytes
            header_bytes = bytearray()
            for i in range(0, header_size * 8, 8):
                if i + 8 <= len(extracted_bits):
                    byte = 0
                    for j in range(8):
                        if extracted_bits[i + j]:
                            byte |= (1 << j)
                    header_bytes.append(byte)

            # Check if our marker is present
            if len(header_bytes) >= marker_size and header_bytes[:marker_size] == self.marker:
                # Extract message length from header (4 bytes after marker)
                message_length = struct.unpack("<I", header_bytes[marker_size:marker_size+4])[0]

                # Validate the length
                if message_length <= 0 or message_length > width * height:
                    self._log(f"Invalid message length: {message_length}")
                    return None

                self._log(f"Found valid marker. Message length: {message_length} bytes")

                # Calculate how many more bits we need
                total_bytes_needed = header_size + message_length
                total_bits_needed = total_bytes_needed * 8

                # Continue reading bits if needed
                if len(extracted_bits) < total_bits_needed:
                    start_idx = len(extracted_bits) // 3  # We read 3 bits per pixel

                    for idx, (x, y) in enumerate(pixel_coords[start_idx:]):
                        if len(extracted_bits) >= total_bits_needed:
                            break

                        r, g, b = img_array[y, x]
                        extracted_bits.append(self._extract_bit(r))
                        extracted_bits.append(self._extract_bit(g))
                        extracted_bits.append(self._extract_bit(b))

                        # Progress indicator
                        if (idx + start_idx) % 10000 == 0:
                            self._log(f"Processed {idx + start_idx} pixels...")

                # Convert all bits to bytes
                all_bytes = bytearray()
                for i in range(0, total_bits_needed, 8):
                    if i + 8 <= len(extracted_bits):
                        byte = 0
                        for j in range(8):
                            if extracted_bits[i + j]:
                                byte |= (1 << j)
                        all_bytes.append(byte)

                # Skip the header and extract just the message data
                if len(all_bytes) >= total_bytes_needed:
                    message_data = all_bytes[header_size:header_size+message_length]

                    # Try to decode as UTF-8 text
                    try:
                        return message_data.decode('utf-8')
                    except UnicodeDecodeError:
                        self._log("Failed to decode as UTF-8")
                        # Return as base64 if not valid UTF-8
                        return base64.b64encode(message_data).decode('ascii')
                else:
                    self._log(f"Not enough bytes extracted: {len(all_bytes)} < {total_bytes_needed}")
            else:
                self._log("Marker not found in image")

            # If we got here, decoding failed
            return None

        except Exception as e:
            self._log(f"Error during decoding: {e}")
            return None
