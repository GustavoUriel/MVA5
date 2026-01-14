Create a ENTITY that includes all the possible results.

## Initialize the results entity
Add to the ENTITY.CONFIG the config file

## import the three datasets
Add to the ENTITY.DATASETS the three datasets 

## new dataset with renaming of metadata columns. set in the dataset el título de lo que es o va a ser.
add to the ENTITY.TRANSLATIONS the translation of columns names

## removal of unselected metadata columns from dataset

## calculation of taxonomy data to the selected time

## merging of taxonomy data to dataset

## Keep only the edges from dataset
add to ENTITY.PATIENTS the amount of patients

## Try to cure the data, each column with its method
Add to ENTITY.RECORDS_CURED a dictionary of modifications

## Remove records with invalid data that could not be cured
Add to ENTITY.RECORDS_REMOVED all removed records and reason

## Remove columns that are constant to all patients
Add to the ENTITY.COLUMNS_REMOVED all removed columns names and reason

## Filtrado técnico inicial
Antes de cualquier análisis, aplicá filtros básicos para limpiar el dataset:
• 	Presencia mínima: eliminá taxones que aparecen en menos del 10–20% de los pacientes. ??? preguntar en config
• 	Abundancia mínima: descartá taxones con conteos muy bajos (por ejemplo, menos de 5 en promedio). ??? preguntar en config
• 	Varianza: eliminá taxones con varianza casi nula (no aportan información). ??? Preguntar en config: no hacer nada, porcentual o absoluta?
Add to the ENTITY.COLUMNS_REMOVED all removed columns names and reason

## Hacer scaling:
CLR (Centered Log-Ratio) para variables taxonómicas
Z-score (estandarización) para variables clínicas. (Las variables binarias no se escalan: se dejan como 0/1.)
Add to the ENTITY.SCALED a flag with the results of scaling, if apply

## stratifications: hasta 2 divisiones de n-stratos.
calcular la calificación para los stratos y generar (n-st1+1 (sin estratificar)) * n-(st2+1 (sin estratificar)) +1 (sin estratificar) datasets. En cada dataset modificar el título de lo que es. Ej, por disease_characteristics (4 stratos) y genomic_risk_profile (4 stratos), son un total de 26 estudios comparativos.
Create one instance of ENTITY.ANALYSIS[] for each strato
Add to ENTITY.ANALYSIS[].DATASET.CONFIG the config of the analysis

## Por cada dataset:

## Offer to do a visual representation of patterns
🔹 UMAP (Uniform Manifold Approximation and Projection)
• 	Similar a PCA pero no lineal.
• 	Captura mejor agrupamientos complejos.
• 	Muy usado en microbioma, transcriptómica, citometría.
¿Qué puedes ver?
• 	Si los pacientes con PFS alto/bajo forman grupos distintos → hay señal biológica.
• 	Si están mezclados → tal vez los taxones no explican bien el PFS.
Add to the ENTITY.ANALYSIS[].VISUALIZATION a png instance for each of those

## Eliminar las variables de alta correlación. 
Usando el score para decidir qué variable conservar
Add to ENTITY.ANALYSIS[].RECORDS_REMOVED all removed records and reason

## calculation Cox univariado with p>0.05
	Regresión de Cox univariada: si PFS está censurado (es decir, algunos pacientes no han progresado aún), usas modelos de supervivencia:
• 	Para cada taxón, haces un modelo de Cox:
• 	Obtienes un valor de p para cada taxón.
• 	Seleccionas los taxones con p < 0.05 como candidatos para el modelo multivariado.

## Verificar y seleccionar taxones para el estudio con PLS-DA
¿Para qué usarías PLS-DA?
PLS-DA es una técnica que reduce la dimensionalidad de tus datos mientras intenta separar grupos. En tu caso, esos grupos serían los pacientes con PFS alto vs PFS bajo.
Lo usarías para:
• 	Visualizar si hay señal biológica en tus datos taxonómicos.
• 	Explorar si los taxones discriminan bien entre pacientes con buen y mal pronóstico.
• 	Identificar qué taxones contribuyen más a esa separación.

