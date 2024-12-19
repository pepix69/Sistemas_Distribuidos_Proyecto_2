from db import db
from bson import ObjectId
from auth import hash_password
from schemas import *
from datetime import datetime, date
from jose import JWTError, jwt
import boto3
import os

# Configurar cliente de AWS S3
s3_client = boto3.client('s3')
BUCKET_NAME = "sistemas-ditribuidos-students-images-bucket"

def convert_objectid_to_str(data):
    if isinstance(data, ObjectId):
        return str(data)
    elif isinstance(data, dict):
        return {key: convert_objectid_to_str(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [convert_objectid_to_str(item) for item in data]
    return data

def convert_date_to_datetime(fecha_nacimiento):
    if isinstance(fecha_nacimiento, date):
        return datetime.combine(fecha_nacimiento, datetime.min.time())
    return fecha_nacimiento


# CRUD
def create_user(user: UserCreate):
    user_dict = user.model_dump()
    user_dict["hashed_password"] = hash_password(user.password)
    del user_dict["password"]  # Eliminar la contraseña en texto claro
    db.users.insert_one(user_dict)

def get_user_by_username(username: str):
    return db.users.find_one({"username": username})

def convert_date_to_string(date_obj):
    if isinstance(date_obj, date):
        return date_obj.isoformat()  # Convierte la fecha en formato 'YYYY-MM-DD'
    return date_obj

def serialize_dates(obj):
    if isinstance(obj, dict):
        # Recorrer el diccionario y convertir las fechas
        return {k: serialize_dates(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        # Recorrer la lista y convertir las fechas
        return [serialize_dates(i) for i in obj]
    else:
        # Si el objeto es una fecha, convertirla
        return convert_date_to_string(obj)


#-----------------------------------------------------------------------------------------------------------------------------------------------
# Funciones CRUD para profesores
# Crear un nuevo profesor
def create_professor(professor: ProfesorCreate):
    professor_dict = professor.model_dump()
    professor_dict = serialize_dates(professor_dict)
    db.professors.insert_one(professor_dict)


# Obtener un profesor por su ID
def get_professor_by_id(professor_id: str) -> Optional[ProfesorInDB]:
    professor = db.professors.find_one({"_id": ObjectId(professor_id)})
    if professor:
        return ProfesorInDB(**professor, id=professor_id)
    return None

# Obtener todos los profesores
def get_all_professors() -> list[ProfesorInDB]:
    professors = list(db.professors.find())
    return [ProfesorInDB(**professor, id=professor["_id"]) for professor in professors]

# Actualizar un profesor
def update_professor(professor_id: str, updated_data: ProfesorCreate):
    if hasattr(updated_data, 'dob'):
        updated_data.dob = convert_date_to_datetime(updated_data.dob)
    
    result = db.professors.update_one(
        {"_id": ObjectId(professor_id)}, 
        {"$set": updated_data.model_dump()}
    )
    return result.modified_count > 0

# Eliminar un profesor
def delete_professor(professor_id: str):
    result = db.professors.delete_one({"_id": ObjectId(professor_id)})
    return result.deleted_count > 0

#-----------------------------------------------------------------------------------------------------------------------------------------------
# Crud para estudiantes
# Crear un nuevo alumno
def create_student(student: AlumnoCreate):
    student_dict = student.model_dump()
    student_dict = serialize_dates(student_dict)
    
    # Manejo de la imagen
    student_dict["photo_url"] = upload_image_to_s3(student.photo_url)
    
    db.students.insert_one(student_dict)

# Obtener un alumno por su ID
def get_student_by_id(student_id: str) -> Optional[AlumnoInDB]:
    student = db.students.find_one({"_id": ObjectId(student_id)})
    if student:
        return AlumnoInDB(**student, id=student_id)
    return None

# Obtener todos los alumnos
def get_all_students() -> list[AlumnoInDB]:
    students = list(db.students.find())
    students = [convert_objectid_to_str(student) for student in students]
    return [AlumnoInDB(**student, id=student['_id']) for student in students]

# Actualizar un alumno
def update_student(student_id: str, updated_data: AlumnoCreate):
    updated_data = updated_data.model_dump()
    updated_data = serialize_dates(updated_data)
    
    # Manejo de la imagen
    updated_data["photo_url"] = upload_image_to_s3(updated_data.get("photo_url"))
    
    result = db.students.update_one(
        {"_id": ObjectId(student_id)}, 
        {"$set": updated_data}
    )
    return result.modified_count > 0

# Eliminar un alumno
def delete_student(student_id: str):
    result = db.students.delete_one({"_id": ObjectId(student_id)})
    return result.deleted_count > 0


#-----------------------------------------------------------------------------------------------------------------------------------------------

# Funciones CRUD para materias
# Crear una nueva materia
def create_subject(subject: SubjectCreate):
    subject_dict = subject.model_dump()
    db.subjects.insert_one(subject_dict)

# Obtener una materia por su ID
def get_subject_by_id(subject_id: str) -> Optional[SubjectInDB]:
    subject = db.subjects.find_one({"_id": ObjectId(subject_id)})
    if subject:
        return SubjectInDB(**subject, id=subject_id)
    return None


# Obtener todas las materias
def get_all_subjects() -> list[SubjectInDB]:
    subjects = list(db.subjects.find())
    return [SubjectInDB(**subject, id=subject['_id']) for subject in subjects]

# Actualizar una materia
def update_subject(subject_id: str, updated_data: SubjectCreate):
    result = db.subjects.update_one(
        {"_id": ObjectId(subject_id)}, 
        {"$set": updated_data.dict()}
    )
    return result.modified_count > 0

# Eliminar una materia
def delete_subject(subject_id: str):
    result = db.subjects.delete_one({"_id": ObjectId(subject_id)})
    return result.deleted_count > 0


def get_user_by_id(user_id: str):
    try:
        user_object_id = ObjectId(user_id)
    except Exception:
        return None
    return db.users.find_one({"_id": user_object_id})

def get_subjects_by_professor(professor_id: str):
    return list(db.subjects.find({"professor_id": professor_id}))

#-----------------------------------------------------------------------------------------------------------------------------------------------
# Funciones CRUD para inscripciones
def enroll_student(enrollment: EnrollmentCreate):
    enrollment_dict = enrollment.model_dump()
    db.enrollments.insert_one(enrollment_dict)

def get_enrollments_by_student(student_id: str):
    return list(db.enrollments.find({"student_id": student_id}))

def get_enrollments_by_subject(subject_id: str):
    return list(db.enrollments.find({"subject_id": subject_id}))

def assign_grade(enrollment_id: str, grade: float):
    enrollment_id = ObjectId(enrollment_id)
    db.enrollments.update_one({"_id": enrollment_id}, {"$set": {"grade": grade}})

#-----------------------------------------------------------------------------------------------------------------------------------------------
# AWS
def upload_image_to_s3(photo_url: Optional[str]) -> Optional[str]:
    if not photo_url or not os.path.exists(photo_url):
        return None  # Retorna None si la imagen no existe
    try:
        file_name = os.path.basename(photo_url)
        s3_client.upload_file(photo_url, BUCKET_NAME, file_name)
        return f"https://{BUCKET_NAME}.s3.amazonaws.com/{file_name}"
    except Exception as e:
        print(f"Error uploading to S3: {e}")
        return None
