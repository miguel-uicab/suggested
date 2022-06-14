# **SUGGESTED PRICE V5**

A continuación se explica cómo ejecutar los scripts de `python` relacionados con el __Proyecto de Precio Sugerido Versión 5__.

Para este proyecto se ha tomado como base `python 3.8.12`.

La repositorio de `GitHub` asociado al proyecto es `suggested-price`.


# __Archivos Workshop (suggested-price\training).__
El _Workshop_ es conformado por una etapa de pos-preprocesamiento además de una de ingeniería de características. Los dos scripts relacionados son:
1. __workshop.py__: Ejecuta de manera automática los eventos relacionados con el _Workshop_.
2. __workshop_functions.py__: Contiene las funciones necesarias para llevar a cabo el _Workshop_. La función principal es `data_workshop`.

Previo de instalar los requerimientos necesarios dados por `requirements_workshop.txt`, la forma de ejecutar en consola de manera automática el proceso _Workshop_ es la siguiente:
```
python workshop.py
```

La función más importante, es decir, `data_workshop` es gobernada por los siguientes parámetros, cuyos valores actuales puede consultarse en `config.yaml`:
* _path_: Directorio que contiene tanto los **archivos-entrada** y los **archivos-salida** del proceso _Workshop_.
* _name_data_raw_: Nombre del **archivo-entrada** necesario.
* _name_data_for_regression_: Nombre que llevará el **archivo-salida** que dará lugar a la data lista para los procesos de *Entrenamiento y Optimización*.
*_name_for_data_colonias_: Nombre que llevará el archivo con el cluster resultante para las colonias de Ciudad de México.
* _export_: Booleano para decidir si se guardan los **archivos-salida**.
*_luxury_features_: Booleano para decidir si se construyen las columnas que informan sobre las características de lujo de inmuebles.
* _clustering_: Booleano para decidir si se construye el cluster para colonias.
* _update_price_: Booleano para decidir si se construye una columna que contiene el "precio actualizado".
* _config_: Diccionario que contiene las variables necesarias para correr el proceso _Workshop_.


El **archivo-entrada** del proceso _Workshop_ está localizado en `suggested-price\outputs`:
* `data_raw.sav`: Contiene la data preprocesada y que es resultante del proceso de _Extracción-Transformación_.

Los **archivos-salida** del proceso _Workshop_ se localizan en `suggested-price\outputs`, y son:
* `data_for_regression.sav`: Contiene la data lista para el proceso de entrenamiento y optimización.
* `colonias_df.sav`: Contiene el cluster resultante para las colonias de Ciudad de México.
* `fids_not_used.sav`: Contiene los valores de `fid` poco frecuentes que han caído en el grupo `uncommon`.
* `grid_ids_not_used.sav`: Contiene los valores de `grid_id` poco frecuentes que han caído en el grupo `uncommon`.
* `neigh_ids_not_used.sav`: Contiene los valores de `neigh_id` poco frecuentes que han caído en el grupo `uncommon`.
* `grid_objectids_not_used.sav`: Contiene los valores de `grid_objectid` poco frecuentes que han caído en el grupo `uncommon`.



# __Archivos de Entrenamiento y Optimización (suggested-price\training).__
Los procesos de _Entrenamiento y Optimización_ se llevan a cabo de manera conjunta. Los dos scripts relacionados son:

1. __training.py__: Ejecuta de manera automática las funciones principales contenidas en `training_functions.py`.
2. __training_functions.py__: Contiene las funciones necesarias para el entrenamiento, optimización y guardado del modelo. Las funciones más importantes son `random_search_optimize_histogram_sklearn` y `fit_model`.

Previo a instalar los requerimientos necesarios dados en `requirements_training.txt`, la forma de ejecutar desde consola los procesos  es la siguiente:
```
python training.py
```

