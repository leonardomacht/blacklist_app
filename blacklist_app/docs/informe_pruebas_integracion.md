# Informe de pruebas de integración con Postman y Newman

## Repositorio del proyecto

https://github.com/leonardomacht/blacklist_app

## Objetivo

Este informe documenta el paso a paso que se siguió para crear una colección de
Postman con las capacidades del servicio `blacklist_app`, exportarla, probarla
localmente con Newman, y automatizar su ejecución dentro del pipeline de
integración continua en GitHub Actions.

## Paso 1: Creación de la colección en Postman

Se creó una colección llamada **Blacklist App** dentro de Postman, organizada en
tres carpetas según la funcionalidad que prueban.

**Salud del servicio**

Contiene una sola petición, `Ping`, que hace un GET a `/blacklists/ping` sin
necesidad de autenticación. Sirve para confirmar que el servicio está levantado
antes de correr el resto de las pruebas.

**Agregar a blacklist (POST)**

Contiene cinco peticiones que cubren tanto el caso exitoso como los casos de error:

- Agregar email, caso exitoso: envía email, app_uuid y blocked_reason. Debe
  responder 201.
- Agregar email sin motivo: confirma que blocked_reason es opcional. Debe
  responder 201.
- Agregar email sin autenticación: no envía el header Authorization. Debe
  responder 401.
- Agregar email con UUID inválido: envía un app_uuid con formato incorrecto.
  Debe responder 400.
- Agregar email duplicado: intenta agregar un email que ya fue agregado antes en
  la misma ejecución. Debe responder 409.

**Consultar blacklist (GET)**

Contiene tres peticiones:

- Consultar email que existe en la lista: debe responder 200 con
  is_blacklisted en true.
- Consultar email que no existe en la lista: debe responder 200 con
  is_blacklisted en false y blocked_reason nulo.
- Consultar email sin autenticación: debe responder 401.

Todas las peticiones usan variables de colección en lugar de valores fijos:
`base_url`, `token` y `email_prueba`. Esto permite reutilizar la misma colección
tanto en el ambiente local como en el pipeline de CI, sin tener que modificar cada
petición por separado.

## Paso 2: Exportación del archivo .json

Desde Postman, se exportó la colección usando la opción
Export. El archivo generado se guardó dentro del repositorio en la ruta:

```
blacklist_app/postman/blacklist_app.postman_collection.json
```

Este archivo quedó versionado junto con el resto del código, para que cualquier
persona del equipo o el pipeline de CI puedan usarlo sin depender de Postman
instalado localmente.

## Paso 3: Ejecución local con Newman

Antes de automatizar la colección en CI, se probó localmente para confirmar que
todos los casos respondían como se esperaba.

Primero se instaló Newman de forma global:

```bash
npm install -g newman
```

Luego se levantó la aplicación con Docker Compose, ya con el archivo .env
configurado con un BEARER_TOKEN real:

```bash
docker compose up -d
```

Y finalmente se ejecutó la colección, pasando el token por línea de comandos para
sobreescribir el valor de placeholder que trae el archivo exportado:

```bash
newman run blacklist_app/postman/blacklist_app.postman_collection.json \
  --env-var "token=<BEARER_TOKEN_LOCAL>"
```

Newman ejecutó las nueve peticiones en orden y mostró en la terminal un resumen
con la cantidad de aserciones que pasaron y fallaron, confirmando que los códigos
de respuesta coincidían con lo esperado en cada caso.

## Paso 4: Nuevo job en GitHub Actions

Se agregó un nuevo job llamado `pruebas_integracion` al archivo
`.github/workflows/main.yml`, al mismo nivel que el job existente de pruebas
unitarias (`job1`).

Este job depende de que `job1` termine exitosamente, usando `needs: job1`. Esto
significa que si las pruebas unitarias o el 90% de cobertura fallan, las pruebas de
integración ni siquiera se intentan correr.

Los pasos internos del job son los siguientes:

1. Descargar el código del repositorio con actions/checkout.
2. Crear un archivo .env dentro de blacklist_app, usando el secreto BEARER_TOKEN
   configurado en GitHub, ya que ese archivo no está versionado en el repositorio.
3. Levantar la aplicación completa con `docker compose up --build -d`, construyendo
   la imagen y levantando tanto el contenedor de Flask como el de PostgreSQL.
4. Esperar de forma activa a que el endpoint /blacklists/ping responda
   correctamente, para asegurarse de que la aplicación y la base de datos ya
   terminaron de inicializar antes de mandar peticiones reales.
5. Instalar Newman con `npm install -g newman`.
6. Ejecutar la colección exportada en el Paso 2 contra el servicio recién
   levantado, pasando el mismo secreto BEARER_TOKEN como variable de entorno de
   la colección.
7. Apagar los contenedores con `docker compose down -v`, incluso si alguna
   prueba anterior falló, usando la condición `if: always()`.

Para que este job funcione, fue necesario crear un secreto en GitHub llamado
BEARER_TOKEN, desde Settings, luego Secrets and variables, luego Actions, luego
New repository secret. Este secreto se usa dos veces dentro del job, tanto para
crear el .env como para autenticar las peticiones de Newman, así que ambos
lugares siempre quedan sincronizados automáticamente sin necesidad de mantenerlos
iguales a mano.

## Paso 5: Enlace del repositorio

El repositorio completo, incluyendo el código fuente, las pruebas unitarias, la
colección de Postman y el workflow de GitHub Actions, se encuentra en:

https://github.com/leonardomacht/blacklist_app

## Paso 6: Este informe dentro de /docs

Este mismo archivo se agregó al repositorio en la carpeta docs, en la raíz del
proyecto, con el nombre:

```
docs/informe_pruebas_integracion.md
```

## Resultado final

Con estos cambios, el pipeline de GitHub Actions queda compuesto por dos jobs
encadenados. El primero corre las pruebas unitarias y exige un mínimo de 90% de
cobertura de código. El segundo, que solo corre si el primero pasa, levanta la
aplicación completa en contenedores y valida su comportamiento real a través de
los endpoints REST, usando la misma colección de Postman que se probó de forma
manual. Cualquier Pull Request hacia master queda bloqueado automáticamente si
alguno de los dos jobs falla.
