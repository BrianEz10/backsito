from sqlmodel import Session, select
from app.core.security import hash_password
from app.modules.usuarios.models import Usuario
from app.modules.estado_pedido.models import EstadoPedido
from app.modules.forma_pago.models import FormaPago
from app.modules.roles.associations import UsuarioRol
from app.modules.roles.models import Rol
from app.modules.unidad_medida.models import UnidadMedida

#Estados predefinidos de Roles

ROLES_SEED = [
    Rol(codigo="ADMIN", nombre="Administrador", descripcion="Acceso total sin reestricciones"),
    Rol(codigo="STOCK", nombre="Stock", descripcion="Actualiza stock y disponible"),
    Rol(codigo="PEDIDOS", nombre="Pedidos", descripcion="Avanza estados de CONFIRMADO a ENTREGADO"),
    Rol(codigo="CAJERO", nombre="Cajero", descripcion="Crea pedidos desde el punto de venta"),
    Rol(codigo="CLIENT", nombre="Cliente", descripcion="Opera solo sus propios datos")
]

def seed_roles(session: Session):
    for rol in ROLES_SEED:
        existing = session.get(Rol, rol.codigo)
        if not existing:
            session.add(rol)
    session.commit()

#Estados predefinidos de UnidadMedida

UNIDADES_MEDIDA_SEED = [
    UnidadMedida(nombre="kilogramo", simbolo="kg", tipo="peso"),
    UnidadMedida(nombre="gramo", simbolo="g", tipo="peso"),
    UnidadMedida(nombre="litro", simbolo="L", tipo="volumen"),
    UnidadMedida(nombre="mililitro", simbolo="mL", tipo="volumen"),
    UnidadMedida(nombre="unidad", simbolo="ud", tipo="contable"),
    UnidadMedida(nombre="porción", simbolo="porciones", tipo="contable"),
]

def seed_unidades_medida(session: Session):
    for um in UNIDADES_MEDIDA_SEED:
        existing = session.exec(
            select(UnidadMedida).where(UnidadMedida.simbolo == um.simbolo)
        ).first()
        if not existing:
            session.add(um)
    session.commit()

#Creacion de cuenta admin automatica

ADMIN_SEED = {
    "email": "admin@foodstore.com",
    "nombre": "Admin",
    "apellido": "FoodStore",
    "password": "Admin1234!",
}

def seed_admin_test(session: Session):
    existing = session.exec(
        select(Usuario).where(Usuario.email == ADMIN_SEED["email"])
    ).first()
    if existing:
        return
    admin = Usuario(
        email=ADMIN_SEED["email"],
        nombre=ADMIN_SEED["nombre"],
        apellido=ADMIN_SEED["apellido"],
        hashed_password=hash_password(ADMIN_SEED["password"]),
    )
    session.add(admin)
    session.flush()
    session.add(UsuarioRol(usuario_id=admin.id, rol_codigo="ADMIN"))
    session.commit()
    print(f"Admin creado: {ADMIN_SEED['email']} / {ADMIN_SEED['password']}")

#Estados predefinidos de EstadoPedido

ESTADOS_PEDIDO_SEED = [
    EstadoPedido(codigo="PENDIENTE", descripcion="Pedido creado, pago pendiente", orden=1, es_terminal=False),
    EstadoPedido(codigo="CONFIRMADO", descripcion="Pago procesado y confirmado", orden=2, es_terminal=False),
    EstadoPedido(codigo="EN_PREP", descripcion="En preparación en cocina", orden=3, es_terminal=False),
    EstadoPedido(codigo="ENTREGADO", descripcion="Entrega confirmada", orden=4, es_terminal=True),
    EstadoPedido(codigo="CANCELADO", descripcion="Pedido cancelado", orden=5, es_terminal=True),
]

def seed_estados_pedido(session: Session):
    for estado in ESTADOS_PEDIDO_SEED:
        existing = session.get(EstadoPedido, estado.codigo)
        if not existing:
            session.add(estado)
    session.commit()

#Estados predefinidos de FormaPago

FORMAS_PAGO_SEED = [
    FormaPago(codigo="EFECTIVO", descripcion="Pago en efectivo", habilitado=True),
    FormaPago(codigo="MERCADOPAGO", descripcion="Pago con Mercado Pago (tarjeta/QR)", habilitado=True),
    FormaPago(codigo="TRANSFERENCIA", descripcion="Transferencia bancaria", habilitado=True),
]

def seed_formas_pago(session: Session):
    for fp in FORMAS_PAGO_SEED:
        existing = session.get(FormaPago, fp.codigo)
        if not existing:
            session.add(fp)
    session.commit()