# RSA-digital-signature
> Gui version (implemented in kivy)

Python implementation of RSA digital signature algorithm

### Installing / Getting started
To start using this application, you should have installed:
- Python 3.7
    * kivy

### Features
  - Generating RSA keys automatically (default key length is 1024 bit)
  - Creating digital signature
  - Checking digital signature using public key
  - Error handling messages

### File description

#### primes.py
Generating long prime numbers, checking if number is prime, calculating gcd of two files.
    
#### encryption.py
Creating RSA public/private keys, checking if this keys are valid, creating and checking digital signatures.

#### gui.py
Executable file. Showing application gui. It's handling all interactions in gui

#### rsasignature.kv
Kivy file for creating gui elements. Implements style and position of elements in gui.

### Screenshots
![Main window](https://github.com/alj06ka/RSA-digital-signature/blob/master/Screenshots/1.png)
![Setting keys menu](https://github.com/alj06ka/RSA-digital-signature/blob/master/Screenshots/2.png)
![Checking signature](https://github.com/alj06ka/RSA-digital-signature/blob/master/Screenshots/3.png)
