# E-commerce API

This is an e-commerce API built with Django and Django REST framework. It provides endpoints for managing products and orders.

## Setup Instructions

### Prerequisites

- Docker
- Docker Compose
- Python 3.11
- MySQL

### Local Development (Running with Docker container)
1. **Clone the repository:**

   ```bash
   git clone 
   cd ecom
   ```

2. **Build and run the docker container**
    ```bash
    docker compose up --build
    ```
3. **Running migrations**
    ```bash
    docker exec django-web ./manage.py migrate app
    ```
    Webserver should be up and running on `port 8000`

4. **Restart webcontainer**
    
    If you are developing and want to test the changes made in the api make sure to restart the container
    ```bash
    docker compose restart web
    ```


## Running tests

- To run test locally run following command:
    ```bash
    docker exec -it django-web ./manage.py migrate app
    ```
