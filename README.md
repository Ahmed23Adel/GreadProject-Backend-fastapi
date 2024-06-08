# Rowling Backend: FastAPI Server for Plant Disease Detection

## Overview
Rowling Backend is a FastAPI server that serves as the backend for the Rowling Plant Disease Detection System. It provides RESTful APIs for interacting with the system, including uploading images, retrieving detection results, and managing user authentication.

## Features
- RESTful APIs for image upload, disease detection, and result retrieval.
- MongoDB integration for data storage and retrieval.
- User authentication and authorization.
- Asynchronous request handling for scalability.

## Installation
1. Install required Python libraries:
    ```bash
    pip install fastapi uvicorn pymongo
    ```
2. Clone the repository:
    ```bash
    git clone <repository-url>
    cd rowling-backend
    ```
3. Configure MongoDB connection in `config.py`.

## Usage
1. Start the FastAPI server:
    ```bash
    python runserver.py
    ```
2. Access the Swagger UI at `http://localhost:8000/docs` for API documentation and testing.

## Directory Structure
- `app/`: Contains the FastAPI application modules.
- `models/`: MongoDB models and schemas.
- `utils/`: Utility functions and helpers.
- `runserver.py`: Main script to start the FastAPI server.

## Configuration
- Update MongoDB connection settings in `config.py`.

## API Endpoints
- `/upload`: Upload images for disease detection.
- `/results`: Retrieve detection results.
- `/auth`: User authentication and authorization.

## Credits
- FastAPI for providing a modern web framework.
- MongoDB for flexible and scalable database storage.
- Swagger UI for interactive API documentation.

## License
This project is licensed under the MIT License.


