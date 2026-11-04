import random
from datetime import date

from dominio.departamento import Departamento
from dominio.empleado import Empleado
from dominio.proyecto import Proyecto
from dominio.registro_tiempo import RegistroTiempo
from dominio.usuario import Usuario
from persistencia.departamento_dao import DepartamentoDAO
from persistencia.empleado_dao import EmpleadoDAO
from persistencia.proyecto_dao import ProyectoDAO
from persistencia.registro_tiempo_dao import RegistroTiempoDAO
from persistencia.usuario_dao import UsuarioDAO
from servicios.seguridad import hash_password


def cargar_departamentos():
    # 5 departamentos de ejemplo
    nombres_departamentos = [
        "Tecnología",
        "Recursos Humanos",
        "Ventas",
        "Finanzas",
        "Marketing"
    ]

    # Cargamos los existentes en memoria para evitar consultas repetitivas
    existentes = {d.nombre: d for d in DepartamentoDAO.listar()}
    departamentos_creados = []

    for nombre in nombres_departamentos:
        if nombre in existentes:
            print(f"Departamento ya existe: {nombre}")
            departamentos_creados.append(existentes[nombre])
            continue

        nuevo_depto = Departamento(nombre=nombre, id=None, gerente_id=None)
        DepartamentoDAO.insertar(nuevo_depto)
        print(f"Departamento creado: {nombre}")
        departamentos_creados.append(nuevo_depto)

    return departamentos_creados

def cargar_empleados(departamentos):
    # Validamos tener departamentos para asignar
    if not departamentos:
        print("No hay departamentos para asignar a los empleados.")
        return

    # 20 empleados de ejemplo con todos los datos necesarios
    datos_empleados = [
        ("Ana Torres", "Calle 1 #123", "555-0101", "ana.torres@empresa.com", date(2022, 1, 15), 3500.0),
        ("Carlos Ruiz", "Avenida 2 #456", "555-0102", "carlos.ruiz@empresa.com", date(2022, 2, 20), 3200.0),
        ("Elena Gómez", "Pasaje 3 #789", "555-0103", "elena.gomez@empresa.com", date(2021, 5, 10), 4000.0),
        ("Luis Silva", "Calle 4 #101", "555-0104", "luis.silva@empresa.com", date(2023, 3, 5), 2800.0),
        ("María Paz", "Avenida 5 #202", "555-0105", "maria.paz@empresa.com", date(2020, 11, 11), 4500.0),
        ("Jorge Vega", "Plaza 6 #303", "555-0106", "jorge.vega@empresa.com", date(2021, 7, 22), 3100.0),
        ("Sofía Castro", "Calle 7 #404", "555-0107", "sofia.castro@empresa.com", date(2022, 8, 30), 3300.0),
        ("Diego Luna", "Avenida 8 #505", "555-0108", "diego.luna@empresa.com", date(2023, 1, 10), 2900.0),
        ("Laura Soto", "Pasaje 9 #606", "555-0109", "laura.soto@empresa.com", date(2020, 2, 14), 4200.0),
        ("Pedro Mora", "Calle 10 #707", "555-0110", "pedro.mora@empresa.com", date(2021, 9, 18), 3400.0),
        ("Carmen Díaz", "Avenida 11 #808", "555-0111", "carmen.diaz@empresa.com", date(2022, 10, 5), 3600.0),
        ("Raúl Reyes", "Plaza 12 #909", "555-0112", "raul.reyes@empresa.com", date(2023, 4, 12), 3000.0),
        ("Isabel Ríos", "Calle 13 #111", "555-0113", "isabel.rios@empresa.com", date(2021, 12, 1), 3800.0),
        ("Andrés Cruz", "Avenida 14 #222", "555-0114", "andres.cruz@empresa.com", date(2020, 6, 25), 4100.0),
        ("Paula León", "Pasaje 15 #333", "555-0115", "paula.leon@empresa.com", date(2022, 3, 8), 3250.0),
        ("Javier Gil", "Calle 16 #444", "555-0116", "javier.gil@empresa.com", date(2023, 5, 20), 2750.0),
        ("Rosa Ortiz", "Avenida 17 #555", "555-0117", "rosa.ortiz@empresa.com", date(2021, 8, 15), 3700.0),
        ("Miguel Peña", "Plaza 18 #666", "555-0118", "miguel.pena@empresa.com", date(2022, 11, 28), 3450.0),
        ("Lucía Vera", "Calle 19 #777", "555-0119", "lucia.vera@empresa.com", date(2020, 4, 30), 4300.0),
        ("Tomás Roa", "Avenida 20 #888", "555-0120", "tomas.roa@empresa.com", date(2023, 2, 18), 2950.0)
    ]

    # Obtenemos los empleados actuales para evitar duplicidad de correos
    empleados_existentes = {e.email: e for e in EmpleadoDAO.listar()}

    for i, (nombre, dir, tel, email, fecha, salario) in enumerate(datos_empleados):
        if email in empleados_existentes:
            print(f"Empleado ya existe: {email}")
            continue

        # Distribuir uniformemente a los empleados entre los 5 departamentos
        depto_asignado = departamentos[i % len(departamentos)]

        nuevo_empleado = Empleado(
            id=None,
            nombre=nombre,
            direccion=dir,
            telefono=tel,
            email=email,
            fechaInicioContrato=fecha,
            salario=salario,
            departamento_id=depto_asignado.id
        )

        EmpleadoDAO.insertar(nuevo_empleado)
        print(f"Empleado creado: {email} en {depto_asignado.nombre}")

