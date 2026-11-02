import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from dominio.departamento import Departamento
from dominio.empleado import Empleado
from dominio.proyecto import Proyecto
from dominio.registro_tiempo import RegistroTiempo
from persistencia.departamento_dao import DepartamentoDAO
from persistencia.empleado_dao import EmpleadoDAO
from persistencia.proyecto_dao import ProyectoDAO
from persistencia.registro_tiempo_dao import RegistroTiempoDAO


NOMBRE_DEPARTAMENTO = "Desarrollo (Demo)"
EMPLEADOS_EJEMPLO = (
    {
        "nombre": "Camila Rojas",
        "direccion": "Avenida Siempre Viva 123",
        "telefono": "+56912345678",
        "email": "camila.rojas.demo@example.com",
        "fecha": date(2025, 3, 10),
        "salario": 1_200_000,
    },
    {
        "nombre": "Diego Fuentes",
        "direccion": "Pasaje Los Robles 456",
        "telefono": "+56987654321",
        "email": "diego.fuentes.demo@example.com",
        "fecha": date(2025, 6, 2),
        "salario": 1_050_000,
    },
)
PROYECTOS_EJEMPLO = (
    {
        "nombre": "EcoTech - Plataforma",
        "descripcion": "Desarrollo de la plataforma interna EcoTech.",
        "fecha": date(2026, 1, 15),
    },
    {
        "nombre": "EcoTech - Reportes",
        "descripcion": "Creación de reportes y métricas del sistema.",
        "fecha": date(2026, 2, 1),
    },
)
REGISTROS_EJEMPLO = (
    {
        "empleado_email": "camila.rojas.demo@example.com",
        "proyecto_nombre": "EcoTech - Plataforma",
        "fecha": date(2026, 3, 2),
        "horas": 3.5,
        "descripcion": "Implementación de módulos de gestión.",
    },
    {
        "empleado_email": "diego.fuentes.demo@example.com",
        "proyecto_nombre": "EcoTech - Plataforma",
        "fecha": date(2026, 3, 3),
        "horas": 2.0,
        "descripcion": "Pruebas de integración de la plataforma.",
    },
    {
        "empleado_email": "camila.rojas.demo@example.com",
        "proyecto_nombre": "EcoTech - Reportes",
        "fecha": date(2026, 3, 4),
        "horas": 1.5,
        "descripcion": "Diseño de reportes de avance.",
    },
)


def cargar_datos_ejemplo() -> None:
    departamentos = DepartamentoDAO.listar()
    departamento = next(
        (dep for dep in departamentos if dep.nombre == NOMBRE_DEPARTAMENTO),
        None,
    )
    if departamento is None:
        departamento = DepartamentoDAO.insertar(Departamento(NOMBRE_DEPARTAMENTO))

    empleados_existentes = {
        empleado.email: empleado for empleado in EmpleadoDAO.listar()
    }
    empleados = {}
    for datos in EMPLEADOS_EJEMPLO:
        empleado = empleados_existentes.get(datos["email"])
        if empleado is None:
            empleado = EmpleadoDAO.insertar(
                Empleado(
                    datos["nombre"],
                    datos["direccion"],
                    datos["telefono"],
                    datos["email"],
                    datos["fecha"],
                    datos["salario"],
                    departamento.id,
                )
            )
        else:
            empleado.asignarDepartamento(departamento.id)
            EmpleadoDAO.actualizar(empleado)
        empleados[empleado.email] = empleado

    departamento = DepartamentoDAO.obtenerPorId(departamento.id)
    departamento.asignarGerente(empleados[EMPLEADOS_EJEMPLO[0]["email"]])
    DepartamentoDAO.actualizar(departamento)

    proyectos_existentes = {
        proyecto.nombre: proyecto for proyecto in ProyectoDAO.listar()
    }
    proyectos = {}
    for datos in PROYECTOS_EJEMPLO:
        proyecto = proyectos_existentes.get(datos["nombre"])
        if proyecto is None:
            proyecto = ProyectoDAO.insertar(
                Proyecto(datos["nombre"], datos["descripcion"], datos["fecha"])
            )
        proyectos[proyecto.nombre] = proyecto

    registros_existentes = {
        (
            registro.empleado_id,
            registro.proyecto_id,
            registro.descripcion,
        )
        for registro in RegistroTiempoDAO.listar()
    }
    for datos in REGISTROS_EJEMPLO:
        empleado = empleados[datos["empleado_email"]]
        proyecto = proyectos[datos["proyecto_nombre"]]
        clave = (empleado.id, proyecto.id, datos["descripcion"])
        if clave not in registros_existentes:
            RegistroTiempoDAO.insertar(
                RegistroTiempo(
                    fecha=datos["fecha"],
                    horas=datos["horas"],
                    descripcion=datos["descripcion"],
                    empleado_id=empleado.id,
                    proyecto_id=proyecto.id,
                    empleado=empleado,
                    proyecto=proyecto,
                )
            )
            registros_existentes.add(clave)

    print("Datos de ejemplo listos (la carga se puede ejecutar más de una vez).")
    print(f"Departamento: {departamento.nombre} (ID {departamento.id})")
    print(f"Gerente: {empleados[EMPLEADOS_EJEMPLO[0]['email']].nombre}")
    for empleado in empleados.values():
        print(
            f"Empleado: {empleado.nombre} | ID {empleado.id} "
            f"| {empleado.email} | Departamento {departamento.id}"
        )
    for proyecto in proyectos.values():
        proyecto_actualizado = ProyectoDAO.obtenerPorId(proyecto.id)
        print(
            f"Proyecto: {proyecto.nombre} | ID {proyecto.id} "
            f"| Horas registradas: {proyecto_actualizado.calcularHorasTotales():g}"
        )


if __name__ == "__main__":
    cargar_datos_ejemplo()
