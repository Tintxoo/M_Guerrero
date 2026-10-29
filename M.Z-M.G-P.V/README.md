# Sistema de Gestión EcoTechSolutions

Aplicación de consola en Python para administrar departamentos, empleados,
proyectos y registros de tiempo. Incluye registro e inicio de sesión de usuarios
y persistencia en SQLite o MySQL.

## Requisitos

- Python 3.10 o superior.
- Windows PowerShell (los comandos siguientes se ejecutan desde la carpeta raíz
  del proyecto).

## Instalación y ejecución en Windows

1. Crea y activa un entorno virtual:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   Si PowerShell bloquea la activación del entorno, puedes ejecutar los comandos
   siguientes usando directamente `.\.venv\Scripts\python.exe`.

2. Instala las dependencias:

   ```powershell
   python -m pip install -r requirements.txt
   ```

3. Inicia el programa:

   ```powershell
   python src\main.py
   ```

La primera ejecución crea las tablas de SQLite en `data/ecotech.db` y carga
datos iniciales de demostración. SQLite es
la configuración predeterminada; no necesitas crear un archivo `.env` para
ejecutar localmente.

## Acceso inicial

Al iniciar, el programa muestra el menú de acceso para iniciar sesión o salir.
La precarga inicial crea cuentas de demostración. El nombre de cada cuenta es
la parte del correo del empleado anterior a `@` (por ejemplo, `ana.torres`); la
contraseña inicial compartida para esos datos de prueba es `empleado123`. Usa
estas credenciales solo para desarrollo y demostración, no en un entorno real.

Al iniciar sesión, se abre el menú que corresponde al rol de la cuenta. La
contraseña se solicita de forma oculta y no se muestra en la consola mientras
la escribes. El administrador puede registrar cuentas para empleados
existentes; sus nombres de usuario deben tener entre 3 y 40 caracteres y sus
contraseñas, al menos 6.

Las contraseñas nuevas se guardan usando PBKDF2-HMAC-SHA256 con una sal aleatoria
por cuenta y 600.000 iteraciones; no se almacenan en texto plano. Los hashes
SHA-256 heredados se actualizan automáticamente cuando el usuario inicia sesión
correctamente.

La precarga asigna el rol **administrador** a `ana.torres`; las demás cuentas
quedan con el rol **empleado**. Todas las cuentas de demostración usan
inicialmente la contraseña `empleado123`.
Al iniciar, una base de datos existente se migra automáticamente para añadir
el rol a las cuentas actuales y asignar a `ana.torres` como administradora.

El administrador conserva los menús de gestión de departamentos, empleados,
proyectos y registros de tiempo, y puede registrar cuentas de empleados. Los
empleados solo pueden consultar su propia ficha y registros de tiempo, y
modificar su nombre y correo. El acceso a los registros propios se filtra por
el ID del empleado asociado a la sesión; desde el menú de empleado no se
ofrecen funciones de administración, ni se puede cambiar el rol, el ID o las
relaciones laborales.

## Datos de demostración opcionales

Para cargar un departamento, dos empleados, proyectos y registros de tiempo
adicionales, ejecuta desde la raíz:

```powershell
python scripts\cargar_ejemplos.py
```

La carga es repetible y evita duplicar esos registros. Luego puedes iniciar el
programa con `python src\main.py`.

## Configuración de MySQL

SQLite se utiliza por defecto. Para MySQL, configura las variables de conexión
en un archivo local `.env` y selecciona `DB_ENGINE=mysql`. Puedes basarte en
`.env_example` si está disponible en la copia del proyecto. No compartas ni
subas `.env` o credenciales reales; utiliza un usuario de base de datos con los
permisos mínimos necesarios. Para SQLite, `DB_NAME` puede ser una ruta
absoluta o una ruta relativa a la raíz del proyecto.

## Estructura del proyecto

- `src/dominio`: entidades y relaciones del modelo.
- `src/persistencia`: conexión, creación de tablas y DAO con operaciones CRUD
  parametrizadas.
- `src/presentacion`: menús de acceso y gestión, además de validación de
  entradas.
- `src/servicios`: validación de entradas, hashing de contraseñas y autorización
  centralizada por rol.
- `src/main.py`: inicialización de la base de datos y arranque de la aplicación.
- `scripts`: utilidades independientes y carga opcional de datos de ejemplo.
- `tests`: pruebas automatizadas.

Los formularios validan, entre otros datos, fechas `AAAA-MM-DD`, IDs enteros
positivos, correos, teléfonos, salarios y horas registradas.

## Ejecutar las pruebas

Desde la raíz del proyecto:

```powershell
python -m unittest discover -s tests -v
```