def cargar_usuarios():
    password_default = "empleado123"

    for empleado in EmpleadoDAO.listar():
        if UsuarioDAO.buscar_por_empleado(empleado.id) is not None:
            print(f"Usuario ya existe para el empleado: {empleado.email}")
            continue

        nombre_usuario = empleado.email.split("@", 1)[0].lower()
        nombre_usuario = Usuario.normalizar_usuario(nombre_usuario)

        usuario = Usuario(
            nombre_usuario=nombre_usuario,
            password_hash=hash_password(password_default),
            empleado_id=empleado.id,
            rol=(
                Usuario.ROL_ADMINISTRADOR
                if nombre_usuario == "ana.torres"
                else Usuario.ROL_EMPLEADO
            ),
        )
        UsuarioDAO.insertar(usuario)
        print(f"Usuario creado: {usuario.nombre_usuario} | rol: {usuario.rol}")


def cargar_proyectos_por_departamento(
    departamentos: list[Departamento],
) -> dict[int, Proyecto]:
    proyectos_existentes = {
        proyecto.nombre: proyecto for proyecto in ProyectoDAO.listar()
    }
    proyectos_por_departamento = {}

    for departamento in departamentos:
        nombre = f"Proyecto - {departamento.nombre}"[:100]
        proyecto = proyectos_existentes.get(nombre)
        if proyecto is None:
            proyecto = ProyectoDAO.insertar(
                Proyecto(
                    nombre,
                    f"Proyecto asignado al departamento {departamento.nombre}.",
                    date.today(),
                )
            )
            proyectos_existentes[nombre] = proyecto
        proyectos_por_departamento[departamento.id] = proyecto

    return proyectos_por_departamento


def asignar_proyectos_iniciales(
    empleados: list[Empleado],
    proyectos: list[Proyecto],
) -> None:
    if not proyectos:
        return

    usuarios = {usuario.empleado_id: usuario for usuario in UsuarioDAO.listar()}
    empleados_no_administradores = [
        empleado
        for empleado in empleados
        if (
            empleado.id not in usuarios
            or usuarios[empleado.id].rol != Usuario.ROL_ADMINISTRADOR
        )
    ]

    for empleado in empleados_no_administradores[:10]:
        if not ProyectoDAO.listarPorEmpleado(empleado.id):
            ProyectoDAO.asignarEmpleado(
                random.choice(proyectos).id,
                empleado.id,
            )


def cargar_registro_inicial_por_empleado(
    empleados: list[Empleado],
    proyectos_por_departamento: dict[int, Proyecto],
    proyectos: list[Proyecto],
) -> None:
    if not proyectos:
        return

    empleados_con_registros = {
        registro.empleado_id for registro in RegistroTiempoDAO.listar()
    }
    for empleado in empleados:
        if empleado.id in empleados_con_registros:
            continue

        proyectos_asignados = ProyectoDAO.listarPorEmpleado(empleado.id)
        if proyectos_asignados:
            proyecto = random.choice(proyectos_asignados)
        else:
            proyecto = proyectos_por_departamento.get(empleado.departamento_id)
            if proyecto is None:
                proyecto = random.choice(proyectos)

        RegistroTiempoDAO.insertar(
            RegistroTiempo(
                fecha=date.today(),
                horas=1,
                descripcion=f"Registro inicial de {empleado.nombre}.",
                empleado_id=empleado.id,
                proyecto_id=proyecto.id,
            )
        )
        empleados_con_registros.add(empleado.id)


def inicializar_base_datos():
    print("--- Iniciando precarga de datos ---")
    departamentos = cargar_departamentos()
    cargar_empleados(departamentos)
    cargar_usuarios()
    empleados = EmpleadoDAO.listar()
    proyectos_por_departamento = cargar_proyectos_por_departamento(
        DepartamentoDAO.listar()
    )
    proyectos = list(proyectos_por_departamento.values())
    asignar_proyectos_iniciales(empleados, proyectos)
    cargar_registro_inicial_por_empleado(
        empleados,
        proyectos_por_departamento,
        proyectos,
    )
    print("--- Precarga finalizada ---")
