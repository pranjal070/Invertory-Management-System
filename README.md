<<<<<<< HEAD
# Invertory-Management-System
=======
# INVENTORY MANAGEMENT SYSTEM
Stockaly is a powerful Inventory Management System built using Django, designed to simplify stock tracking and management. It combines Python for backend logic, HTML and CSS for a clean and responsive user interface, and JavaScript for interactive features. Stockaly helps businesses efficiently manage products, monitor inventory levels, and streamline operations with an intuitive dashboard and real-time updates.


## Deployment

To deploy this project run

1. Create a virtual environment in your vs code by hitting the command in the terminal
```bash
  python -m venv my-env
```
2. Now activate the virtual environment
```bash
  .\my-env\bin\activate
```
3. Now change the directory first to Flask-Api using cd command in the terminal and run the following commands in the following sequential order.
```bash
  pip install -r requirements.txt
```
```bash
  python app.py
```
4. Now do the same for stockaly simple create a new terminal activate the virtual environment cd to stockaly folder and run the following command 
```bash
  pip manage.py makemigrations
  ```
```bash
  pip manage.py migrate
  ```
```bash
  python manage.py runserver
``` 

6. You are all set , also you can check the requirements.txt file for the essential requirements for the project.

>>>>>>> 45d9d27 (Initial commit with project files)