📦 ¿Qué te entrega PLS-DA?
1. Componentes latentes
• 	Reduce tus 6000 taxones a 2 o 3 componentes que resumen la variación más relevante para separar los grupos.
• 	Te permite graficar a los pacientes en un plano 2D y ver si los grupos se separan.
2. Gráfico de dispersión (score plot)
• 	Cada punto es un paciente.
• 	Si los pacientes con PFS alto y bajo se agrupan en zonas distintas → tus datos tienen poder discriminativo.
3. Importancia de variables (loadings)
• 	Te dice qué taxones están más asociados con cada componente.
• 	Puedes identificar los taxones que más contribuyen a separar los grupos.
4. Validación cruzada
• 	Puedes evaluar si el modelo realmente discrimina bien o si es solo ruido.
• 	Se calcula el error de clasificación y métricas como R² y Q².

🧬 Ejemplo aplicado a tu estudio
Supongamos que tienes 30 pacientes extremos (15 con PFS alto, 15 con PFS bajo) y 6000 taxones:
• 	PLS-DA reduce esos 6000 taxones a 2 componentes.
• 	Te muestra si los pacientes con PFS alto se agrupan en un lado del gráfico y los de PFS bajo en otro.
• 	Te entrega una lista de taxones que están más asociados con cada grupo.
• 	Si el modelo tiene buen rendimiento, puedes usar esos taxones como candidatos para modelos más complejos (como Random Forest o Cox penalizado).

🧠 ¿Por qué es útil en esta etapa?
Porque no necesitas asumir relaciones lineales ni construir modelos predictivos aún. PLS-DA te ayuda a:
• 	Explorar si hay estructura en tus datos.
• 	Visualizar agrupamientos.
• 	Filtrar variables relevantes.
• 	Justificar el siguiente paso del análisis.

¿Qué implica “buen rendimiento”?
En PLS-DA, el rendimiento se evalúa con métricas como:
• 	Error de clasificación bajo: el modelo predice correctamente si un paciente está en el grupo de PFS alto o bajo.
• 	R² y Q² altos: indican que el modelo explica bien la variabilidad y tiene poder predictivo.
• 	Separación clara en el gráfico: los grupos se ven distintos en el espacio reducido.
Si ves esto, significa que hay señal en tus datos.

🧬 ¿Qué significa “usar esos taxones como candidatos”?
PLS-DA te entrega una lista de taxones que tienen mayor peso en los componentes que separan los grupos. Esos taxones:
• 	Son los que más diferencian a los pacientes con PFS alto vs bajo.
• 	Pueden tener valor biológico (por ejemplo, estar relacionados con inflamación, inmunidad, microbioma protector).
• 	Se convierten en variables seleccionadas para modelos más complejos.

🧠 ¿Qué son esos “modelos más complejos”?
Una vez que tienes un subconjunto de taxones relevantes (por ejemplo, 50 en vez de 6000), puedes usarlos en:
• 	Random Forest: para clasificar pacientes y ver qué taxones tienen mayor importancia.
• 	Regresión de Cox penalizada (LASSO-Cox): para modelar el tiempo de PFS directamente, incluyendo censura.
• 	XGBoost: para construir un modelo predictivo más potente.

En resumen: PLS-DA te ayuda a filtrar y priorizar taxones. Si el modelo funciona bien, esos taxones se convierten en insumos valiosos para el siguiente paso del análisis, donde ya puedes construir modelos predictivos, hacer inferencias clínicas, o incluso buscar biomarcadores.

## Hacer un XGBoost para determinar las variables relevantes

## hacer una lista de las taxos resultado de Cox univariada, PLS-DA y XGBoost
Ponderar y calcular el score para seleccionar las columnas para el estudio
Add to ENTITY.ANALYSIS[].COLUMNS_RELEVANCE a matrix for each col with the relevance results for each method
??? Hacer un informe de evidencia convergente

## Seleccionar sólo las variables top score del paso previo
Add to ENTITY.ANALYSIS[].COLUMNS_REMOVED all removed columns names and reason
Add to ENTITY.ANALYSIS[].DATASET the dataset that will be used for the study

## Visualizaciones:
2. Visualizaciones clave
• 	Score plots de PLS-DA mostrando separación de grupos.
• 	Gráficos de importancia de variables en XGBoost.
• 	Kaplan-Meier o curvas de supervivencia para taxones relevantes.
Add to Add to ENTITY.ANALYSIS[].DATA_VISUALIZATION image for each of the visualizations

