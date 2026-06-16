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

## 3. Creamos nuestras variables de entorno.

    cp .env.example .env

## 4.1 Configuramos ngrok (necesario para Mercado Pago).

    Descargamos ngrok desde la web oficial "https://ngrok.com"

## 4.2 Levantar ngrok.

    Abrimos una terminal y ejecutamos "ngrok http 8000"

## 4.3 Recogemos la URL.

    Copiamos la URL que nos da es similiar a esta "https://abc123.ngrok-free.dev"

## 4.4 Aplicar URL.

    Abrimos nuestro archivo ".env" y en la parte de "MP_NOTIFICATION_URL=(Aca va nuestra URL)/api/v1/pagos/webhook" entre el parentesis pegar la URL
    borrar el parentesis luego tiene que quedar asi "MP_NOTIFICATION_URL=https://abc123.ngrok-free.dev/api/v1/pagos/webhook"

## 4.5 Aplicar el webhook en Mercado Pago

    1- Inicia sesion en https://www.mercadopago.com.ar/developers
    2- Ingresar a "Tu integración"--> "Webhooks"
    3- Seleccionamos en "Crear un WebHook" 
    4- Agregá la misma URL de ngrok + /api/v1/pagos/webhook este es un ejemplo de como deberia de quedar (https://abc123.ngrok-free.dev/api/v1/pagos/webhook)
    5- Y luego seleccionamos opciones en "Eventos recomendados para integraciones con Checkout PRO"
        -Pagos
        -Órdenes comerciales
    6- Guardamos los cambios

## 5. Adjuntar las crendeciales de Prueba de Mercado Pago

    1- Inicia sesion en https://www.mercadopago.com.ar/developers
    2- Ingresar a "Tu integración"--> "Crendenciales de prueba"
    3- Ahora tenemos nuestras 2 credenciales "Public Key" y el "Access Token"
    4- Luego nos dirigimos a nuestro archivo creado ".env" y pegamos alli las credenciales en su lugar correspondiente.
    5- Guardamos los cambios


## 6. Abrimos una terminal para levantar el proyecto con Docker.

    docker compose up --build

## 7. Ingresamos al swagger para ver los endpoints.

    http://localhost:8000/docs


# Generacion del Seed

## Al iniciar el servidor se crean automaticamente:

    - **Roles**: ADMIN, STOCK, CAJERO, PEDIDOS, CLIENT
    - **Estado de pedido**: PENDIENTE, CONFIRMADO, EN_PREP, ENTREGADO, CANCELADO
    - **Formas de pago**: MERCADO_PAGO, EFECTIVO, TRANSFERENCIA
    - **Unidades de medida**: kg, g, mL, ud, porciones
    - **Usuario del admin**: El email es "admin@foodstore.com" y la contraseña es "Admin1234!"