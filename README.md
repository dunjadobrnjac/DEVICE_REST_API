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
   - `JWT_KEY`: Secret key required for JWT signing.
   
Example:
```plaintext
DATABASE_URL=your_database_url
JWT_KEY=your_jwt_secret_key
```
(Note: You can find an example in the `.env.example` file.)

## Running the Application
To run the application, execute the following command:
```bash
flask run
```
