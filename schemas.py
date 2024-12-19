from pydantic import BaseModel, field_validator
from typing import Optional
from bson import ObjectId
from datetime import date

class UserCreate(BaseModel):
    username: str
    password: str
    is_teacher: bool

    @field_validator('is_teacher')
    def validate_is_teacher(cls, v):
        if not isinstance(v, bool):
            raise ValueError('is_teacher must be a boolean')
        return v
    
    @field_validator('username')
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('Username must have at least 3 characters')
        return v
    
    
# Clase para el Alumno en la base de datos
class UserInDB(UserCreate):
    hashed_password: Optional[str]
    id: str  # ID único para el usuario

    class Config:
        # Convertir ObjectId a string automáticamente
        json_encoders = {
            ObjectId: str
        }

class AlumnoCreate(BaseModel):
    first_name: str  # Nombre
    last_name: str   # Apellido
    dob: date        # Fecha de nacimiento
    address: str     # Dirección
    photo_url: Optional[str] = None  # Foto del alumno (URL en AWS S3)

    @field_validator('dob')
    def validate_dob(cls, v):
        if v > date.today():
            raise ValueError('La fecha de nacimiento no puede ser en el futuro')
        return v

# Clase para el Alumno en la base de datos
class AlumnoInDB(AlumnoCreate):
    id: str  # ID único para el alumno
    class Config:
        # Convertir ObjectId a string automáticamente
        json_encoders = {
            ObjectId: str
        }



class ProfesorCreate(BaseModel):
    first_name: str  # Nombre
    last_name: str   # Apellido
    dob: date        # Fecha de nacimiento
    address: str     # Dirección
    specialty: str   # Especialidad del profesor

    @field_validator('dob')
    def validate_dob(cls, v):
        if v > date.today():
            raise ValueError('Date of birth cannot be in the future')
        return v

# Clase para el Profesor en la base de datos
class ProfesorInDB(ProfesorCreate):
    id: str # ID único para el profesor
    class Config:
        # Convertir ObjectId a string automáticamente
        json_encoders = {
            ObjectId: str
        }


class SubjectCreate(BaseModel):
    name: str
    description: str
    professor_id: str  # El ID del profesor que enseña la materia

class SubjectInDB(SubjectCreate):
    id: str  # ID generado por MongoDB
    class Config:
        json_encoders = {
            ObjectId: str
        }



class EnrollmentCreate(BaseModel):
    student_id: str  # El ID del alumno
    subject_id: str  # El ID de la materia
    grade: Optional[float] = None  # Calificación, si ya fue asignada

class EnrollmentInDB(EnrollmentCreate):
    id: str  # ID generado por MongoDB
    class Config:
        json_encoders = {
            ObjectId: str
        }