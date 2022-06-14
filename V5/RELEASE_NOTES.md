# **SUGGESTED PRICE V5**

**Versión**: 5.0
**Verisón previa:** 4.0
**Personas a cargo:** Miguel Uicab, Carlos Calderón, Virgilio Padrón
**Fecha de inicio:** 01 / enero / 2022
**Fecha de entrega:**  31 / mayo / 2022
**Estado:** En evolución
**Links externos:** RELEASE_NOTES Extract - Transform.
**Proyectos relacionados:** Precio Sugerido Versión 4, Extracción-Transformación de Data.


***
***
# __1. Resumen.__
Se desarrolla un nuevo algoritmo de cálculo de *Precio Sugerido*. Se toma como base la data unificada, homologada y limpia derivada de los procesos de **Extracción-Transformación**,  se aprovecha de mejor manera la información pública geoespacial a disposición, se hace una ingeniería de características más sofisticada, además del uso de data de precios del pasado.


# __2. Estado Previo.__
El *Precio Sugerido V4* innovó en su momento con las siguientes características:
* Uso del estimador `HistGradientBoostingRegressor`, la cual es una versión rápida de `GradientBoosting` implementado en `Scikit-Learn` y que compite con versiones dadas por `XGBoost` o `LightGBM`.
* Uso la `latitude` y `longitud`, transformadas, como **inputs** del modelo.
* Uso de variables relacionadas con la información de predios catastrales de la Ciudad de México.
* Uso de un polígonos propios, los cuales en conjunto reciben el nombre de `grid`, que consistía en una cuadrícula sobre la Ciudad de México. Cada celda de esta cuadrícula mide 280 m2.

Lo anterior ayudo a darle "dinamismo"
a la predicción, al considear no solo la presencia del inmueble a cierta colonia, sino su pertencia a cierto predio catastral y a cierta celda.


# __3. Metodología.__
El desarrollo de este algoritmo se ha pensado en 4 etapas:
1. __Workshop:__ Es una etapa de pos-preprocesamiento desarrollado exclusivamente para este proyecto. Se toma la data resultante de los procesos de __*Extracción-Transformación*__. Además de eso, se realiza la ingeniería de características. Los scripts asociados: `workshop.py` y `workshop.py`.
2. __Entrenamiento y Optimización:__ Se encuentra el mejor modelo vía un proceso de búsqueda de dos etapas:
  1. Obtener las *n* primeras "mejores" combinaciones de hiperparámetros que optimicen cierta métrica A.
  2.  De estas *n* combinaciones de hiperparámetros, obtener la que optimice cierta métrica B.

  Para la primera iteración de la **Versión 5**, se buscan las 100 combinaciones de hiperparámetros que minimicen el `mape de cross-validation`. Luego, sobre estas 100, se encuentra la que minimice el `fugacity de cross-validation`. Los scripts relacionados son `training.py` y `training_functions.py`.
3. __Predicción:__ Se prepara un script maestro en python que, dado una estructura `json`, asigne a la observación los polígonos geográficos de interés y reconstruya la limpieza e ingeniería de características llevadas a cabo en el **Workshop**. El resultado final es otra estructura `json` con los resultados de predicción.
Los scripts relacionados son `prediction.py` y `prediction_function.py`.
4. __Evaluación:__ Se construyen métricas para conocer el rendimiento del modelo a niveles de Ciudad de México, Alcaldías, Colonias-Top y Cluster (*en desarrollo*).
5. __Actualización:__
Si en un futuro reentrenamiento las métricas mejoran y lo hacen *significativamente*, el modelo se actualiza (*en desarrollo*).

En cuento a medir el rendimiento del modelo final, se han utilizado las siguientes métricas:
* __MAPE:__ Mean Absolute Percentage Error. Es el promedio de los siguientes errores:
* __FUGACITY:__ % de predicciones cuyo error porcentual absoluto está por arriba del 17 %.



# __4. Cambios específicos.__
### Sobre las variables.
La ingeniería de características ha sido más rigurosa y rica en esta versión. Algunas de las maneras en que se han obtenido/construido nuevas variables son:
1. Usando directamente variables con información básica. Estos son
`antiquity`, `covered_area`, `rooms`, `bathrooms`, `parking`.

2. Al relacionar las variables de básicas. Por relaciones, se entiende que se lleva a cabo operaciones de multiplicación, division, diferencia, ..., entre ellas. Las construidas de esta manera han sido:
  * `price_x_mt2`
  * `bathrooms_rooms`
  * `parking_rooms`
  * `covered_area_rooms`
  * `covered_area_bathrooms`
  * `space_utility`
  * `rooms_bathrooms_difference`
  * `rooms_parking_difference`

3. Variables obtenidas directo de las características de inmuebles como `has_furniture`, `has_service_room`, `has_gym`, etcétera. Para saber la totalidad de ellas consultar el `RELEASE_NOTES.md` del proyecto de **Extracción-Transformación**.

4. Al relacionar variables de características de inmubles. Para esta ocasión se han construido las siguientes:
  * `prescence_luxury_features`: Presencia de al menos una de las características de lujo (booleano). Estas son `has_swimming_pool`, `has_gym`, `has_private_security`, `has_jacuzzi`.
  * `perc_luxury_features`: Porcentaje de la presencia de esas características.

5. Variables derivadas de los polígonos. Se han usado los polígonos de colonia, de alcaldía, de predio catastral, y de `grid`.

6. Transformaciones a la `latitude` y `longitude`- Se transforman en `x`, `y`, `z`, para ubicar el punto en un plano cartesiano tridimensional.

7. Auxiliares para el entrenamiento.

### Variables de polígonos.

Estas variables surgen de manipular la información contenida en los polígonos. Los polígonos usados son

