# REST API for IoT devices

## Setup Instructions

### Install Dependencies
To install all the required dependencies, use the following command:
```bash
pip install -r requirements.txt
```

### Environment Setup
1. Create a `.env` file in the root directory.
2. Add the following keys to the `.env` file:
   - `DATABASE_URL`: URL for the database.
      (Optional, default is "sqlite:///data.db")
   - `JWT_KEY`: Secret key required for JWT signing.
      (Generated automatically using the provided script)


Example:
```plaintext
DATABASE_URL=your_database_url
JWT_KEY=your_jwt_secret_key
```
(Note: You can find an example in the `.env.example` file.)

Before running the application, you need to generate the JWT secret key. You can do this by executing the provided script `generate_secret_key.py`. This script needs to be run only once before starting the application. It generates the `.env` file with the JWT secret key.

#### Script: generate_secret_key.py
```python
#!python3
import os
import secrets

from dotenv import load_dotenv, set_key

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENVIRONMENT_FILE = os.path.join(BASE_DIR, ".env")
load_dotenv(ENVIRONMENT_FILE)

def main():
   # openssl rand -hex 32
   secret_key = secrets.token_hex(32)
   set_key(
      dotenv_path=ENVIRONMENT_FILE,
      key_to_set='JWT_KEY',
      value_to_set=secret_key,
      quote_mode='auto',
      export=False
   )
   print("Secret key generated and written to .env file.") 

if __name__ == '__main__':
   main()
```

To run the script, execute the following command:
```bash
python generate_secret_key.py
```

## Running the Application
After generating the JWT secret key, you can run the application. Execute the following command:
```bash
flask run
```
(Note: Starting the application will not be possible if the JWT key is not defined in the `.env` file.)
