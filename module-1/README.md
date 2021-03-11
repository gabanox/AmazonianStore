# Creación de un sitio web estático en Amazon S3

#### Cree un bucket de S3 y configúrelo para el alojamiento de sitios web

A continuación, crearemos los componentes de infraestructura necesarios para alojar un sitio web estático en Amazon S3 a través de la AWS CLI.

***Nota: Este taller utiliza marcadores de posición para los nombres que debe proporcionar. Estos marcadores de posición usan el prefijo REPLACE_ME_ para facilitar su búsqueda usando CTRL-F en Windows o ⌘-F en Mac.***

Primero, cree un bucket de S3, reemplace REPLACE_ME_BUCKET_NAME con su propio nombre de bucket único, como se describe en los [requerimientos para nombres de bucket](https://docs.aws.amazon.com/AmazonS3/latest/dev/BucketRestrictions.html#bucketnamingrules).** ** Copie el nombre que elija y guárdelo para más adelante, ya que lo usará en varios otros lugares durante este taller:

```
aws s3 mb s3://REPLACE_ME_BUCKET_NAME
```

Ahora que hemos creado un bucket, necesitamos establecer algunas opciones de configuración que permitan que el bucket se utilice para el alojamiento de sitios web estáticos. Esta configuración permite que los objetos en el bucket se soliciten utilizando un nombre DNS público registrado para el bucket, así como solicitudes de sitio directas a la ruta base del nombre DNS a la página de inicio de un sitio web seleccionado (index.html en la mayoría de los casos):

```
aws s3 website s3://REPLACE_ME_BUCKET_NAME --index-document index.html
```

#### Actualizar la política de bucket de S3


Todos los buckets creados en Amazon S3 son completamente privados de forma predeterminada. Para que se pueda utilizar como un sitio web público, debemos crear una Política de bucket de S3 que indique que cualquier persona puede acceder públicamente a los objetos almacenados en este nuevo bucket. Las políticas de bucket se representan como documentos JSON que definen las acciones de S3 (llamadas a la API de S3) que se permite (o no se permite) realizar por diferentes Principals (en nuestro caso, el público o cualquier persona).

El documento JSON para la política de bucket necesaria se encuentra en: `~/environment/AmazonianStore/module-1/aws-cli/website-bucket-policy.json` Este archivo contiene una cadena que debe reemplazarse con el nombre del bucket que eligió (indicado con `REPLACE_ME_BUCKET_NAME` ).

Para abrir un archivo en Cloud9, use el Explorador de archivos en el panel izquierdo y haga doble click `website-bucket-policy.json`:

![bucket-policy-image.png](/images/module-1/bucket-policy-image.png)

Esto se abrirá `bucket-policy.json`en el panel Editor de archivos. Reemplace la cadena que se muestra con el nombre de su bucket elegido utilizado en los comandos anteriores:

![replace-bucket-name.png](/images/module-1/replace-bucket-name.png)

Ejecute el siguiente comando de la CLI para agregar una política de bucket público a su sitio web:

```
aws s3api put-bucket-policy --bucket REPLACE_ME_BUCKET_NAME --policy file://~/environment/AmazonianStore/module-1/aws-cli/website-bucket-policy.json
```

#### Publicar el contenido del sitio web en S3

Ahora que nuestro nuevo bucket de sitios web está configurado correctamente, agreguemos la primera iteración de la página de inicio de Amazonian Store al bucket. Utilice el siguiente comando de la CLI de S3 que es similar al comando de Linux para copiar archivos ( cp ) para copiar la página index.html proporcionada localmente desde su IDE hasta el nuevo bucket de S3 (reemplazando el nombre del bucket de forma apropiada).

```
aws s3 cp ~/environment/AmazonianStore/module-1/web/index.html s3://REPLACE_ME_BUCKET_NAME/index.html
```

Ahora, abra su navegador web favorito e ingrese uno de los URI a continuación en la barra de direcciones. Uno de los URI siguientes contiene un '.' antes del nombre de la región, y el otro un '-'. Cuál debe usar depende de la región que esté usando.

La cadena para reemplazar ***REPLACE_ME_YOUR_REGION*** debe coincidir con la región en la que creó el bucket S3 (por ejemplo: us-east-1):

Para us-east-1 (N. Virginia), us-west-2 (Oregón), eu-west-1 (Irlanda) utilice:

```
http://REPLACE_ME_BUCKET_NAME.s3-website-REPLACE_ME_YOUR_REGION.amazonaws.com
```

Para el uso de us-east-2 (Ohio):

```
http://REPLACE_ME_BUCKET_NAME.s3-website.REPLACE_ME_YOUR_REGION.amazonaws.com
```

¡Felicitaciones, has desacoplado los componentes estáticos del sitio web hacia Amazon S3

#### Challenge sobre Amazon CloudFront: prácticas recomendadas para el servicio de sitios web en AWS

Para que este taller lo lleve rápidamente más allá de la parte del sitio web estático del sitio web Amazonian Store, le pedimos que haga que un bucket de S3 sea de acceso público. Si bien la creación de buckets de S3 públicos está perfectamente bien y es típico para muchas aplicaciones ... al crear un sitio web de cara al público en AWS, es una buena práctica que utilice Amazon CloudFront como la red de entrega de contenido global (CDN) y el punto de conexión de cara al público. para su sitio.

Amazon CloudFront habilita muchas capacidades diferentes que son beneficiosas para los sitios web públicos (menor latencia, redundancia global, integración con AWS Web Application Firewall, etc.) e incluso reduce los costos de transferencia de datos para un sitio web en comparación con que los clientes soliciten datos directamente de S3.

Pero, debido a su naturaleza global, la creación de una nueva distribución de CloudFront puede tardar más de 15 minutos en algunos casos antes de que esté disponible en todo el mundo. Por eso, hemos decidido omitir ese paso en este tutorial para avanzar más rápido. Pero si está creando un sitio web público por su cuenta, el uso de CloudFront debe considerarse un requisito para que se cumplan las mejores prácticas.

Eso concluye el Módulo 1.

[Proceder al Módulo 2](/module-2)