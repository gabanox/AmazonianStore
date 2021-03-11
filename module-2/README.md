# Módulo 2: Creación de un servicio con AWS Fargate

![Arquitectura](/images/module-2/architecture-module-2.png)

**Tiempo para completar:** 60 minutos

**Services utilizados:**
* [AWS CloudFormation](https://aws.amazon.com/cloudformation/)
* [AWS Identity and Access Management (IAM)](https://aws.amazon.com/iam/)
* [Amazon Virtual Private Cloud (VPC)](https://aws.amazon.com/vpc/)
* [Amazon Elastic Load Balancing](https://aws.amazon.com/elasticloadbalancing/)
* [Amazon Elastic Container Service (ECS)](https://aws.amazon.com/ecs/)
* [AWS Fargate](https://aws.amazon.com/fargate/)
* [AWS Elastic Container Registry (ECR)](https://aws.amazon.com/ecr/)
* [AWS CodeCommit](https://aws.amazon.com/codecommit/)
* [AWS CodePipeline](https://aws.amazon.com/codepipeline/)
* [AWS CodeDeploy](https://aws.amazon.com/codedeploy/)
* [AWS CodeBuild](https://aws.amazon.com/codebuild/)


### Vista General

En el Módulo 2, creará un nuevo microservicio alojado con [AWS Fargate](https://aws.amazon.com/fargate/) en [Amazon Elastic Container Service](https://aws.amazon.com/ecs/) para que su sitio web Amazonian Store pueda tener un backend de aplicación con el que integrarse. AWS Fargate es una opción de implementación en Amazon ECS que le permite implementar contenedores sin tener que administrar clústeres o servidores. Para nuestro backend Amazonian Store, usaremos Python y crearemos una aplicación Flask en un contenedor Docker detrás de un Balanceador de carga de red. Estos formarán el backend de microservicios para que el sitio web de frontend se integre.

### Creación de la infraestructura principal con AWS CloudFormation

Antes de que podamos crear nuestro servicio, debemos crear el entorno de infraestructura central que utilizará el servicio, incluida la infraestructura de red en [Amazon VPC](https://aws.amazon.com/vpc/) y los roles de [AWS Identity and Access Management](https://aws.amazon.com/iam/) que definirán los permisos que ECS y nuestros contenedores tendrán en parte superior de AWS. Usaremos [AWS CloudFormation](https://aws.amazon.com/cloudformation/) para lograr esto. AWS CloudFormation es un servicio que puede aprovisionar de manera programática los recursos de AWS que declara dentro de archivos JSON o YAML denominados Plantillas de CloudFormation , lo que permite la práctica recomendada común de Infraestructura como código.. Hemos proporcionado una plantilla de CloudFormation para crear todos los recursos de red y seguridad necesarios en `/module-2/cfn/core.yml`. Esta plantilla creará los siguientes recursos:

* [**Una Amazon VPC**](https://aws.amazon.com/vpc/) - un entorno de red que contiene cuatro subredes (dos públicas y dos privadas) en el espacio de IP privado 10.0.0.0/16, así como todas las configuraciones de tabla de ruta necesarias. Las subredes para esta red se crean en zonas de disponibilidad (AZ) de AWS independientes para permitir una alta disponibilidad en varias instalaciones físicas en una región de AWS.
* [**Dos NAT Gateways**](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-nat-gateway.html) (una para cada subred pública, que también abarca varias zonas de disponibilidad): permiten que los contenedores que finalmente implementaremos en nuestras subredes privadas se comuniquen con Internet para descargar los paquetes necesarios, etc.
* [**A DynamoDB VPC Endpoint**](https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/vpc-endpoints-dynamodb.html) - nuestro backend de microservicio se integrará finalmente con Amazon DynamoDB para la persistencia (como parte del módulo 3).
* [**A Security Group**](https://docs.aws.amazon.com/vpc/latest/userguide/VPC_SecurityGroups.html) - permite que los contenedores Docker reciban tráfico en el puerto 8080 desde Internet a través del balanceador de carga de red.
* [**IAM Roles**](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html) - se crean los roles de administración de identidad y acceso. Estos se utilizarán durante todo el taller para brindar a los servicios o recursos de AWS que cree acceso a otros servicios de AWS como DynamoDB y S3 entre otros.

Para crear estos recursos, ejecute el siguiente comando en la terminal de Cloud9 (tomará ~ 10 minutos para que se crear el stack):

```
aws cloudformation create-stack --stack-name AmazonianStoreCoreStack --capabilities CAPABILITY_NAMED_IAM --template-body file://~/environment/AmazonianStore/module-2/cfn/core.yml   
```

Puede verificar el estado de la creación de su pila a través de la Consola de AWS o ejecutando el comando:

```
aws cloudformation describe-stacks --stack-name AmazonianStoreCoreStack
```

Ejecute el comando `describe-stacks`, hasta que vea un estado de ```"StackStatus": "CREATE_COMPLETE"```
![cfn-complete.png](/images/module-2/cfn-complete.png)

Cuando reciba esta respuesta, CloudFormation habrá terminado de aprovisionar todos los recursos básicos de red y seguridad descritos anteriormente y puede continuar. Espere a que se muestre la pila anterior `CREATE_COMPLETE` antes de continuar.

**Utilizará valores de la salida de este comando durante el resto del taller. Puede ejecutar el siguiente comando para enviar directamente el comando `describe-stacks` anterior a un nuevo archivo en su IDE que se almacenará como `cloudformation-core-output.json`:**

```
aws cloudformation describe-stacks --stack-name AmazonianStoreCoreStack > ~/environment/cloudformation-core-output.json
```

#### Módulo 2a: Implementación de un servicio con AWS Fargate

### Creación del backend con un contenedor Docker en Flask

#### Construcción de la imagen

A continuación, creará una imagen de contenedor de Docker que contiene todo el código y la configuración necesarios para ejecutar el backend de Amazonian Store como una API de microservicio creada con Flask. Crearemos la imagen del contenedor de Docker dentro de Cloud9 y luego la enviaremos al Registro de contenedores elásticos de Amazon, donde estará disponible para extraer cuando creemos nuestro servicio con Fargate.

Todo el código necesario para ejecutar nuestro servicio de backend se almacena en el directorio `/module-2/app/` del repositorio que ha clonado en su IDE de Cloud9. Si desea revisar el código Python que usa Flask para crear la API de servicio, vea el archivo `/module-2/app/service/amazonianStoreService.py`.

All of the code required to run our service backend is stored within the `/module-2/app/` directory of the repository you've cloned into your Cloud9 IDE.  If you would like to review the Python code that uses Flask to create the service API, view the `/module-2/app/service/amazonianStoreService.py` file.

Docker ya viene instalado en el IDE de Cloud9 que ha creado, por lo que para construir la imagen de Docker localmente, todo lo que tenemos que hacer es ejecutar los siguientes comandos en la terminal de Cloud9:

* Navegar a `~/environment/module-2/app`

```
cd ~/environment/AmazonianStore/module-2/app
```

* Puede obtener su ID de cuenta y la región predeterminada a partir de la salida de CloudFormation ** describe-stacks 

* Reemplace *REPLACE_ME_ACCOUNT_ID* con su ID de cuenta y *REPLACE_ME_REGION* con su región predeterminada en el siguiente comando para construir la imagen de Docker usando el archivo Dockerfile , que contiene instrucciones de Docker. El comando etiqueta la imagen de Docker, utilizando la -topción, con un formato de etiqueta específico para que la imagen se pueda enviar posteriormente al servicio [Amazon Elastic Container Registry](https://aws.amazon.com/ecr/).


```
docker build . -t REPLACE_ME_ACCOUNT_ID.dkr.ecr.REPLACE_ME_REGION.amazonaws.com/amazonianstore/service:latest
```

Verá que Docker  instala todos los paquetes de dependencia necesarios que nuestra aplicación necesita y genera la etiqueta para la imagen construida. Copie la etiqueta de la imagen para referencia posterior. Debajo de la etiqueta de ejemplo que se muestra es: *111111111111.dkr.ecr.us-east-1.amazonaws.com/amazonianstore/service:latest*

```
Successfully built 8bxxxxxxxxab
Successfully tagged 111111111111.dkr.ecr.us-east-1.amazonaws.com/amazonianstore/service:latest
```

#### Testing del servicio de forma local

Probemos nuestra imagen localmente dentro de Cloud9 para asegurarnos de que todo funcione como se espera. Copie la etiqueta de imagen que resultó del comando anterior y ejecute el siguiente comando para implementar el contenedor "localmente" (que en realidad está dentro de su IDE de Cloud9 dentro de AWS):

```
docker run -p 8080:8080 REPLACE_ME_WITH_DOCKER_IMAGE_TAG
```

Como resultado, verá que Docker informa que su contenedor está funcionando localmente:

```
 * Running on http://0.0.0.0:8080/ (Press CTRL+C to quit)
```

Para probar nuestro servicio con una solicitud local, vamos a abrir el navegador web integrado dentro del IDE de Cloud9 que se puede usar para obtener una vista previa de las aplicaciones que se ejecutan en la instancia del IDE. Para abrir el navegador web de vista previa, seleccione `Vista previa>`` Vista previa de la aplicación en ejecución en la barra de menú de Cloud9:

![preview-menu](/images/module-2/preview-menu.png)

Esto abrirá otro panel en el IDE donde estará disponible el navegador web. Agregue /store al final del URI en la barra de direcciones del navegador de vista previa en el nuevo panel y presione enter:

![preview-menu](/images/module-2/address-bar.png)

Si tiene éxito, verá una respuesta del servicio que devuelve el documento JSON almacenado en `/AmazonianStore/module-2/app/service/store-response.json`

Cuando termine de probar el servicio, puede detenerlo presionando CTRL-c en PC o Mac.

#### Envío de la imagen de Docker a Amazon ECR

Con una prueba exitosa de nuestro servicio a nivel local, estamos listos para crear un repositorio de imágenes de contenedor en [Amazon Elastic Container Registry](https://aws.amazon.com/ecr/) (Amazon ECR) e insertar nuestra imagen en él. Para crear el registro, ejecute el siguiente comando, esto crea un nuevo repositorio en el registro AWS ECR predeterminado creado para su cuenta.


```
aws ecr create-repository --repository-name amazonianstore/service
```

La respuesta a este comando contendrá metadatos adicionales sobre el repositorio creado. Para enviar imágenes de contenedor a nuestro nuevo repositorio, necesitaremos obtener credenciales de autenticación para nuestro cliente Docker en el repositorio. Ejecute el siguiente comando, que devolverá un comando de inicio de sesión para recuperar las credenciales de nuestro cliente Docker y luego ejecutarlo automáticamente (incluya el comando completo, incluido el $ a continuación). Se informará 'Inicio de sesión exitoso' si el comando es exitoso.

```
$(aws ecr get-login --no-include-email)
```

A continuación, envíe la imagen que creó al repositorio de ECR utilizando la etiqueta copiada anteriormente. Con este comando, Docker enviará su imagen y todas las imágenes de las que depende a Amazon ECR:

```
docker push REPLACE_ME_WITH_DOCKER_IMAGE_TAG
```

Ejecute el siguiente comando para ver la imagen Docker recién enviada almacenada dentro del repositorio de ECR:

```
aws ecr describe-images --repository-name amazonianstore/service
```

### Configuración de los requisitos previos del servicio en Amazon ECS

#### Crear un clúster de ECS

Ahora, tenemos una imagen disponible en ECR que podemos implementar en un servicio alojado en Amazon ECS usando AWS Fargate. El mismo servicio que probó localmente a través del terminal en Cloud9 como parte del último módulo ahora se implementará en la nube y estará disponible públicamente detrás de un Equilibrador de carga de red.

Primero, crearemos un clúster en Amazon Elastic Container Service (ECS) . Esto representa el grupo de "servidores" en el que se implementarán sus contenedores de servicios. Los servidores están entre "cotizaciones" porque utilizará AWS Fargate . Fargate le permite especificar que sus contenedores se implementen en un clúster sin tener que aprovisionar o administrar ningún servidor usted mismo.

Para crear un nuevo clúster en ECS, ejecute el siguiente comando:

```
aws ecs create-cluster --cluster-name AmazonianStore-Cluster
```

#### Cree un grupo de registros de AWS CloudWatch Logs

A continuación, crearemos un nuevo grupo de registros en AWS CloudWatch Logs . AWS CloudWatch Logs es un servicio para la recopilación y el análisis de registros. Los registros que genera su contenedor se enviarán automáticamente a los registros de AWS CloudWatch como parte de este grupo específico. Esto es especialmente importante al utilizar AWS Fargate, ya que no tendrá acceso a la infraestructura del servidor donde se ejecutan sus contenedores.

Para crear el nuevo grupo de registros en CloudWatch, ejecute el siguiente comando:

```
aws logs create-log-group --log-group-name amazonianstore-logs
```

#### Registrar una definición de tarea de ECS

Ahora que tenemos un clúster creado y un grupo de registros definido para dónde se enviarán nuestros registros de contenedor, estamos listos para registrar una definición de tarea de ECS . Una tarea en ECS es un conjunto de imágenes de contenedor que deben programarse juntas. Una definición de tarea declara ese conjunto de contenedores y los recursos y la configuración que requieren esos contenedores. Utilizará la AWS CLI para crear una nueva definición de tarea sobre cómo se debe programar su nueva imagen de contenedor en el clúster de ECS que acabamos de crear.

Se ha proporcionado un archivo JSON que servirá como entrada para el comando CLI.

Abrir `~/environment/AmazonianStore/module-2/aws-cli/task-definition.json` en el IDE.

Reemplace los valores indicados con los apropiados de sus recursos creados.

Estos valores se extraerán de la respuesta de CloudFormation que copió anteriormente, así como de la etiqueta de imagen de la ventana acoplable que envió anteriormente a ECR, por ejemplo: `REPLACE_ME_ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/amazonianstore/service:latest`

Una vez que haya reemplazado los valores `task-defintion.json`y lo haya guardado. Ejecute el siguiente comando para registrar una nueva definición de tarea en ECS:

```
aws ecs register-task-definition --cli-input-json file://~/environment/AmazonianStore/module-2/aws-cli/task-definition.json
```

### Habilitación de un servicio Fargate con equilibrio de carga

#### Crear un balanceador de carga de red

Con una nueva definición de tarea registrada, estamos listos para aprovisionar la infraestructura necesaria en nuestra pila de servicios. En lugar de exponer directamente nuestro servicio a Internet, proporcionaremos un [**Network Load Balancer (NLB)**](https://docs.aws.amazon.com/elasticloadbalancing/latest/network/introduction.html) para que se ubique frente a nuestro nivel de servicio. Esto permitiría que el código de nuestro sitio web frontend se comunique con un solo nombre DNS, mientras que nuestro servicio backend podría escalar elásticamente hacia adentro y hacia afuera, en múltiples zonas de disponibilidad, según la demanda o si ocurren fallas y es necesario aprovisionar nuevos contenedores.

Para aprovisionar un nuevo NLB, ejecute el siguiente comando CLI en la terminal de Cloud9 (recupere los subnetIds de la salida de CloudFormation que guardó):


```
aws elbv2 create-load-balancer --name amazonian-nlb --scheme internet-facing --type network --subnets REPLACE_ME_PUBLIC_SUBNET_ONE REPLACE_ME_PUBLIC_SUBNET_TWO > ~/environment/nlb-output.json
```

Cuando este comando se haya completado con éxito, se creará un nuevo archivo en su IDE llamado nlb-output.json. Usted va a utilizar las `DNSName`, `VpcId` y `LoadBalancerArn` los pasos en posteriores.

#### Crear un grupo de destino de equilibrador de carga

A continuación, utilice la CLI para crear un grupo objetivo de NLB . Un grupo objetivo permite que los recursos de AWS se registren como objetivos para las solicitudes que el equilibrador de carga recibe para reenviar. Nuestros contenedores de servicios se registrarán automáticamente en este objetivo para que puedan recibir tráfico de la NLB cuando se aprovisionen. Este comando incluye un valor que deberá reemplazarse, el vpc-idcual se puede encontrar como un valor dentro de la salida de `AmazonianStoreCoreStack` guardada anteriormente devuelta por CloudFormation.

```
aws elbv2 create-target-group --name AmazonianStore-TargetGroup --port 8080 --protocol TCP --target-type ip --vpc-id REPLACE_ME_VPC_ID --health-check-interval-seconds 10 --health-check-path / --health-check-protocol HTTP --healthy-threshold-count 3 --unhealthy-threshold-count 3 > ~/environment/target-group-output.json
```

Cuando se complete este comando, su salida se guardará `target-group-output.json` en su IDE. Hará referencia al `TargetGroupArn` valor en un paso posterior.

#### Crear un escucha del equilibrador de carga

A continuación, use la CLI para crear un escucha del equilibrador de carga para el NLB. Esto informa al equilibrador de carga que para las solicitudes recibidas en un puerto específico, deben reenviarse a los destinos que se han registrado en el grupo de destino anterior. Asegúrese de reemplazar los dos valores indicados con el ARN apropiado del TargetGroup y el NLB que guardó en los pasos anteriores:

```
aws elbv2 create-listener --default-actions TargetGroupArn=REPLACE_ME_NLB_TARGET_GROUP_ARN,Type=forward --load-balancer-arn REPLACE_ME_NLB_ARN --port 80 --protocol TCP
```

### Creación de un servicio con Fargate

#### Creación de un rol vinculado al servicio para ECS

Si ya ha utilizado ECS en el pasado, puede omitir este paso y continuar con el siguiente. Si nunca antes ha utilizado ECS, debemos crear un rol vinculado al servicio en IAM que otorgue al servicio de ECS permisos para realizar solicitudes de API de ECS dentro de su cuenta. Esto es necesario porque cuando crea un servicio en ECS, el servicio llamará a las API dentro de su cuenta para realizar acciones como extraer imágenes Docker, crear nuevas tareas, etc.

Sin la creación de este rol, no se otorgarían permisos al servicio ECS para realizar las acciones necesarias. Para crear el rol, ejecute el siguiente comando en la terminal:

```
aws iam create-service-linked-role --aws-service-name ecs.amazonaws.com
```

Si lo anterior devuelve un error sobre el rol que ya existe, puede ignorarlo, ya que indicaría que el rol se creó automáticamente en su cuenta en el pasado.


#### Crear el servicio

Con el NLB creado y configurado, y el servicio ECS otorgado los permisos adecuados, estamos listos para crear el servicio ECS real donde nuestros contenedores se ejecutarán y se registrarán en el balanceador de carga para recibir tráfico. Hemos incluido un archivo JSON para la entrada de la CLI que se encuentra en: `~/environment/aws-modern-application-workshop/module-2/aws-cli/service-definition.json`. Este archivo incluye todos los detalles de configuración para el servicio que se creará, incluida la indicación de que este servicio debe iniciarse con AWS Fargate , lo que significa que no tiene que aprovisionar ningún servidor dentro del clúster de destino. Los contenedores que están programados como parte de la tarea que se usa en este servicio se ejecutarán en un clúster completamente administrado por AWS.

Abra `~/environment/aws-modern-application-workshop/module-2/aws-cli/service-definition.json` en el IDE y reemplace los valores indicados de `REPLACE_ME`. Guárdelo, luego ejecute el siguiente comando para crear el servicio:

```
aws ecs create-service --cli-input-json file://~/environment/AmazonianStore/module-2/aws-cli/service-definition.json
```

Una vez creado el servicio, ECS aprovisionará una nueva tarea que ejecuta el contenedor que ha enviado a ECR y lo registrará en el NLB creado.

#### Pruebe el servicio

Copie el nombre DNS que guardó al crear el NLB y envíele una solicitud usando el navegador de vista previa en Cloud9 (o simplemente con cualquier navegador web, ya que esta vez nuestro servicio está disponible en Internet). Intente enviar una solicitud al recurso `/store`:

```
http://amazonian-nlb-123456789-abc123456.elb.us-east-1.amazonaws.com/store
```

Una respuesta que muestra la misma respuesta JSON que recibimos anteriormente al probar el contenedor de la ventana acoplable localmente en Cloud9 significa que su API de Flask está en funcionamiento en AWS Fargate.

>Note: Nota: este balanceador de carga de red solo admite solicitudes HTTP (http: //) ya que no tiene instalados certificados SSL / TLS. Para este tutorial, asegúrese de enviar solicitudes usando http: // solamente, las solicitudes https: // no funcionarán correctamente.

### Actualizar Amazonian Store para llamar a la NLB

#### Reemplazar el API Endpoint
A continuación, debemos integrar nuestro sitio web con su nuevo backend de API en lugar de utilizar los datos codificados que cargamos previamente en S3. Deberá actualizar el siguiente archivo para usar la misma URL NLB para las llamadas a la API (no incluya la ruta /store ):/module-2/web/index.html

Abra el archivo en Cloud9 y reemplace el área resaltada a continuación entre las comillas con la URL NLB:

![before replace](/images/module-2/before-replace.png)

Después de pegar, la línea debería verse similar a la siguiente:

![after replace](/images/module-2/after-replace.png)

#### Subir a S3
Para cargar este archivo en su sitio web alojado en S3, use nuevamente el nombre del bucket que se creó durante el Módulo 1 y ejecute el siguiente comando:

```
aws s3 cp ~/environment/AmazonianStore/module-2/web/index.html s3://INSERT-YOUR-BUCKET-NAME/index.html
```

Abra su sitio web utilizando la misma URL que se utilizó al final del Módulo 1 para ver su nuevo sitio web Amazonian Store, que está recuperando datos JSON de su API Flask que se ejecuta dentro de un contenedor Docker implementado en AWS Fargate.


## Módulo 2b: Automatización de implementaciones mediante AWS Code Services

![Architecture](/images/module-2/architecture-module-2b.png)


### Creación de la canalización de CI / CD

#### Crear un bucket S3 para los artefactos de canalización

Ahora que tiene un servicio en funcionamiento, puede pensar en los cambios de código que le gustaría realizar en su servicio Flask. Sería un cuello de botella para su velocidad de desarrollo si tuviera que seguir todos los mismos pasos anteriores cada vez que quisiera implementar una nueva función en su servicio. ¡Ahí es donde entran en juego la integración continua y la entrega continua o CI / CD!

En este módulo, creará una pila de CI / CD completamente administrada que entregará automáticamente todos los cambios de código que realice en su base de código al servicio que creó durante el último módulo.

Primero, necesitamos crear otro bucket de S3 que se utilizará para almacenar los artefactos temporales que se crean en medio de nuestras ejecuciones de canalización de CI / CD. Elija un nuevo nombre de depósito para estos artefactos y cree uno con el siguiente comando CLI:

```
aws s3 mb s3://REPLACE_ME_CHOOSE_ARTIFACTS_BUCKET_NAME
```

A continuación, este bucket necesita una política de bucket para definir permisos para los datos almacenados en él. Pero a diferencia de nuestro grupo de sitios web que permitía el acceso a cualquier persona, solo nuestra canalización de CI / CD debería tener acceso a este grupo. Hemos proporcionado el archivo JSON necesario para esta política en `~/environment/AmazonianStore/module-2/aws-cli/artifacts-bucket-policy.json`. Abra este archivo y, en su interior, deberá reemplazar varias cadenas para incluir los ARN que se crearon anteriormente como parte de AmazonianStoreCoreStack, así como el nombre de bucket recién elegido para sus artefactos de CI / CD.

Una vez que haya modificado y guardado este archivo, ejecute el siguiente comando para otorgar acceso a este depósito a su canalización de CI / CD:

```
aws s3api put-bucket-policy --bucket REPLACE_ME_ARTIFACTS_BUCKET_NAME --policy file://~/environment/AmazonianStore/module-2/aws-cli/artifacts-bucket-policy.json
```

#### Crear un repositorio de CodeCommit

Necesitará un lugar para enviar y almacenar su código. Cree un repositorio de [**AWS CodeCommit Repository**](https://aws.amazon.com/codecommit/) con la CLI para este propósito:

```
aws codecommit create-repository --repository-name AmazonianStoreService-Repository
```

#### Crear un proyecto de CodeBuild

Con un repositorio para almacenar nuestro código y un bucket de S3 que se utilizará para nuestros artefactos de CI / CD, agreguemos a la pila de CI / CD con una forma de que se produzca una compilación de servicio. Esto se logrará mediante la creación de un proyecto de AWS CodeBuild . Cada vez que se activa la ejecución de una compilación, AWS CodeBuild aprovisionará automáticamente un servidor de compilación para nuestra configuración y ejecutará los pasos necesarios para compilar nuestra imagen Docker y enviará una nueva versión al repositorio de ECR que creamos (y luego apagará el servidor cuando la construcción está completa). Los pasos para nuestra compilación (que empaquetan nuestro código Python y compilan / empujan el contenedor Docker) están incluidos en el archivo `~/environment/aws-modern-application-workshop/module-2/app/buildspec.yml`. El ***buildspec.yml*** file es lo que crea para instruir a CodeBuild sobre los pasos necesarios para la ejecución de una compilación dentro de un proyecto de CodeBuild.

Para crear el proyecto CodeBuild, se requiere que se actualice otro archivo de entrada CLI con parámetros específicos de sus recursos. Se encuentra en `~/environment/aws-modern-application-workshop/module-2/aws-cli/code-build-project.json`. De manera similar, reemplace los valores dentro de este archivo como lo hizo antes desde AmazonianStoreCoreStackOutput. Una vez guardado, ejecute lo siguiente con la CLI para crear el proyecto:

```
aws codebuild create-project --cli-input-json file://~/environment/AmazonianStore/module-2/aws-cli/code-build-project.json
```

#### Crear una canalización de CodePipeline

Finalmente, necesitamos una forma de integrar continuamente nuestro repositorio CodeCommit con nuestro proyecto CodeBuild para que las compilaciones se produzcan automáticamente cada vez que se envíe un cambio de código al repositorio. Entonces, necesitamos una forma de entregar continuamente esos artefactos recién construidos a nuestro servicio en ECS. [**AWS CodePipeline**](https://aws.amazon.com/codepipeline/) es el servicio que une estas acciones en una canalización que creará a continuación.

Su canalización en CodePipeline hará exactamente lo que describí anteriormente. Cada vez que se envía un cambio de código a su repositorio de CodeCommit, CodePipeline entregará el código más reciente a su proyecto de AWS CodeBuild para que se produzca una compilación. Cuando CodeBuild lo crea correctamente, CodePipeline realizará una implementación en ECS utilizando la imagen de contenedor más reciente que la ejecución de CodeBuild envió a ECR.

Todos estos pasos se definen en un archivo JSON siempre que lo utilice como entrada en la AWS CLI para crear la canalización. Este archivo se encuentra en `~/environment/AmazonianStore/module-2/aws-cli/code-pipeline.json`, ábralo, reemplace los atributos requeridos dentro y guarde el archivo.

Una vez guardado, cree una canalización en CodePipeline con el siguiente comando:

```
aws codepipeline create-pipeline --cli-input-json file://~/environment/AmazonianStore/module-2/aws-cli/code-pipeline.json
```

#### Habilite el acceso automatizado al repositorio de imágenes ECR

Tenemos un último paso antes de que nuestra canalización de CI / CD pueda ejecutarse de un extremo a otro con éxito. Con una canalización de CI / CD en su lugar, ya no tendrá que enviar manualmente imágenes de contenedores a ECR. CodeBuild lanzará nuevas imágenes ahora. Necesitamos dar permiso a CodeBuild para realizar acciones en su repositorio de imágenes con una ***política de repositorio ECR***. El documento de política debe actualizarse con el ARN específico para el rol de CodeBuild creado por AmazonianStoreCoreStack, y el documento de política se encuentra en `~/environment/aws-modern-application-workshop/module-2/aws-cli/ecr-policy.json`. Actualice y guarde este archivo y luego ejecute el siguiente comando para crear la política:

```
aws ecr set-repository-policy --repository-name amazonianstore/service --policy-text file://~/environment/AmazonianStore/module-2/aws-cli/ecr-policy.json
```

Cuando se ha creado correctamente, tiene una canalización de CI / CD de un extremo a otro en funcionamiento para entregar los cambios de código automáticamente a su servicio en ECS.

### Pruebe la canalización de CI / CD

#### Uso de Git con AWS CodeCommit

Para probar la nueva canalización, necesitamos configurar git dentro de su IDE de Cloud9 e integrarlo con su repositorio de CodeCommit.

AWS CodeCommit proporciona un asistente de credenciales para git que usaremos para facilitar la integración. Ejecute los siguientes comandos en secuencia en el terminal para configurar git que se usará con AWS CodeCommit (ninguno informará ninguna respuesta si tiene éxito):

```
git config --global user.name "REPLACE_ME_WITH_YOUR_NAME"
```

```
git config --global user.email REPLACE_ME_WITH_YOUR_EMAIL@example.com
```

```
git config --global credential.helper '!aws codecommit credential-helper $@'
```

```
git config --global credential.UseHttpPath true
```

A continuación, cambie los directorios de su IDE al directorio del entorno utilizando la terminal:

```
cd ~/environment/
```

Ahora, estamos listos para clonar nuestro repositorio usando el siguiente comando de terminal:

```
git clone https://git-codecommit.REPLACE_REGION.amazonaws.com/v1/repos/AmazonianStoreService-Repository
```

This will tell us that our repository is empty¡Esto nos dirá que nuestro repositorio está vacío! Arreglemos eso copiando los archivos de la aplicación en nuestro directorio de repositorio usando el siguiente comando:

```
cp -r ~/environment/AmazonianStore/module-2/app/* ~/environment/AmazonianStoreService-Repository/
```

#### Empujar un cambio de código

Ahora, el código de servicio completo que usamos para crear nuestro servicio Fargate en el Módulo 2 se almacena en el repositorio local que acabamos de clonar de AWS CodeCommit. Hagamos un cambio en el servicio Flask antes de confirmar nuestros cambios, para demostrar que la canalización de CI / CD que hemos creado está funcionando. En Cloud9, abra el archivo almacenado en `~/environment/AmazonianStoreService-Repository/service/store-response.json` y cambie la descripción de alguno de los productos a otro valor y guarde el archivo.

Después de guardar el archivo, cambie los directorios al nuevo directorio del repositorio:

```
cd ~/environment/AmazonianStoreService-Repository/
```

Luego, ejecute los siguientes comandos de git para introducir los cambios de su código.

```
git add .
git commit -m "modifique la descripcion de uno de los productos."
git push
```

Una vez que el cambio se envía al repositorio, puede abrir el servicio CodePipeline en la consola de AWS para ver los cambios a medida que avanzan en la canalización de CI / CD. Después de confirmar su cambio de código, los cambios tardarán entre 5 y 10 minutos en implementarse en su servicio en vivo que se ejecuta en Fargate. Durante este tiempo, AWS CodePipeline organizará la activación de una ejecución de canalización cuando los cambios se hayan verificado en su repositorio de CodeCommit, activará su proyecto de CodeBuild para iniciar una nueva compilación y recuperará la imagen de la ventana acoplable que CodeBuild envió a ECR y realizará un ECS automatizado. Servicio de actualizaciónAcción para conectar drenar los contenedores existentes que se están ejecutando en su servicio y reemplazarlos con la imagen recién construida. Actualice su sitio web Amazonian Store en el navegador para ver que los cambios han surtido efecto.

Puede ver el progreso de su cambio de código a través de la consola de CodePipeline aquí (no se necesitan acciones, ¡solo observe la automatización en acción!): [AWS CodePipeline](https://console.aws.amazon.com/codepipeline/home)

Con esto concluye el Módulo 2.

[Continúe con el Módulo 3](/module-3)
