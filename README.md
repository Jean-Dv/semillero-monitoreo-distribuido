# Semillero de monitorización distribuida

Repositorio de trabajo para construir, de forma incremental y trazable, una propuesta de investigación sobre reconocimiento interpretable de patrones en la monitorización de sistemas distribuidos.

## Resultado actual

Los ciclos 1 a 5 consolidaron:

1. contexto macro internacional;
2. contexto micro de la detección de patrones en datos de observabilidad;
3. síntomas y causas; y
4. pronóstico si el problema persiste; y
5. una pregunta de investigación inicial;
6. un objetivo general y cuatro objetivos específicos;
7. justificación, delimitación y alcance; y
8. diez núcleos del marco teórico y veinte definiciones del marco conceptual.

El ciclo 6 prepara el borrador para la presentación de la propuesta. Reformula la pregunta sin anticipar una mejora, reduce la formulación a tres objetivos específicos, justifica la necesidad del prototipo, selecciona DSRM como única metodología general y añade un plan de trabajo. La aplicación de DSRM se detalla mediante insumos, actividades, productos y criterios de avance para sus seis fases, y se acompaña con figuras propias del problema y del ciclo metodológico. La delimitación conserva cuatro variables tecnológicas: integración multimodal, desempeño del reconocimiento de patrones, interpretabilidad y utilidad para la toma de decisiones. El alcance llega hasta un prototipo funcional experimental y una validación reproducible en sistemas controlados desplegados localmente; no comprende una implementación industrial.

No se formula una hipótesis. El problema, incluida la pregunta, se mantiene dentro de 600 palabras; alcances y limitaciones dentro de 250; la justificación dentro de 300; y el marco teórico dentro de 1500.

El corpus bibliográfico actual contiene veinticuatro documentos. A los veintidós antecedentes técnicos se añadieron las fuentes de DSRM y CRISP-ML(Q) para justificar la decisión metodológica. El método se integrará mediante una extensión para Grafana, sin atribuir a la plataforma una unificación semántica automática de métricas, registros y trazas.

## Estructura

```text
.
|-- AGENTS.md                         # memoria compacta y reglas para próximos ciclos
|-- README.md                         # guía para trabajar el proyecto
|-- docs/
|   |-- propuesta_investigacion.md    # fuente narrativa vigente del ciclo 6
|   |-- proyecto_investigacion.md     # fuente conservada del ciclo 5
|   `-- matriz_evidencia.md           # trazabilidad: afirmación, fuente y página
|-- assets/figures/                    # figuras explicativas generadas
|-- papers/                           # corpus bibliográfico original
|-- scripts/
|   |-- build_figures.py              # generación reproducible de figuras
|   `-- build_documents.py            # exportación reproducible a DOCX/PDF
`-- output/
    |-- docx/propuesta_investigacion.docx
    `-- pdf/propuesta_investigacion.pdf
```

## Flujo recomendado para editar

1. Lea `AGENTS.md` para conocer el alcance, las decisiones vigentes y la numeración bibliográfica.
2. Revise o amplíe `docs/matriz_evidencia.md` antes de añadir afirmaciones nuevas.
3. Edite `docs/propuesta_investigacion.md`.
4. Mantenga las citas IEEE entre corchetes y en orden de aparición.
5. Regenere los documentos y revise visualmente todas las páginas.
6. Compacte en `AGENTS.md` los nuevos acuerdos, fuentes y pendientes del ciclo.

## Exportar a DOCX

Requiere Python 3.10 o posterior y `python-docx`:

```powershell
python -m pip install python-docx
python scripts/build_documents.py
```

El archivo se escribe en `output/docx/propuesta_investigacion.docx`.

## Exportar también a PDF

Instale LibreOffice y asegúrese de que `soffice` esté disponible en `PATH`. Después ejecute:

```powershell
python scripts/build_documents.py --pdf
```

El PDF se escribe en `output/pdf/propuesta_investigacion.pdf`. Si el DOCX ya existe, también puede abrirlo en Word o LibreOffice y usar **Archivo > Exportar como PDF**.

## Convenciones IEEE usadas

- Citas numéricas: `[1]`, `[2]`, …, `[24]`.
- Una fuente conserva el mismo número en todo el texto.
- La lista de referencias respeta el orden de primera aparición.
- Se incluyen autores, título, publicación, volumen/número o identificador de artículo, año y DOI.
- La matriz de evidencia registra las páginas que sustentan cada afirmación.

## Incorporar un paper nuevo

1. Guárdelo en `papers/` con un nombre descriptivo: `apellido-etal-anio-tema.pdf`.
2. Registre sus datos bibliográficos y su número IEEE en `AGENTS.md`.
3. Añada a `docs/matriz_evidencia.md` únicamente los hallazgos que efectivamente utilizará.
4. Integre las citas en el texto y actualice la sección **Referencias**.
5. Regenere DOCX/PDF y compruebe que no haya referencias huérfanas ni citas sin entrada bibliográfica.

## Control de calidad antes de cerrar un ciclo

- No se añadieron cifras o contextos nacionales sin una fuente verificable.
- Los hechos reportados y las inferencias del pronóstico están diferenciados.
- La pregunta de investigación, los tres objetivos y las decisiones tecnológicas coinciden con lo registrado en `AGENTS.md`.
- El planteamiento no nombra herramientas o plataformas específicas.
- «Datos de referencia para la evaluación» y «oráculo de evaluación» se distinguen de los agentes que ejecutan tareas.
- Toda cita del texto tiene una referencia y toda referencia es citada.
- `AGENTS.md`, la matriz, el Markdown y los documentos exportados están sincronizados.
- El DOCX y el PDF fueron revisados página por página.