A continuación se describen las funciones más importantes.
 1. `random_search_optimize_histogram_sklearn`: Utiliza un *random search* para llevar a cabo una búsqueda inicial de los combinaciones de hiperparámetros de interés. La **mejor combinación** es determinada en una búsqueda posterior a este *random search*. Los parámetros que la controlan son:
   * *name_objective*: Nombre de la variable a explicar.
   * *name_stratify*: Nombre de la variable que se utilizará para hacer una división estratificada de la data entre **conjunto de prueba** y **conjunto de entrenamiento**.
    * *name_no_features*: Lista de variables que serán eliminadas después de la división entre **conjunto de prueba** y **conjunto de entrenamiento**. Por ejemplo, podría ser que una variable sea usada para el proceso de estratificación, pero no se desee que sea un **input** del modelo.
    * *name_model*: Selección del estimador. Por default se trabaja con `HistGradientBoostingRegressor`.
    * *name_data_for_regression*: Nombre de la base de datos lista y tratada para los procesos de *Entrenamiento y Optimización*.
   * *selected_features*: Lista de variables seleccionadas como **inputs** del modelo y que son las que se tomarán en cuenta en la división **entrenamiento-prueba**.
   * *vars_basic*, *vars_features*, *vars_grid*, *vars_fid*, *vars_geo*: Alternativa para seleccionar variables por medio de listas más pequeñas de nombres. La suma de estos listados equivale a *selected_features*. Si *selected_features* es `Null`, se tomará el contenido de estas listas para la selección de variables.
  * *categoric_column_names_for_target_encoder*: Lista de variables categóricas que se codificarán usando *TargetEncoder*.
   * *with_monotone_constraints*: Booleno para decidir si se incluirán restricciones de monotonía.
   * *columns_for_increasing*: Lista de variables donde se aplicarán restricciones para obtener una monotonía creciente. En caso no haber ninguna lista, su valor deberá ser `''`.
   * *columns_for_decreasing*: Lista de variables donde se aplicarán restricciones para obtener una monotonía decreciente. En caso no haber ninguna lista, su valor deberá ser `''`.
   * *random_state*: Semilla aleatoria que gobernará la división **prueba-entrenamiento** así como el proceso de optimización.
   * *test_size*: Tamaño del **conjunto de prueba**. Es una proporción del conjunto total dado por *name_data_for_regression*.
   * *hyperparameters_HGBR*: Diccionario con los valores de los hiperparámetros que formarán el grid de búsqueda.
   * *n_iter_for_search*: Número de iteraciones de búsqueda que conformará el proceso dado por *random search*.
   * *n_splits_for_cv*. Número de folds para el proceso de cross-validation.
   * *metric_for_final_search*: Métrica con base a la cual se realiza la búsqueda final. Una vez finalizado el proceso de búsqueda dado por *random search*, se ordena el historial de combinaciones de hiperparámetros de manera ascendente con base en esta métrica. Los valores disponibles son `cv_mape`  y  `cv_fugacity`.
   * *n_selections_for_final_search*: Número de combinaciones de hiperparámetros donde se hará la búsqueda final. Esta selección se hace una vez ordenado de manera ascendente con base en *metric_for_final_search*. Las combinaciones seleccionadas son pues donde se obtienen los valores más bajos de *metric_for_final_search*.
   * *metric_for_best_hyperparameters*: Métrica con la que se localizará a la mejor combinación de hiperparámetros. Esta búsqueda se hará en la selección de combinaciones de hiperparámetros hecho con base a la métrica *metric_for_final_search*, es decir, solo en un subconjunto del historial completo de combinaciones. Este subconjunto se vuelve a ordenar de manera ascendente pero ahora con base en *metric_for_best_hyperparameters*. La combinación de hiperparámetros con el más pequeño *metric_for_best_hyperparameters* dará paso al "mejor modelo". Los valores disponibles son `cv_mape`  y  `cv_fugacity`.
   * *path*: directorio que contiene tanto los **archivos-entrada** y los **archivos-salida** de los procesos de *Entrenamiento y Optimización*.

