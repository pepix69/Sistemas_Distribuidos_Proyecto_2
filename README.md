# Sistema de Gestión Escolar

## Descripción

Este sistema permite gestionar la información de estudiantes, profesores y materias en una institución educativa mediante una API RESTful desarrollada con FastAPI. Los datos se almacenan en una base de datos MongoDB y se maneja un sistema de identificadores únicos autogenerados para cada registro. Además, el sistema incluye operaciones CRUD (Crear, Leer, Actualizar y Eliminar) para las entidades principales.

## Objetivo

El objetivo principal de este sistema es ofrecer una solución eficiente y flexible para administrar información escolar, asegurando la integridad de los datos y facilitando la interoperabilidad mediante una API bien documentada y segura.

## Características Principales

### Alumnos
- *CRUD Completo*: Crear, leer, actualizar y eliminar registros de alumnos.
- *Datos del Alumno*:
  - ID único autogenerado.
  - Nombre y apellido.
  - Fecha de nacimiento.
  - Dirección.
  - Foto (URL de almacenamiento externo).

### Profesores
- *CRUD Completo*: Crear, leer, actualizar y eliminar registros de profesores.
- *Datos del Profesor*:
  - ID único autogenerado.
  - Nombre y apellido.
  - Fecha de nacimiento.
  - Dirección.
  - Especialidad.

### Materias
- *CRUD Completo*: Crear, leer, actualizar y eliminar materias.
- *Datos de la Materia*:
  - ID único autogenerado.
  - Nombre.
  - Descripción.

## Endpoints Implementados

### Alumnos
- GET /alumnos/: Obtener todos los alumnos.
- GET /alumnos/{alumno_id}: Obtener un alumno por su ID.
- POST /alumnos/: Crear un nuevo alumno.
- PUT /alumnos/{alumno_id}: Actualizar la información de un alumno existente.
- DELETE /alumnos/{alumno_id}: Eliminar un alumno.

### Profesores
- GET /profesores/: Obtener todos los profesores.
- GET /profesores/{profesor_id}: Obtener un profesor por su ID.
- POST /profesores/: Crear un nuevo profesor.
- PUT /profesores/{profesor_id}: Actualizar la información de un profesor existente.
- DELETE /profesores/{profesor_id}: Eliminar un profesor.

### Materias
- GET /materias/: Obtener todas las materias.
- GET /materias/{materia_id}: Obtener una materia por su ID.
- POST /materias/: Crear una nueva materia.
- PUT /materias/{materia_id}: Actualizar la información de una materia existente.
- DELETE /materias/{materia_id}: Eliminar una materia.

## Arquitectura del Proyecto

- *FastAPI*: Framework utilizado para crear la API RESTful.
- *MongoDB*: Base de datos NoSQL para almacenar información de alumnos, profesores y materias.
- *Pydantic*: Validación de datos y creación de modelos.
- *Motor*: Cliente asíncrono para la interacción con MongoDB.

## Configuración de la Base de Datos

1. El sistema utiliza una base de datos llamada proyecto_II.
2. Las colecciones principales son:
   - alumnos
   - profesores
   - materias
   - contadores: Utilizada para gestionar los IDs autogenerados de cada colección.
3. La inicialización de la base de datos incluye la creación de los contadores si no existen.

## Requisitos del Sistema

- Python 3.9 o superior.
- MongoDB en ejecución.
- Paquetes requeridos:
  - fastapi
  - motor
  - pydantic
  - bson

## Pasos para Ejecutar

1. Configura la conexión a MongoDB en la variable MONGO_URI.
2. Instala los paquetes requeridos usando pip install fastapi motor pydantic.
3. Inicia el servidor FastAPI con el comando:
   bash
   uvicorn main:app --reload
   
4. Accede a la documentación interactiva de la API en http://127.0.0.1:8000/docs.

## Integrantes del Equipo

- Giovanna Inosuli Campos Flores
- José Ángel Montoya Zúñiga
- Yavé Emmanuel Vargas Márquez
- Rodrigo Olmos Gómez
- Martha Dalila Cardona Serna
- José Refugio Salinas Uribe
