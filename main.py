from fastapi import FastAPI, Depends, HTTPException, status
from schemas import *
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from crud import *
from auth import *
from bson import ObjectId
from typing import List, Dict
from datetime import datetime

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Endpoint para obtener el token (login)
@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = get_user_by_username(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": form_data.username, "is_teacher": user["is_teacher"]}
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Verificación del token en endpoints protegidos
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        # Decodificar el token JWT
        user_data = verify_token(token)  # Suponiendo que `verify_token` decodifica el token y verifica su validez.
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token or expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token or expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = UserInDB(
        username=user_data["sub"],
        id=user_data["sub"],  # O como sea que almacenaste el ID en tu JWT
        is_teacher=user_data.get("is_teacher", False),
        hashed_password="",  # No necesitas el `hashed_password` aquí
        password=""
    )
    return user

# Crear usuario (alumno o profesor)
@app.post("/register/")
async def register_user(user: UserCreate):
    # Verificar si el usuario ya existe
    existing_user = get_user_by_username(user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    create_user(user)
    return {"message": "User created successfully"}

#---------------------------------------------------------------------------------------------------------------------------------------
# Funcionalidades del sistema

# Inscripción de alumno a materia (Solo para maestros)
@app.post("/enroll/")
async def inscribir_estudiante_a_materia(enrollment: EnrollmentCreate, user: UserInDB = Depends(get_current_user)):
    
    # Verificar que el usuario sea maestro
    if not user.is_teacher:
        raise HTTPException(status_code=403, detail="Only teachers can enroll")

    # Verificar si la materia existe
    subject = get_subject_by_id(enrollment.subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    enroll_student(enrollment)
    return {"message": "Student enrolled successfully"}

# Asignar calificación (solo para profesores)
@app.put("/assign_grade/")
async def calificar_estudiente(enrollment_id: str, grade: float, user: UserInDB = Depends(get_current_user)):
    # Verificar que el usuario sea profesor
    if not user.is_teacher:
        raise HTTPException(status_code=403, detail="Only professors can assign grades")

    # Asignar calificación
    assign_grade(enrollment_id, grade)
    return {"message": "Grade assigned successfully"}

# Ver las materias de un profesor (Solo para profesores)
@app.get("/showsubjects/{professor_id}")
async def materias_de_profesor(professor_id: str, user: UserInDB = Depends(get_current_user)):
    # Verificar que el usuario sea profesor
    if not user.is_teacher:
        raise HTTPException(status_code=403, detail="Only professors can view their subjects")

    subjects = get_subjects_by_professor(professor_id)
    subjects = convert_objectid_to_str(subjects)
    return {"subjects": subjects}

# Ver las inscripciones de un alumno (Solo para alumnos)
@app.get("/enrollments/{student_id}")
async def obtener_materias_estudientes(student_id: str, user: AlumnoCreate = Depends(get_current_user)):
    # Verificar que el usuario sea alumno
    if user.is_teacher:
        raise HTTPException(status_code=403, detail="Only students can view their enrollments")

    enrollments = get_enrollments_by_student(student_id)

    result = []

    for enrollment in enrollments:
        subject = get_subject_by_id(enrollment["subject_id"])
        if subject:
            # Obtener el nombre del profesor
            professor = get_user_by_id(subject.professor_id)
            professor_name = professor.first_name + professor.last_name if professor else "Unknown"

            result.append({
                "subject_name": subject.name, 
                "professor_name": professor_name,
                "grade": enrollment.get("grade")
            })
        else:
            result.append({
                "subject_name": "Unknown", 
                "professor_name": "Unknown", 
                "grade": enrollment.get("grade")
            })

    return convert_objectid_to_str(result)
    #return {"enrollments": enrollments}



#---------------------------------------------------------------------------------------------------------------------------------------

# CRUD de todas las entidades
# Materias CRUD

@app.get("/subjects/")
async def obtener_materias():
    subjects = db.subjects.find()  # Suponiendo que `db.subjects` es la colección de materias
    return convert_objectid_to_str(list(subjects))


@app.get("/subjects/{subject_id}")
async def obtener_materia(subject_id: str):
    # Verificar que el usuario es un profesor
    
    subject = get_subject_by_id(subject_id)
    if not subject:
        raise HTTPException(status_code=404, detail="Subject not found")
    
    return convert_objectid_to_str(subject)


# Crear materia (solo para profesores)
@app.post("/subjects/")
async def crear_materia(subject: SubjectCreate, user: UserInDB = Depends(get_current_user)):
    # Verificar que el usuario sea profesor
    if not user.is_teacher:
        raise HTTPException(status_code=403, detail="Only professors can create subjects")

    create_subject(subject)
    return {"message": "Subject created successfully"}

@app.put("/subjects/{subject_id}", response_model=SubjectInDB)
async def actualizar_materia(subject_id: str, subject: SubjectCreate, user: UserInDB = Depends(get_current_user)):
    # Verificar que el usuario sea profesor
    if not user.is_teacher:
        raise HTTPException(status_code=403, detail="Only professors can update subjects")

    # Buscar la materia por ID
    existing_subject = db.subjects.find_one({"_id": ObjectId(subject_id)})
    if not existing_subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    # Actualizar los campos de la materia (name y description)
    updated_subject = {
        "name": subject.name,
        "description": subject.description
    }

    # Actualizar la materia en la base de datos
    db.subjects.update_one({"_id": ObjectId(subject_id)}, {"$set": updated_subject})

    # Obtener la materia actualizada desde la base de datos
    updated_subject = db.subjects.find_one({"_id": ObjectId(subject_id)})

    # Convertir el ObjectId a string
    return convert_objectid_to_str(updated_subject)


@app.delete("/subjects/{subject_id}")
async def eliminar_materia(subject_id: str, user: UserInDB = Depends(get_current_user)):
    # Verificar que el usuario sea profesor
    if not user.is_teacher:
        raise HTTPException(status_code=403, detail="Only professors can delete subjects")

    # Buscar la materia por ID
    existing_subject = db.subjects.find_one({"_id": ObjectId(subject_id)})
    if not existing_subject:
        raise HTTPException(status_code=404, detail="Subject not found")

    # Eliminar la materia de la base de datos
    db.subjects.delete_one({"_id": ObjectId(subject_id)})

    return {"message": f"Subject with ID {subject_id} deleted successfully"}



#---------------------------------------------------------------------------------------------------------------------------------------
# Profesores

@app.get("/professors/")
async def obtener_docentes():
    professors = db.professors.find()
    return convert_objectid_to_str(list(professors))


@app.get("/professors/{professor_id}")
async def obtener_docente(professor_id: str):
    professor = get_professor_by_id(professor_id)
    if not professor:
        raise HTTPException(status_code=404, detail="Professor not found")
    
    return convert_objectid_to_str(professor)


@app.post("/professors/")
async def crear_docente(professor: ProfesorCreate, user: UserInDB = Depends(get_current_user)):
    # Verificar que el usuario es un profesor
    if not user.is_teacher:
        raise HTTPException(status_code=403, detail="Only professors can create professors")

    create_professor(professor)
    return {"message": "Professor created successfully"}


@app.put("/professors/{professor_id}")
async def actualizar_docente(professor_id: str, professor_update: ProfesorCreate, user: UserInDB = Depends(get_current_user)):
    # Verificar que el usuario es un profesor
    if not user.is_teacher:
        raise HTTPException(status_code=403, detail="Only professors can update professors")

    updated = update_professor(professor_id, professor_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Professor not found or update failed")
    
    return {"message": "Professor updated successfully"}

@app.delete("/professors/{professor_id}")
async def eliminar_docente(professor_id: str, user: UserInDB = Depends(get_current_user)):
    # Verificar que el usuario es un profesor
    if not user.is_teacher:
        raise HTTPException(status_code=403, detail="Only professors can delete professors")

    deleted = delete_professor(professor_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Professor not found")
    
    return {"message": "Professor deleted successfully"}


#---------------------------------------------------------------------------------------------------------------------------------------
# Alumnos

@app.get("/students/")
async def obtener_estudiantes():
    students = get_all_students()
    return students


@app.get("/students/{student_id}")
async def obtener_estudiante(student_id: str):
    # Verificar que el usuario tiene permisos para ver la información del alumno
    
    student = get_student_by_id(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    return convert_objectid_to_str(student)


@app.post("/students/")
async def crear_estudiente(student: AlumnoCreate, user: UserInDB = Depends(get_current_user)):
    # Verificar que el usuario es un profesor, porque solo los profesores pueden crear alumnos
    if not user.is_teacher:
        raise HTTPException(status_code=403, detail="Only professors can create students")

    create_student(student)
    return {"message": "Student created successfully"}


@app.put("/students/{student_id}")
async def actualizar_estudiente(student_id: str, student_update: AlumnoCreate, user: UserInDB = Depends(get_current_user)):
    # Verificar que el usuario es un profesor
    if user.is_teacher:
        raise HTTPException(status_code=403, detail="Only students can update students")

    updated = update_student(student_id, student_update)
    if not updated:
        raise HTTPException(status_code=404, detail="Student not found or update failed")

    return {"message": "Student updated successfully"}


@app.delete("/students/{student_id}")
async def eliminar_estudiente(student_id: str, user: UserInDB = Depends(get_current_user)):
    # Verificar que el usuario es un profesor
    if not user.is_teacher:
        raise HTTPException(status_code=403, detail="Only professors can delete students")

    deleted = delete_student(student_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Student not found")

    return {"message": "Student deleted successfully"}

