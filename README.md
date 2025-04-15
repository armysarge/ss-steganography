[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-Donate-brightgreen?logo=buymeacoffee)](https://www.buymeacoffee.com/armysarge)

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![GitHub issues](https://img.shields.io/github/issues/armysarge/ss-steganography)](https://github.com/armysarge/ss-steganography/issues)


# SS Steganography

A powerful steganography application that allows hiding and retrieving messages within image files using advanced encryption and embedding techniques.

## Features

- Graphical user interface for ease of use
- Multiple steganography methods with strong encryption
- Support for various image formats (PNG, JPG, BMP)
- Resistance to common steganalysis techniques
- Message encryption before embedding for added security

## Requirements

- Python 3.8+
- Pillow (PIL Fork)
- NumPy
- pycryptodome
- tkinter

## Installation

```bash
pip install -r requirements.txt
```

## Usage

Run the application:

```bash
python ss_steganography.py
```

1. Select an image file
2. Enter a message to hide or retrieve a hidden message
3. Provide a password for encryption/decryption
4. Choose operation (encode/decode)

## Security Notes

The application uses multiple layers of security:
- AES-256 encryption of message data
- Pseudorandom distribution of data across image pixels
- Minimal statistical footprint in the carrier image

## License

MIT
