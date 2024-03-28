# REST API for IoT devices

## Cloning the Project
To clone this project from GitHub, use the following command:
```bash
git clone <repository_url>
```

## Database Setup
Before running the project, you need to install a database (e.g., PostgreSQL) on your local machine or server. After installation, configure the database instance to obtain the database connection URL, typically in the format of postgresql://username:password@localhost:5432/database_name, which you'll use in your project configuration.

Instead, you can create an account on ElephantSQL's platform and provision a new database instance there. Once you've done that, you'll obtain the database connection URL from ElephantSQL, which you'll use in your project configuration.

## Setup Instructions

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

### Install Dependencies
To install all the required dependencies, use the following command:
```bash
pip install -r requirements.txt
```

### Database Model Definition
The database model is defined using SQLAlchemy. To create the required tables in the database, execute the following command:
```bash
flask db upgrade
```

## Running the Application
After generating the JWT secret key, you can run the application. Execute the following command:
```bash
waitress-serve --port=5000 wsgi:app 
```
(Note: Starting the application will not be possible if the JWT key is not defined in the `.env` file.)

## Developer's Guide

1. Clone Project:
- Use git clone <repository_url> to download the project from GitHub.

2. Database Setup:
- Install a database (e.g., PostgreSQL).
- Configure the database connection URL.
- Alternatively, use ElephantSQL for a hosted database solution.

3. Environment Setup:
- Create a .env file with DATABASE_URL and JWT_KEY.
- Generate JWT secret key using generate_secret_key.py script.

4. Install Dependencies:
- Run pip install -r requirements.txt to install required dependencies.

5. Database Model:
- Execute flask db upgrade for database migration.

6. Run Application:
- Start the application with flask run.


## Testing

### Running Tests with Postman

To run the tests for this project using Postman, follow these steps:

1. **Install Postman**: Make sure you have Postman installed on your computer. Postman is a free tool used for API development and testing.

2. **Load Tests into Postman**: After installing Postman, import the tests from the `test/postman` folder in this project. To do this, open Postman, click on the `Import` button in the top-left corner, choose the file with the tests, and click `Import`.

3. **Load Postman Environment**: Also import the Postman environment from the `test/postman` folder. Click on the `Manage Environments` button in Postman, then `Import`, choose the environment file, and click `Import`.

4. **Run the Tests**: Once the tests and environment are loaded, select the collection of tests you want to run from the left sidebar in Postman. Then, click the `Run` button to execute the tests. Postman will run all tests in the collection using the defined environment variables.

After running the tests, you'll receive the test results within Postman, showing which tests passed and which failed, along with details for each test.

### Running tests with Newman

#### Prerequisites
- Install `newman` following instructions from [here](https://learning.postman.com/fdocs/running-collections/using-newman-cli/command-line-integration-with-newman/)
#### Execute testing locally
- run (test application) on separate terminal, either of scripts: 
   ```commandline
   test_run.bat
   ```
   or
   ```bash
   test_run.sh
   ```
   or
   ```powerShell
   test_run.ps1
   ```
- run (tests) on other terminal, depending on the terminal:
   ```commandline
   cd test
   ./postman.bat
   ```
   
   or 
   
   ```shell
   cd test
   ./postman.sh
   ```