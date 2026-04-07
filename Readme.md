# Base de datos jurisprudenciap penal

Este es un proyecto que facilita la consulta de la base de datos de jurisprudencia que ha recopilado el encargado del servicio de Mensaje Jurídico, que es enviado vía WhatsApp y también por correo electrónico.

El propósito es proporcionarle fuentes a la IA NoteBook Lm que le permitan arrojar informes a preguntas que se le hagan y, lo más importante, que sea capaz de devolver el número de providencia y radicado de donde saca la información.

Se hizo así porque se encontró que convertir la información enviada por Mensaje Jurídico a archivos PDF no garantizaba que NoteBook Lm devolviera de manera confiable la data del número de providencia y radicado en donde estaba la información que se le pedía, lo cual generaba dudas en la confiabilidad de la información.

Con la estructura hecha se garantiza que la información de radicados y números de providencia sea muy confiable, no exacta, pudiendo detectarse cuándo devuelve datos errados. Se garantiza sí que siempre devolverá el número de DDP correcto.

## ¿Cómo se obtiene la información de Mensaje Jurídico?

En los mensajes enviados, se resumen los temas que abordan jurisprudencias escogidas por el dueño del serivicio, las cuales envía en párrafos que tienen esta forma:

```
DDP 8536. (i) “Con el cometido de analizar la probable violación al principio de congruencia por la condena irrogada a YEISON GIOVANNY SÁNCHEZ MEJÍA, IVÁN DANIEL SÁNCHEZ MEJÍA, CARLOS ANDRÉS ROSAS SÁNCHEZ, GERMÁN EDUARDO RESTREPO SÁNCHEZ y GERARDO GUTIÉRREZ HERNÁNDEZ por el delito de lesiones personales con perturbación psíquica permanente, la Sala delineará las aristas del principio en mención, de cara al procedimiento penal abreviado, y con sustento en ello, dirimirá el caso concreto.”. (ii)  “Por lo expuesto, si después de formulada la imputación la Fiscalía advierte que pretermitió hechos jurídicamente relevantes o si, con ocasión de los actos de investigación, sobrevinieron premisas fácticas que alteran la inicial comunicación de cargos, al punto que, por afectarse el núcleo fáctico de la inicial imputación se configuran otras hipótesis delictivas, el ente acusador debe procurar su adición mediante otra audiencia preliminar ante juez de control de garantías, previo a radicar el escrito de acusación.”. (iii) “Regla que aplica, también, al procedimiento especial abreviado, pues aun cuando este no prevé la audiencia de formulación de imputación, el traslado de la acusación hace las veces de esta, según el parágrafo 4º del artículo 536 del C.P.P., como se indicó líneas atrás. Luego, para incluir nuevas aristas fácticas que generen consecuencias jurídicas no conocidas por el procesado en el acto inicial de comunicación de cargos, sin afrentar el debido proceso, en el derecho de defensa y el principio de congruencia, es menester que la Fiscalía realice otro traslado de la acusación, antes de la audiencia concentrada.”. (iv) “En ese orden, comoquiera que ambas instancias avalaron el preacuerdo por el delito de lesiones personales por perturbación psíquica permanente, sin advertir que este no fue imputado fáctica ni jurídicamente, para la Sala es clara la afectación al debido proceso y, en concreto, al principio de congruencia, ya que los acusados fueron declarados culpables por hechos que no constaron en el traslado de la acusación.”. SP042-2026. RAD 65698.

```
## Componentes de cada párrafo.

Cada párrafo se compone de lo siguiente:

1. ***Número de DDP***: Inica en 1 y en cada entrega se agregan más. Por ejemplo DDP 8356
2. Temas y subtemas. Contiene los temas que el dueño del servicio escoge. Generalmente los numera en números romanos (i, ii, iii...) y a veces dentro de alguno de esos números les coloca otros.
3. Número de la providencia: corresponde al tipo de providencia que el dueño del servicio envía. Ejemplo: SP042-2026, que es una sentencia penal.
4. Número de radicado: es el radicado que se maneja en la Corte Suprema. A veces va, a veces no.

## ¿Cómo se arma la base de datos?

Para cada DDP se extrae la información atrás señalada y se coloca en un archivo MarckDown. Para cada uno se maneja la siguiente estructura:

```
---

# PROVIDENCIA DDP NUMERO

**Número de Providencia (DDP NUMERO):** número de la providencia
**Radicación (DDP NUMERO):** número del radicado

**Lista de Temas (DDP NUMERO):**
Aquí va todo el listado de temas.

---
```

Para el ejemplo anterior se ve así:

```
---

# PROVIDENCIA DDP 8536

**Número de Providencia (DDP 8536):** SP042-2026
**Radicación (DDP 8536):** 65698

**Lista de Temas (DDP 8536):**
(i) “Con el cometido de analizar la probable violación al principio de congruencia por la condena irrogada a YEISON GIOVANNY SÁNCHEZ MEJÍA, IVÁN DANIEL SÁNCHEZ MEJÍA, CARLOS ANDRÉS ROSAS SÁNCHEZ, GERMÁN EDUARDO RESTREPO SÁNCHEZ y GERARDO GUTIÉRREZ HERNÁNDEZ por el delito de lesiones personales con perturbación psíquica permanente, la Sala delineará las aristas del principio en mención, de cara al procedimiento penal abreviado, y con sustento en ello, dirimirá el caso concreto.”. 
(ii)  “Por lo expuesto, si después de formulada la imputación la Fiscalía advierte que pretermitió hechos jurídicamente relevantes o si, con ocasión de los actos de investigación, sobrevinieron premisas fácticas que alteran la inicial comunicación de cargos, al punto que, por afectarse el núcleo fáctico de la inicial imputación se configuran otras hipótesis delictivas, el ente acusador debe procurar su adición mediante otra audiencia preliminar ante juez de control de garantías, previo a radicar el escrito de acusación.”. 
(iii) “Regla que aplica, también, al procedimiento especial abreviado, pues aun cuando este no prevé la audiencia de formulación de imputación, el traslado de la acusación hace las veces de esta, según el parágrafo 4º del artículo 536 del C.P.P., como se indicó líneas atrás. Luego, para incluir nuevas aristas fácticas que generen consecuencias jurídicas no conocidas por el procesado en el acto inicial de comunicación de cargos, sin afrentar el debido proceso, en el derecho de defensa y el principio de congruencia, es menester que la Fiscalía realice otro traslado de la acusación, antes de la audiencia concentrada.”. 
(iv) “En ese orden, comoquiera que ambas instancias avalaron el preacuerdo por el delito de lesiones personales por perturbación psíquica permanente, sin advertir que este no fue imputado fáctica ni jurídicamente, para la Sala es clara la afectación al debido proceso y, en concreto, al principio de congruencia, ya que los acusados fueron declarados culpables por hechos que no constaron en el traslado de la acusación.”.

---
```