2. `fit_model`: Ajusta un modelo utilizando un diccionario con los valores de hiperparámetros resultante del proceso de optimización. Si se ejecuta después de `random_search_optimize_histogram_sklearn`, entonces ajustará al modelo ganador. Muchos de parámetros que la gobiernan tienen exactamente la misma definición que en la anterior función. A continuación, solo se ofrecerá la explicación de los parámetros exclusivos de esta función:
  * *pd_with_hyperparameters_dic*: Pandas DataFrame resultado del proceso de optimización.
  * *name_objective*: Ya explicado.
  * *name_stratify*: Ya explicado.
  * *name_no_features*: Ya explicado.
  * *name_model*: Ya explicado.
  * *name_data_for_regression*: Ya explicado.
  * *selected_features*: Ya explicado.
  * *vars_basic*, *vars_features*, *vars_grid*, *vars_fid*, *vars_geo*: Ya explicados.
  * *categoric_column_names_for_target_encoder*: Ya explicado.
  * *with_monotone_constraints*: Ya explicado.
  * *columns_for_increasing*: Ya explicado.
  * *columns_for_decreasing*: Ya explicado.
  * *random_state*: Ya explicado.
  * *test_size*: Ya explicado.
  + *n_splits_for_cv*: Ya explicado.
  + *save_model*: Booleano para guardar el modelo, y sus métrica, a través archivos `.sav`.
  * *save_train_test_sets*: Booleano para guardar los **conjuntos de entrenamiento y prueba** en archivos `.sav`.
  * *shap_feature_importances*: Booleano para poder calcular las *features importances* con base en *shap-values*, ponerlas en un Pandas DataFrame y guardarlas en un archivo `.sav`. Además, se guardan los *shap-values* para las predicciones del **conjunto de prueba** y el "explicador" que calcula estas *shap-values*.
  * *path*: Directorio en donde se guardará los **archivos-salida**.

Los valores actuales de los parámetros que gobiernan las pasadas funciones pueden consultarse en `config.yaml`.

El **archivo-entrada** esperado en los procesos de *Entrenamiento y Optimización*, el cual debe estar localizado en `suggested_price\outputs`,  esta dado por
* `data_for_regression_v5.sav`.

Los **archivos-salida**, los cuales se localizan en `suggested_price\outputs`, son:
* `optimization_history.sav`: Contiene los resultados del proceso de búsqueda vía *random_search*.
* `model_cdmx.sav`: Binario con el modelo optimizado.
* `model_metrics.sav`: Pandas DataFrame con las métricas de entrenamiento, cross-validation y de prueba del modelo optimizado.
* `data_test.sav`: Pandas DataFrame que contiene el **conjunto  de prueba**.
* `data_train.sav`: Pandas DataFrame que contiene el **conjunto de entrenamiento**.
* `encoder_cdmx.sav`: Binario con el codificador *TargetEncoder* de variables categóricas.
*`pd_feature_importances:` Pandas DataFrame que contiene las *features-importances* de las variables seleccionadas para el entrenamiento.
*`shap_values_test.sav`: Contiene las importancias para cada una de las predicciones hechas en el **conjunto de prueba**.
* `explainer.sav`: Contiene el "explicador" para calcular las contribuciones de las características en una predicción.

# __Archivos de Predicción (suggested-price\project).__
En el proceso de *Predicción*, dado una estructura `JSON` con la información suficiente, se asigna los polígonos geográficos necesarios al inmueble, además de que se recrea la ingeniería de características dada en el *Workshop*. Los scripts relacionados son:

1. __prediction.py__: Dada una estructura `JSON`, calcula el *Precio Sugerido*.  Dentro, se encuentra una función homónima la cual es la más importante.
2. __prediction_functions.py__: Contiene las funciones necesarias para llevar a cabo la predicción.

La función `prediction` es la más importante y es gobernada por los siguientes parámetros:
* *json*: Estructura `JSON` con la información básica necesaria.
* *path*: Directorio en el cual se localizan los **archivos-entrada** necesarios para la predicción.
* *with_location_variables*: Booleano para decidir si se construyen las variables de localización (`x`, `y`,`z`).
* *with_basic_relationship_variables*: Booleano para decidir si se construyen las variables de relación entre las variables básicas (`antiquity`, `covered_area`, `rooms`, `bathrooms`, `parking`).
* *with_fid_grid_variables*: Booleano para decidir si se asignan los polígonos geográficos y traer así las variables derivadas de `fid` y `grid`.
* *with_luxury_features*: Booleano para decidir se se consturyen las variables de información de características lujosas de inmuebles.

