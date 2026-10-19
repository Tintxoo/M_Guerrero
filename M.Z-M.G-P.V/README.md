# Sistema de Gestión EcoTechSolutions

Aplicación de consola en Python para administrar departamentos, empleados,
proyectos y registros de tiempo. La implementación está organizada en capas:

- `src/dominio`: clases y relaciones del diagrama UML.
- `src/persistencia`: conexión, creación de tablas y objetos DAO con operaciones
  CRUD parametrizadas.
- `src/presentacion`: menús y validación de entradas.
- `src/main.py`: inicialización de la base de datos y coordinación de los menús.

## Ejecución local con SQLite

Se requiere Python 3.10 o superior.

```powershell
python -m pip install -r requirement.txt
python src/main.py
```

SQLite se utiliza por defecto y crea `src/persistencia/ecotech.db`. Para cambiar
la configuración, copia `.env_example` a `.env`. No subas `.env` ni credenciales
reales al repositorio.

Para cargar dos empleados y datos relacionados de demostración (departamento,
gerente, proyectos y horas) ejecuta:

```powershell
python src/cargar_ejemplos.py
```

La carga es repetible y no duplica los ejemplos si vuelves a ejecutarla.
Después inicia la aplicación normalmente con `python src/main.py`.

## Uso de MySQL

Configura en `.env` `DB_ENGINE=mysql`, el host, puerto, nombre de base de datos,
usuario y contraseña. El usuario de la aplicación debe tener permisos limitados
a las operaciones requeridas; la contraseña se lee desde el entorno y no se
incluye en el código. La aplicación informa las variables obligatorias que
falten y no intenta conectarse con credenciales predeterminadas.

## Relaciones principales

- Un departamento contiene empleados y puede tener un empleado gerente.
- Un empleado puede pertenecer a un departamento y registrar varios tiempos.
- Cada registro de tiempo corresponde a un empleado y a un proyecto.
- Un proyecto agrupa sus registros; `calcularHorasTotales()` suma las horas
  recuperadas desde la base de datos.

Los DAO usan consultas parametrizadas, cierran las conexiones incluso cuando
ocurre un error y revierten la transacción antes de propagar la excepción. Los
formularios validan los datos y vuelven a solicitar las entradas que no cumplen
el formato esperado: fechas `AAAA-MM-DD`, horas y montos con hasta dos decimales
(punto o coma), IDs enteros positivos, correos y teléfonos válidos. El salario
puede ser cero y las horas registradas deben ser mayores que cero. La consola se
limpia entre operaciones y espera confirmación para que se alcance a leer el
resultado.

## Validación

Ejecuta las pruebas automatizadas desde la raíz del repositorio:

```powershell
python -m unittest discover -s tests -v
```

La revisión técnica final y la explicación de los aportes individuales y del uso
de herramientas de IA deben ser realizadas y justificadas por el equipo.