1. `grid_id`: Identificador de una celda del `grid`. La totalidad de variables creadas está contenida en el archivo `grid_data_complete.sav`.

![grid_cdmx](images/grid_cdmx.png)*Malla `grid` que cubre la Ciudad de México.*

2. `fid`: Identificador de predio catastral. La totalidad de variables creadas está contenida en el archivo `cadastral_data_fid.sav`.

![cadastral_cdmx](images/cadastral_cdmx.png)*Predios Catastrales de Ciudad de México.*

3. `mun_id_cdmx`: Identificador de alcaldía.
![alcaldias_cdmx](images/alcaldias_cdmx.png)*Alcaldías de la Ciudad de México.*
4. `neigh_id`: Identificador de colonia.
![neigh_cdmx](images/neigh_cdmx.png)*Colonias de la Ciudad de México.*

### Variables derivadas del historial de precios.
Aprovechando que se tiene a disposición el comportamiento de los precios de renta en el pasado, se obtiene un cluster usando las medias y desviaciones estándar de `price/coverd_area` obtenidas por colonia.

![cluster_cdmx](images/cluster_cdmx.png)*Cluster de colonias de Ciudad de México.*


# __5. Estado Actual.__
NO todas las variables construidas han quedados en las **inputs** finales del modelo. Ha habiado un filtrado de variables, previo al entrenamiento, el cual se hizo utilizando la **información mutua**. Luego, a habido un filtrado final de variables, después de entrenamiento, utilizando las importancias de las variables dadas por las **shap-values**. En el histograma de abajo, se puede ver que variables conocidas como `coverd_area`, `parking` `bathrooms`, `has_furniture`, entre otras, ocupan el top 15 de variables más importantes.
![shap_feature_importances](images/shap_feature_importances.png)*Importancias de las variables finales vía **shap-values**.*

Estas son las variables **input** finales que el estimador `HistogramGradientBosstingRegressor` utiliza en su primera versión subida a producción:

| Grupo | Nombres | Descripción  |
| ------------- | ------------- | ------------- |
| Básicas  | `antiquity`, `covered_area`, `rooms`, `bathrooms`, `parking`| Variables que se pueden obtener directo de un payload. |
| Relaciones entre las Básicas | `covered_area_rooms`, `covered_area_bathrooms`, `bathrooms_rooms`| Se construyen haciendo multiplicaciones, divisiones o potencias. Actualmente, todas con cocientes. |
| Características de Inmuebles |                   `has_service_room`, `has_terrace`,`has_garden`, `has_elevator`, `has_full_kitchen`, `has_furniture`| Se obtienen directo de un payload.|
| Derivadas de Características de Inmuebles |  `perc_luxury_features` | Se construye con base a las características de lujo de un inmueble. Estas son: `has_swimming_pool`, `has_gym`, `has_private_security`, `has_jacuzzi`.|
| Derivadas de  `grid_id` | `superficie_construida`, `superficie_total`, `valor_suelo`, `anio_media_grid`, `unidades_por_sup_contruida`, `unidades_por_sup_total`, `valor_suelo_por_unidad`, `sup_construida_sobre_sup_total`| |
| Derivadas de  `fid` | `unidades`, `antiquity_anio_media_construccion`, `suma_superficie_terreno`, `ratio_superficie_unidades`, `count_rango_nivel_min`| |
| Historial de Precios | `class_past`| |
| Localización| `x`, `y`, `z`| |
| Identificadores Geográficos | `grid_id_modified`, `fid_modified`, `mun_id_cdmx`, `neigh_id_modified`| |
| Para estratifiación | `grid_objectid_modified`| |

# __6. Cambios Generales.__
### Variables en payload
La siguiente es un comparativa de las variables que se necesitan en un payload para poder tener una predicción:

| Información | V4 | V5  |
| ------------- | ------------- | ------------- |
| Básicas  | `antiquity`, `covered_area`, `rooms`, `bathrooms`, `parking`| `antiquity`, `covered_area`, `rooms`, `bathrooms`, `parking` |
| Localización  |`latitude`, `longitude` |  `latitude`, `longitude`|
| Características de Inmuebles  | |  `has_service_room`, `has_terrace`, `has_garden`, `has_elevator`, `has_full_kitchen`, `has_furniture`, `has_swimming_pool`, `has_gym`, `has_private_security`, `has_jacuzzi`|

En cuento al rendimiento del modelo, se ofrece la siguiente tabla comparativa con respecto a la versión anterior.

| | Versión 4| Versión 5 |
|--|--|--|
| __MAPE CROSS-VALIDATION__ | 19.15% | 12.47%|
| __FUGACITY CROSS-VALIDATION__| 40 % |26% |

### Rendimiento del modelo
Un ejercicio realizado con datos de mayo de 2022, los cueles el modelo no consideró en su entrenamiento, reveleraron las siguientes métricas.

| | Versión 4| Versión 5 |
|--|--|--|
| __MAPE__ |  20.81% | 15.74% |
| __FUGACITY__|  42.96% | 33.41% |

La gráfica de abajo muestra que los errores porcentuales absolutos en la Version 5 etán más concentrados en el valor 0 que en la Versión 4.
![shap_feature_importances](images/mape_cdmx_may_2022.png)


# __7. Mejoras y planes a futuro.__
Adición de más variables derivadas de nuevas fuentes de información pública, como datos de censo, datos electorales, datos socio-demográficos, datos económicos, etcétera.

Desarrollo de modelo de predicción para los demás estados de la república.

# __8. Post-Mortem.__
Los procesos de __Evaluación__ y __Actualización__ del modelo están aún en desarrollo. Las tareas de despligue se desarrollarán de manera inicial solo para el proceso de __Predicción__.
