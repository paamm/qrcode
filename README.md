# QRcode

QRCode is a simple library that generates QR codes without the use of other libraries (except PIL and numpy for image
generation).



## Usage

```python
from qrcode.image import QRImage

# Create a new QR code
code = QRImage(version=1, ec_level="L", message="message")

# Access the Pillow image object
pillow_image = code.get_image()

# Change code configuration
code.set_version(2)
code.set_error_correction_level("Q")
code.set_message("Hello World!")
pillow_image = code.get_image()  # Will regenerate image with updated data.
```



## Goal

The goal of this project was to learn about the QR code standard and to implement it from start to finish without the
help of external libraries. This isn't meant to be a super optimized way of generating QR codes but simply to learn
how they are made.

#### Limitations

* No kanji support
* No ECI mode