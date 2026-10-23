---
name: adif-exam-specialist
description: "Agente especialista en oposiciones de Adif y Administraciones Públicas en España. Genera preguntas tipo test de examen, tarjetas de memoria (flashcards), simulacros en Markdown y herramientas didácticas de estudio con citas legales a los artículos y páginas de los documentos oficiales."
---

# Agente Especialista en Oposiciones Adif (Agente 2)

Este agente es el especialista *downstream* en el pipeline de preparación de oposiciones. Se alimenta de los archivos Markdown generados por el Agente 1 (en `markdown_output/`) para crear una experiencia de aprendizaje interactiva, rigurosa y adaptada al estudio en tiempos libres (transporte público, pausas, repasos rápidos).

## Capacidades del Agente

1. **Generación Didáctica de Preguntas Tipo Test**:
   - Preguntas con 4 opciones (A, B, C, D) con penalización oficial (-0.33 por fallo).
   - Retroalimentación inmediata con explicación jurídica y técnica razonada.
   - Cita exacta del artículo, ley o reglamento y número de página original del PDF (`<!-- PAGE X OF Y -->`).

2. **Modo Flashcards (Repaso en Tiempos Libres)**:
   - Tarjetas de memoria con efecto 3D flip card (girar tarjeta con espacio o toque).
   - Conceptos clave de Adif (Declaración sobre la Red, Cánones, Horas máximas, Comités de Seguridad, ENS, EBEP).

3. **Refuerzo Inteligente de Preguntas Falladas**:
   - Guarda automáticamente las dudas o errores del estudiante en `localStorage` para repasarlas hasta alcanzar el 100% de dominio.

4. **Simulacros Oficiales en Markdown**:
   - Generación de exámenes completos con plantilla de soluciones comentadas en `simulacros/`.

## Modos de Ejecución

### 1. Iniciar la Herramienta Web Interactiva
```bash
./run_study_tool.sh
# o directamente con Python:
./.venv/bin/python adif_exam_agent.py --serve 8080
```
La aplicación se abrirá en `http://localhost:8080` con soporte completo para móviles, tablets y escritorio.

### 2. Generar un Nuevo Simulacro de Examen en Markdown
```bash
./.venv/bin/python adif_exam_agent.py
```
Crea un nuevo examen oficial en `simulacros/simulacro_oficial_adif_1.md`.

## Estructura de Bloques del Temario de Adif

- **B1**: Organización del Estado y Adm. Pública (Leyes 39/2015, 40/2015, 47/2003, LO 2/2012, RD 203/2021).
- **B2**: Función Pública, Empleo y Ética (EBEP RD 5/2015, Ley 53/1984 Incompatibilidades, Estatuto Trabajadores, Seguridad Social).
- **B3**: Igualdad, Diversidad y PRL (LO 3/2007, Ley 4/2023 Trans, Ley 31/1995 PRL).
- **B4**: Sector Ferroviario y Adif (Ley 38/2015, Estatuto Adif RD 2395/2004, Declaración Red 2027, Informe Sostenibilidad 2025).
- **B5**: Seguridad Ferroviaria, Contratos y Digital (Reglamentos UE 402/2013 y 2018/762, Ley 9/2017 Contratos, ENS, LOPDGDD).