Un ejemplo de la estructura `JSON` es la siguiente:
```
{"features": {"antiquity": 14,
              "covered_area": 137,
              "rooms": 3,
              "bathrooms": 2,
              "parking": 2},
 "location": {"latitude": 19.4356,
              "longitude": -99.2041},
 "amenities": {"has_service_room": false,
                   "has_terrace": true,
                   "has_garden": false,
                   "has_elevator": false,
                   "has_full_kitchen": true,
                   "has_furniture": false,
                   "has_swimming_pool": false,
                   "has_gym": false,
                   "has_private_security": false,
                   "has_jacuzzi": false}}
```

Previo a instalar los requerimientos necesarios  dados en `requirements_prediction.txt`, la manera de obtener una predicción, en consola, es la siguiente:
```
>>> import json
>>> with open('example.json', 'r') as f: json_s = json.load(f)
>>> from prediction import prediction
>>> prediction(json=json_s, path="../outputs", with_location_variables=True, with_basic_relationship_variables=True, with_fid_grid_variables=True, with_luxury_features=True)
```
El resultado de esto, es una estructura `JSON` como la siguiente:

```
{'min': 29800.0,
 'mid': 35000.0,
 'max': 40300.0,
 'original_prediction': 35021.25,
 'version': '5.0'}
 ```
donde:
* `min`: Es el *Precio Mínimo* redondeado a la centena más próxima.
* `mid`: Es el *Precio Sugerido* redondeado a la centena más próxima.
* `max`: Es el *Precio Máximo* redondeado a la centena más próxima.
* `original_prediction`: Es la predicción real redondeada.
* `version`: Es la versión del proyecto.

En caso de que el inmueble esté fuera de Ciudad de México, es decir, en otro estado de la república o en otro país, entonces la función devolvera `None`.

En `suggested-price\project` se pueden encontrar más ejemplos de `JSON` de entrada para esta función de predicción.
* `example.json`, `example_2.json`: ejemplos en Ciudad de México.
* `example_no_cdmx.json`: ejemplo que se encuentra en Quintana Roo.
* `example_no_mexico.json`: ejemplo ubicado en Europa.

Los **archivos-entrada**, es decir, los archivos necesarios para obtener una predicción, los cuales están localizados en `suggested-price\outputs`, son:
* `grid_data_complete.sav`: el archivo con las variables de `grid`.
* `cadastral_data_fid.sav`: el archivos con las variables de `fid`.
* `colonias_df.sav`: Ya explicado.
* `fids_not_used.sav`: Ya explicado.
* `grid_ids_not_used.sav`: Ya explicado.
* `neigh_ids_not_used.sav`: Ya explicado.
* `grid_objectids_not_used.sav`: Ya explicado.
* `encoder_cdmx.sav`: Ya explicado.
* `model_cdmx.sav`: Ya explicado.

El aumentar o reducir variables a la predicción es posible manipulando las listas de nombres de variables dados en `config.yaml`.


# __Despliegue del modelo.__
## Requerimientos para pruebas locales e implementación

Para poder correr las pruebas locales e implementar la API en AWS necesitamos contar en nuestro equipo con la siguiente lista de software de linea de comandos:

