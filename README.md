# Tienda de comida Food Store - Backend API

Este es un sistema de pedidos de comida. El backend esta desarrollado con FastAPI, SQLModel y PostgreSQL.

# Nuestro Stack

**FastAPI**

**SQLModel**

**PostgreSQL**

**Mercado Pago**

**Cloudinary**

# Como instalarlo

## 1. Clonas el repo.
git clone https://github.com/BrianEz10/backsito.git

## 2. Entras a la carpeta del backend.

cd backsito

## 3. Generas el entorno virtual.

python -m venv venv

## 4. Activas el entorno virtual, dependiendo de tu sistema operativo.

- **Linux/macOS**: source venv/bin/activate 
- **Windows**: venv\Scripts\activate 

## 5. Instalamos las dependencias.

pip install -r requirements.txt

## 6. Creamos nuestras variables de entorno.

cp .env.example .env

## 7. Creamos la base de datos.

psql -U postgres -c "CREATE DATABASE food_store;"

## 8. Levantamos el proyecto.

uvicorn main:app --reload

## 9. Ingresamos al swagger para ver los endpoints

http://localhost:8000/docs


# Generacion del Seed

## Al iniciar el servidor se crean automaticamente:

- **Roles**: ADMIN, STOCK, PEDIDOS, CLIENT
- **Estado de pedido**: PENDIENTE, CONFIRMADO, EN_PREP, ENTREGADO, CANCELADO
- **Formas de pago**: MERCADO_PAGO, EFECTIVO, TRANSFERENCIA
- **Unidades de medida**: kg, g, mL, ud, porciones
- **Usuario del admin**: El email es "admin@foodstore.com" y la contraseña es "Admin1234!"