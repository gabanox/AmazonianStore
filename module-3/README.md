# Módulo 3: Agregar la capa de datos con Amazon DynamoDB

![Architecture](/images/module-3/architecture-module-3.png)

**Tiempo para completar:** 20 minutos

**Servicios utilizados:**
* [Amazon DynamoDB](https://aws.amazon.com/dynamodb/)

### Visión general

Ahora que tiene un servicio implementado y una canalización de CI / CD en funcionamiento para entregar cambios a ese servicio automáticamente cada vez que actualiza su repositorio de código, puede mover rápidamente las nuevas funciones de la aplicación desde la concepción hasta que estén disponibles para sus clientes de Amazonian Store. Con esta mayor agilidad, agreguemos otra pieza fundamental de funcionalidad a la arquitectura del sitio web Amazonian Store, un nivel de datos. En este módulo, creará una tabla en Amazon DynamoDB , un servicio de base de datos NoSQL administrado y escalable en AWS con un rendimiento súper rápido. En lugar de tener todos los Productos almacenados en un archivo JSON estático, los almacenaremos en una base de datos para que los sitios web sean más extensibles y escalables en el futuro.

### Agregar una base de datos NoSQL a Amazonian Store

#### Crear una tabla de DynamoDB

Para agregar una tabla DynamoDB a la arquitectura, hemos incluido otro archivo de entrada JSON CLI que define una tabla llamada ***ProductsTable*** . Esta tabla tendrá un índice principal definido por un atributo de clave hash llamado ***ProductId*** y dos índices secundarios más. El primer índice secundario tendrá la clave hash de ***AmazonPrime*** y una clave de rango de ***ProductId*** , y el segundo índice secundario tendrá la clave hash de ***DescuentoRegular*** y una clave de rango de ***ProductId***. Estos dos índices secundarios nos permitirán ejecutar consultas en la tabla para recuperar todos los productos que coinciden con un determinado producto en descuento ó disponible en Amazon Prime, para habilitar la funcionalidad de filtro que puede haber notado que aún no funciona en el sitio web. Puede ver este archivo en `~/environment/AmazonianStore/module-3/aws-cli/dynamodb-table.json`. No es necesario realizar cambios en este archivo y está listo para ejecutarse.

Para crear la tabla con la AWS CLI, ejecute el siguiente comando en la terminal de Cloud9:

```
aws dynamodb create-table --cli-input-json file://~/environment/AmazonianStore/module-3/aws-cli/dynamodb-table.json
```

Una vez que se ejecuta el comando, puede ver los detalles de su tabla recién creada ejecutando el siguiente comando de la AWS CLI en la terminal:

```
aws dynamodb describe-table --table-name ProductsTable
```

Si ejecutamos el siguiente comando para recuperar todos los elementos almacenados en la tabla, verá que la tabla está vacía:

```
aws dynamodb scan --table-name ProductsTable
```

```
{
    "Count": 0,
    "Items": [],
    "ScannedCount": 0,
    "ConsumedCapacity": null
}
```

#### Agregar elementos a la tabla de DynamoDB

También se proporciona un archivo JSON que se puede utilizar para insertar por lotes varios elementos de Mysfit en esta tabla. Esto se logrará a través de la API de DynamoDB BatchWriteItem. Para llamar a esta API usando el archivo JSON proporcionado, ejecute el siguiente comando de terminal (la respuesta del servicio debe informar que no hay elementos sin procesar):

```
aws dynamodb batch-write-item --request-items file://~/environment/AmazonianStore/module-3/aws-cli/populate-dynamodb.json
```

Ahora, si ejecuta el mismo comando para escanear todo el contenido de la tabla, encontrará que los elementos se han cargado en la tabla:

```
aws dynamodb scan --table-name ProductsTable
```

### Confirmación del primer cambio de código real

#### Copie el código de servicio Flask actualizado

Ahora que tenemos nuestros datos incluidos en la tabla, modifiquemos el código de nuestra aplicación para leer de esta tabla en lugar de devolver el archivo JSON estático que se usó en el Módulo 2. Hemos incluido un nuevo conjunto de archivos Python para su microservicio Flask, pero ahora, en lugar de leer el archivo JSON estático, realizará una solicitud a DynamoDB.

La solicitud se forma utilizando el AWS Python SDK llamado boto3 . Este SDK es una forma potente pero sencilla de interactuar con los servicios de AWS a través del código Python. Le permite utilizar definiciones y funciones de cliente de servicio que tienen una gran simetría con las API de AWS y los comandos de la CLI que ya ha estado ejecutando como parte de este taller. Traducir esos comandos a código Python funcional es simple cuando se usa boto3 . Para copiar los nuevos archivos en su directorio de repositorio de CodeCommit, ejecute el siguiente comando en la terminal:

```
cp ~/environment/AmazonianStore/module-3/app/service/* ~/environment/AmazonianStoreService-Repository/service/
```

#### Inserte el código actualizado en la canalización de CI / CD

Ahora, debemos verificar estos cambios de código en CodeCommit usando el cliente de línea de comando git. Ejecute los siguientes comandos para verificar los nuevos cambios de código y activar su canalización de CI / CD:

```
cd ~/environment/AmazonianStoreService-Repository
```

```
git add .
```

```
git commit -m "Add new integration to DynamoDB."
```

```
git push
```

Ahora, en solo 5-10 minutos, verá que los cambios de código se realizan a través de su canalización completa de CI / CD en CodePipeline y a su servicio Flask implementado en AWS Fargate en Amazon ECS. No dude en explorar la consola de AWS CodePipeline para ver el progreso de los cambios en su canalización.

#### Actualizar el contenido del sitio web en S3

Finalmente, necesitamos publicar una nueva página index.html en nuestro depósito S3 para que se utilice la nueva funcionalidad de la API que usa cadenas de consulta para filtrar las respuestas. El nuevo archivo index.html se encuentra en ~/environment/AmazonianStore/module-3/web/index.html. Abra este archivo en su IDE de Cloud9 y reemplace la cadena que indica “REPLACE_ME” tal como lo hizo en el Módulo 2, con el punto final NLB apropiado. Recuerde no incluir la ruta / productos. Consulte el archivo que ya editó en el directorio / module-2 / si es necesario. Después de reemplazar el punto final para que apunte a su NLB, cargue el nuevo archivo index.html ejecutando el siguiente comando (reemplazándolo por el nombre del depósito que creó en el Módulo 1:

```
aws s3 cp --recursive ~/environment/AmazonianStore/module-3/web/ s3://REPLACE_ME_WEBSITE_BUCKET_NAME/
```

Vuelva a visitar su sitio web Amazonian Store para ver los nuevos productos que se cargan desde su tabla de DynamoDB y cómo funciona la función de filtro.

Eso concluye el módulo 3.

[Proceder al Módulo 4](/module-4)

