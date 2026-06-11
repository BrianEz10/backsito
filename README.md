## Setup

```bash
# 1. Clonamos el repo
git clone "repo-url"
cd backend

# 2. Entorno virtual
python -m venv venv

# Linux/macOS
source venv/bin/activate  

# Windows
venv\Scripts\activate   

# 3. Dependencias
pip install -r requirements.txt

# 4. Variables de entorno
cp .env.example .env
# Editar .env con sus credenciales

.env.example
DATABASE_URL=postgresql+psycopg://usuario:password@localhost:5432/food_store
SECRET_KEY=changeme
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

Base de datos

# Opción 1: la creamos con createdb
createdb food_store

# Opción 2: la creamos con psql
psql -U postgres -c "CREATE DATABASE food_store;"

Ejecutar

uvicorn main:app --reload

La API queda en http://localhost:8000. Documentación interactiva en http://localhost:8000/docs.

Seed

Al iniciar el servidor se crean automáticamente:

- Roles: ADMIN, STOCK, PEDIDOS, CLIENT
- Admin de prueba: admin@test.com / Admin1234!
- Unidades de medida: kg, g, L, mL, u, doc, m²
- Estados de pedido: PENDIENTE, CONFIRMADO, EN_PREP, EN_CAMINO, ENTREGADO, CANCELADO
- Formas de pago: EFECTIVO, MERCADOPAGO, TRANSFERENCIA

Estructura
backend/
├── app/
│   ├── core/         → Config, DB, seguridad, repo base, UOW
│   ├── modules/
│   │   ├── auth/
│   │   ├── categorias/
│   │   ├── direcciones/
│   │   ├── estado_pedido/
│   │   ├── forma_pago/
│   │   ├── ingredientes/
│   │   ├── pedidos/
│   │   ├── productos/
│   │   ├── roles/
│   │   └── unidad_medida/
│   └── db/           → Seeds
├── main.py
└── requirements.txt