- sam-cli
    - [Linux](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install-linux.html)
    - [Mac](https://docs.aws.amazon.com/es_es/serverless-application-model/latest/developerguide/serverless-sam-cli-install-mac.html)(si ya se cuenta con homebrew usar solamente el comando ```brew install aws-sam-cli```)
- aws-cli
    - [Linux](https://docs.aws.amazon.com/es_es/cli/latest/userguide/install-cliv2-linux.html)
    - En Mac usando el comando ```brew install awscli``` o visitar la [documentación](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-mac.html) de AWS para un método alternativo
- docker
   - En linux visite el siguiente [articulo](https://www.digitalocean.com/community/tutorials/how-to-install-and-use-docker-on-ubuntu-20-04) de DigitalOcean para la instalación o visite la [documentación](https://docs.docker.com/engine/install/ubuntu/) oficial de docker.
   - En mac visite la [pagina](https://docs.docker.com/docker-for-mac/install/) oficial

Nota Importante: También es necesario tener un usuario que tenga acceso mediante programación a AWS con los permisos adecuados para poder implementar la API. Este usuario necesita acceso a ECR, CloudFormation, S3 y Lambda.

## Como probar el microservicio a nivel local.

Genere la aplicación usando el comando
```
sam build --use-container
```
Lo que este comando realizara sera crear una imagen de docker basado en el dockerfile de la ruta `project/Dockerfile`.

## Probar la función de invocación con un evento de prueba

Probar la función con un evento de prueba. Un evento es un documento `JSON` que representa la entrada que recibe la función del origin del evento. Los eventos de prueba se encuentran en la carpeta events.

Para realizar esta prueba debemos ejecutar el comando:
 ```
sam local invoke SuggestedPriceV5Function --event events/event.json --env-vars environments.json
 ```
El resultado deberá ser una salida con la predicción del modelo más unas métricas de desempeño relacionado con el tiempo que la API tardó en procesar y responder a esta petición.

## Simular la API en un contenedor local

SAM CLI también puede emular la API de su aplicación. Utilice
```
sam local start-api --env-vars environments.json
```
para ejecutar la API localmente en el puerto 3000.

## Como probar el microservicio usando Postman

Ingrese el URL en la barra de request URL y seleccione método POST ![url_post](images/url_post.png)

En la parte de Headers indique la opción 'x-api-key' en la casilla de KEY y coloque el token proporcionada por el equipo de Data Science.
![pos2](images/xapikey.png)

Finalmente en la parte de Body ingrese uno de los ejemplos de payload (`example.json` o `example_2.json`) encontrados en `\project` seleccionando las opciones *raw* y *JSON*.

![pos3](images/raw_json_options.png)

Una vez hecho esto, de click en *SEND*. La respuesta se verá como lo siguiente:

![pos3](images/salida_postman.png)

## Pruebas unitarias

Las pruebas se definen en la carpeta `\test` de este proyecto. Las pruebas se corren sobre un contenedor con un Dockerfile diferente al usado en `\project`. Podemos ejecutar los siguientes comandos para lanzar las pruebas:

```
docker build . -f tests/Dockerfile -t suggested_price_model:tests
```

```
docker run -v ${HOME}/.aws:/root/.aws:ro --rm suggested_price_model:tests python -m pytest tests/unit/test_handler.py -v
```

Nota: Asegurarse de tener el archivo ```~/.aws/credentials``` y ```~/.aws/config``` en el equipo local.

## Implementación

Para llevar a cabo la implementación se hará uso de la instancia EC2 llamada ```datascience-team-deployer```. Para conectarse a esta instancia deberá tener configurados el archivo config y el IdentityFile proporcionado por el equipo de datascience. Una vez listos estos archivos la conexión sería vía ssh:

```
ssh deployer-datascience
```

Dentro de la instancia actualizar el repo ```suggested-price```. Luego de cambiarse al directorio del repositorio, ejecutar el script ```deploy.sh```.


El script ```deploy.sh``` solo deberá ejecutarse cuando el código de la aplicación ha tenido algún cambio, puesto que los archivos ```.sav``` importantes para la predición deberán actualizarse de otra forma que depende del bucket S3.

Por defecto el script implementa la aplicación en modo ```dev```. Para la implementación en modo desarrollo o producción ejecutar de la siguiente forma el script:

```./deploy``` modo desarrollo

```./deploy prod``` modo producción

## Limpieza

Para eliminar los recursos creados por el script debera ejecutar el siguiente comando:

```aws cloudformation delete-stack --stack-name SuggestedPriceV5Function-dev``` si la implementación fue en modo desarrollo.

```aws cloudformation delete-stack --stack-name SuggestedPriceV5Function-prod``` si la implementación fue en modo producción.

Los buckets creados por el script deberan eliminarse de manera individual debido a que antes de eliminar un bucket hay que vaciarlo.
