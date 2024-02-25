from fastapi import FastAPI, status, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from typing import Annotated
from pydantic import BaseModel
from sqlalchemy import event
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os
from sqlalchemy.orm import selectinload

import models
from models import Users
from models import Task
from models import logs_table

import auth
from auth import get_current_user

from utils.aes_encryption import generate_key_from_password, encrypt_data, decrypt_data

KEY_ENCRYPT_AES = os.getenv("KEY_ENCRYPT_AES")

app = FastAPI()
app.include_router(auth.router)

models.Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Depedensy yang harus terpenuhi (tersambung database dan mendapatkan token JWT)
db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

# class untuk object melakukan update user
class UpdateUserRequest(BaseModel):
    username: str
    email: str
    full_name: str
    phone_number: str

# Endpoint untuk mendapatkan seluruh user
@app.get('/', status_code=status.HTTP_200_OK)
async def get_all_users(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed!")

    result = db.query(Users).all()
    if not result:
        raise HTTPException(status_code=404, detail='users is not found')

    users = [{"id": user.id, "username": user.username, "email": user.email,
              "full_name": user.full_name, "phone_number": user.phone_number} for user in result]

    return {"users": users}

# Endpoint untuk mendapatkan seluruh user berdasarkan id
@app.get("/{user_id}", status_code=status.HTTP_200_OK)
async def get_user(user_id: int, user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed!")

    result = db.query(Users).filter(Users.id == user_id).first()
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user_data = {
        "id": result.id,
        "username": result.username,
        "email": result.email,
        "full_name": result.full_name,
        "phone_number": result.phone_number
    }

    return user_data

# Endpoint untuk menghapus user berdasarkan id
@app.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed!")

    result = db.query(Users).filter(Users.id == user_id).first()
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    db.delete(result)
    db.commit()
    return JSONResponse(content={"message": "User deleted successfully"})

# Endpoint untuk mengupdate user berdasarkan id
@app.put("/{user_id}", status_code=status.HTTP_200_OK)
async def update_user(user_id: int, user: user_dependency, update_user_request: UpdateUserRequest, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed!")

    existing_user = db.query(Users).filter(Users.id == user_id).first()
    if existing_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Periksa apakah ada perubahan pada bidang data
    if update_user_request.username != existing_user.username:
        existing_user.username = update_user_request.username

    if update_user_request.email != existing_user.email:
        existing_user.email = update_user_request.email

    if update_user_request.full_name != existing_user.full_name:
        existing_user.full_name = update_user_request.full_name

    if update_user_request.phone_number != existing_user.phone_number:
        existing_user.phone_number = update_user_request.phone_number

    db.commit()
    return JSONResponse(content={"message": "User updated successfully"})

# class untuk object melakukan update task
class UpdateTaskRequest(BaseModel):
    title: str
    description: str

# Endpoint untuk membuat task baru user yang sedang login
@app.post("/tasks/", status_code=status.HTTP_201_CREATED)
async def create_task(task_request: UpdateTaskRequest, user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed!")

    key = generate_key_from_password(KEY_ENCRYPT_AES)
    encrypted_desc = encrypt_data(task_request.description, key)
    new_task = Task(title=task_request.title,
                    encrypted_description=encrypted_desc, user_id=user['id'])

    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

# Endpoint untuk mendapatkan seluruh task berdasarkan user yang sedang login
@app.get("/tasks/", status_code=status.HTTP_200_OK)
async def get_all_tasks(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed!")

    tasks = db.query(Task).filter(Task.user_id == user['id']).all()
    key = generate_key_from_password(KEY_ENCRYPT_AES)

    tasks_list = []
    for task in tasks:
        decrypt_desc = decrypt_data(task.encrypted_description, key)
        task_dict = {
            "id": task.id,
            "title": task.title,
            "description": decrypt_desc,
            "user_id": task.user_id
        }
        tasks_list.append(task_dict)

    return JSONResponse(content={"tasks": tasks_list})

# Endpoint untuk mendapatkan task berdasarkan id dan user yang sedang login
@app.get("/tasks/{task_id}", status_code=status.HTTP_200_OK)
async def get_task(task_id: int, user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed!")

    task = db.query(Task).filter(Task.id == task_id,
                                 Task.user_id == user['id']).first()
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    key = generate_key_from_password(KEY_ENCRYPT_AES)   
    decrypt_desc = decrypt_data(task.encrypted_description, key)
    task_dict = {
        "id": task.id,
        "title": task.title,
        "description": decrypt_desc,
        "user_id": task.user_id
    }

    return JSONResponse(content=task_dict)

# Endpoint untuk menghapus task berdasarkan id
@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed!")

    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user['id']).first()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    db.delete(task)
    db.commit()
    return JSONResponse(content={"message": "Task deleted successfully"})

# Endpoint untuk mengupdate task berdasarkan id
@app.put("/tasks/{task_id}", status_code=status.HTTP_200_OK)
async def update_task(task_id: int, task_request: UpdateTaskRequest, user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication failed!")

    task = db.query(Task).filter(Task.id == task_id, Task.user_id == user['id']).first()
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")

    key = generate_key_from_password(KEY_ENCRYPT_AES)   
    decrypt_desc = encrypt_data(task_request.description, key)
    task.title = task_request.title
    task.encrypted_description = decrypt_desc

    db.commit()
    return JSONResponse(content={"message": "Task Updated successfully"})


# Fungsi untuk menambahkan log operasi INSERT
def log_insert_operation(_, connection, target):
    key = generate_key_from_password(KEY_ENCRYPT_AES)
    encrypted_data = encrypt_data(str(target), key)
    log_entry = {'operation': 'CREATE', 'data': encrypted_data}
    connection.execute(logs_table.insert().values(log_entry))

# Fungsi untuk menambahkan log operasi UPDATE
def log_update_operation(_, connection, target):
    key = generate_key_from_password(KEY_ENCRYPT_AES)
    encrypted_data = encrypt_data(str(target), key)
    log_entry = {'operation': 'UPDATE', 'data': encrypted_data}
    connection.execute(logs_table.insert().values(log_entry))

# Fungsi untuk menambahkan log operasi DELETE
def log_delete_operation(_, connection, target):
    key = generate_key_from_password(KEY_ENCRYPT_AES)
    encrypted_data = encrypt_data(str(target), key)
    log_entry = {'operation': 'DELETE', 'data': encrypted_data}
    connection.execute(logs_table.insert().values(log_entry))


event.listen(Users, 'after_insert', log_insert_operation)
event.listen(Users, 'after_update', log_update_operation)
event.listen(Users, 'after_delete', log_delete_operation)