## Do MVA model
??? Seleccionar el método en la config.
??? Ofrecer comparar resultados de varios métodos.
Comparación de modelos de supervivencia
| Método                          | Pros                                                          | Contras                                                         | ¿Recomendado para implementar? |
|---------------------------------|---------------------------------------------------------------|-----------------------------------------------------------------|-------------------------------|
| Cox multivariado                | - Modela tiempo de PFS con censura                            | - Asume proporcionalidad de riesgos                             | ✅ Sí, como modelo explicativo principal |
|                                 | - Hazard ratios interpretables                                | - Sensible al sobreajuste con muchas variables                  |                               |
| AFT (Accelerated Failure Time)  | - Modela tiempo directamente                                  | - Requiere especificar distribución (Weibull, log-normal, etc.) | ✅ Sí, como alternativa a Cox si la proporcionalidad falla |
|                                 | - No requiere proporcionalidad                                | - Menos usado clínicamente                                      |                               |
| Log-Rank Test                   | - Simple y robusto                                            | - No ajusta por covariables                                     | ✅ Sí, para comparar grupos (ej. taxón alto vs bajo) |
|                                 | - Compara curvas de supervivencia entre grupos                | - No da efecto individual de variables                          |                               |
| RMST (Restricted Mean Surv Time)| - Interpretable clínicamente: tiempo promedio sin progresión  | - Requiere definir punto de corte                               | ✅ Sí, como complemento clínico al Cox |
|                                 | - No depende de proporcionalidad                              | - No modela covariables directamente                            |                               |
| Random Survival Forest (RSF)    | - No lineal                                                   | - Menos interpretable                                           | ✅ Sí, para exploración y predicción flexible |
|                                 | - Maneja censura y selecciona variables                       | - Requiere más muestras para estabilidad                        |                               |
| Gradient Boosting Surv Anal     | - Potente y preciso                                           | - Requiere ajuste fino                                          | ✅ Sí, para predicción avanzada si tenés suficientes datos |
|                                 | - Captura interacciones complejas                             | - Menos interpretabilidad clínica                               |                               |

• 	Cox multivariado: como modelo base para explicar qué variables afectan el tiempo de PFS.
• 	AFT: si el supuesto de proporcionalidad de riesgos no se cumple.
• 	Log-Rank y RMST: para visualización y comparación entre grupos (ej. taxón alto vs bajo).
• 	RSF y Gradient Boosting: para construir modelos predictivos más potentes y explorar relaciones no lineales.
Create one instance of ENTITY.ANALYSIS[].RESULTS[] for each result
Add to ENTITY.ANALYSIS[].RESULTS.RESULT each of the results in a standard way

## Validate MVA survival method results
| Métrica de validación             | ¿Qué evalúa?                                                  | Pros                                                                          | Contras                                                             |
|-----------------------------------|---------------------------------------------------------------|-------------------------------------------------------------------------------|---------------------------------------------------------------------|
| Concordancia (C-index)            | Capacidad del modelo para ordenar correctamente el riesgo     | - Interpretable<br>- Funciona con censura<br>- Útil para comparar modelos     | - No indica calibración<br>- Puede ser sensible a censura extrema   |
| AIC (Akaike Information Criterion)| Balance entre ajuste y complejidad del modelo                 | - Permite comparar modelos<br>- Penaliza sobreajuste                          | - No mide poder predictivo<br>- No tiene escala absoluta            |
| Curvas de supervivencia (KM)      | Visualización del tiempo de PFS por grupos                    | - Intuitivo<br>- Compatible con censura<br>- Útil para comunicar clínicamente | - No ajusta por covariables<br>- Requiere discretizar variables     |
| Log-Rank Test                     | Diferencia estadística entre curvas de supervivencia          | - Simple<br>- Robusto<br>- Compatible con censura                             | - No multivariado<br>- No mide magnitud del efecto                  |
| RMST (Restricted Mean Survival)   | Tiempo promedio sin progresión hasta un punto de corte        | - No depende de proporcionalidad<br>- Fácil de interpretar clínicamente       | - Requiere definir punto de corte<br>- No modela covariables        |
| Brier Score                       | Error de predicción en modelos de supervivencia               | - Mide precisión<br>- Compatible con censura                                  | - Menos intuitivo<br>- Depende del tiempo evaluado                  |
| Calibration Plot                  | Coincidencia entre predicción y realidad observada            | - Evalúa confiabilidad<br>- Visualmente claro                                 | - Requiere agrupación<br>- Menos usado en estudios pequeños         |    
Add to ENTITY.ANALYSIS[].RESULTS.VALIDATIONS each of the validations in a standard way
 
## Generate the final results and report 
Add the report to the entity

## Save the entity
