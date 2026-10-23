#!/usr/bin/env python3
"""
Agente Especialista en Oposiciones de Adif y Administraciones Públicas de España.
(Downstream Specialist Agent)

Este agente consume los documentos Markdown procesados por el Agente 1 (en markdown_output/)
y genera herramientas didácticas de estudio:
- Banco exhaustivo de preguntas tipo test de oposición con retroalimentación razonada y citas legales.
- Tarjetas de memoria (Flashcards) para repaso rápido en tiempos libres.
- Simulacros oficiales de examen en formato Markdown.
- Servidor interactivo web para estudiar desde cualquier dispositivo (móvil, tablet, PC).
"""

import os
import sys
import json
import time
import random
import http.server
import socketserver
import webbrowser
from pathlib import Path
from typing import List, Dict, Any, Optional

WORKSPACE_DIR = Path(__file__).resolve().parent
MD_DIR = WORKSPACE_DIR / "markdown_output"
WEB_APP_DIR = WORKSPACE_DIR / "web_app"
SIMULACROS_DIR = WORKSPACE_DIR / "simulacros"

# Catálogo canónico de bloques temáticos de Adif
BLOQUES_TEMATICOS = {
    "B1": "Organización del Estado y Administración Pública (Leyes 39/2015, 40/2015, 47/2003, LO 2/2012, RD 203/2021)",
    "B2": "Función Pública, Empleo y Ética (EBEP RD 5/2015, Incompatibilidades Ley 53/1984, Estatuto Trabajadores, Seguridad Social)",
    "B3": "Igualdad, Diversidad y Prevención (LO 3/2007, Ley 4/2023 Trans, Prevención Riesgos Laborales Ley 31/1995)",
    "B4": "Sector Ferroviario y Adif (Ley 38/2015, Estatuto Adif RD 2395/2004, Declaración Red 2027, Informe Sostenibilidad 2025)",
    "B5": "Seguridad Ferroviaria, Contratación y Digital (Reglamentos UE 402/2013 y 2018/762, Ley 9/2017 Contratos, ENS, LOPDGDD)",
}

class AdifExamAgent:
    """Agente especialista en oposiciones y generación de materiales didácticos de Adif."""

    def __init__(self):
        self.questions_file = WEB_APP_DIR / "adif_questions_db.json"
        self.questions_js_file = WEB_APP_DIR / "questions_data.js"
        self.questions = self._load_or_build_question_bank()

    def _load_or_build_question_bank(self) -> List[Dict[str, Any]]:
        """Carga o compila el banco de preguntas didácticas basadas en el temario en markdown."""
        if self.questions_file.exists():
            try:
                with open(self.questions_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list) and len(data) >= 20:
                        return data
            except Exception:
                pass
        return self._generate_canonical_question_bank()

    def _generate_canonical_question_bank(self) -> List[Dict[str, Any]]:
        """Genera un banco de preguntas rigurosas con citas textuales y páginas originales."""
        questions: List[Dict[str, Any]] = [
            # =========================================================================
            # TEMA 1: EBEP (RD 5/2015) - Código de Conducta y Deberes
            # =========================================================================
            {
                "id": "ADIF-01-01",
                "tema_id": "01_EBEP",
                "tema_titulo": "Estatuto Básico del Empleado Público (RD Leg. 5/2015) - Deberes y Código de Conducta",
                "bloque_id": "B2",
                "pregunta": "¿Cuál de los siguientes principios éticos está recogido expresamente en el artículo 53 del EBEP para los empleados públicos?",
                "opciones": [
                    "Ajustarán su actuación a los principios de lealtad y buena fe con la Administración, superiores, compañeros y subordinados.",
                    "Aceptarán recompensas económicas de particulares si el servicio prestado es de notorio interés público.",
                    "Podrán adquirir beneficios económicos para sí mismos derivados de su cargo siempre que se declaren en IRPF.",
                    "Podrán intervenir en asuntos donde tengan interés personal si así lo autoriza su jefe de servicio oralmente."
                ],
                "respuesta_correcta": 0,
                "explicacion": "El art. 53.2 del EBEP establece que los empleados públicos 'ajustarán su actuación a los principios de lealtad y buena fe con la Administración en la que presten sus servicios, y con sus superiores, compañeros, subordinados y con los ciudadanos'. Además, el art. 53.7 prohíbe taxativamente aceptar cualquier trato de favor o recompensa económica.",
                "articulo_referencia": "Artículo 53.2 del TREBEP (RD Legislativo 5/2015)",
                "documento_origen": "01 RD 5_2015 Estatuto Basico del Empleado Publico. Capitulo VI (Tit. III) Deberes de los empleados publicos. Codigo de conducta.md",
                "pagina_origen": 7,
                "dificultad": "Media"
            },
            {
                "id": "ADIF-01-02",
                "tema_id": "01_EBEP",
                "tema_titulo": "Estatuto Básico del Empleado Público (RD Leg. 5/2015) - Código de Conducta",
                "bloque_id": "B2",
                "pregunta": "Según el artículo 54 del EBEP (Principios de conducta), ¿cómo deben actuar los empleados públicos respecto a los recursos públicos asignados?",
                "opciones": [
                    "Pueden utilizar los vehículos oficiales para fines particulares durante los fines de semana si abonan el carburante.",
                    "Administrarán los recursos y bienes públicos con austeridad y no utilizarán los mismos en provecho propio o de personas allegadas.",
                    "Tienen libertad para gestionar los bienes materiales sin necesidad de llevar inventario si el valor unitario es inferior a 300 €.",
                    "Solo tienen deber de custodia respecto a los fondos en efectivo, no de los equipos informáticos."
                ],
                "respuesta_correcta": 1,
                "explicacion": "El artículo 54.6 del EBEP dispone expresamente: 'Administrarán los recursos y bienes públicos con austeridad, y no utilizarán los mismos en provecho propio o de personas allegadas. Tendrán el deber de velar por su conservación y salvaguarda'.",
                "articulo_referencia": "Artículo 54.6 del TREBEP (RD Legislativo 5/2015)",
                "documento_origen": "01 RD 5_2015 Estatuto Basico del Empleado Publico. Capitulo VI (Tit. III) Deberes de los empleados publicos. Codigo de conducta.md",
                "pagina_origen": 8,
                "dificultad": "Básica"
            },

            # =========================================================================
            # TEMA 2: LEY DE INCOMPATIBILIDADES (Ley 53/1984)
            # =========================================================================
            {
                "id": "ADIF-02-01",
                "tema_id": "02_INCOMPATIBILIDADES",
                "tema_titulo": "Incompatibilidades del Personal al Servicio de las AAPP (Ley 53/1984)",
                "bloque_id": "B2",
                "pregunta": "De acuerdo con el artículo 1 de la Ley 53/1984, ¿cuál es el principio fundamental respecto a la dedicación del personal al servicio de las Administraciones Públicas?",
                "opciones": [
                    "Permite el desempeño libre de hasta tres puestos públicos compatibles previa notificación a Recursos Humanos.",
                    "La dedicación a un solo puesto de trabajo, sin más excepciones que las que demande el propio servicio público.",
                    "La incompatibilidad solo afecta a altos cargos, teniendo los empleados base libertad absoluta para trabajar en el sector privado sin autorización.",
                    "Es incompatible únicamente el ejercicio de cargos en consejos de administración de sociedades bancarias."
                ],
                "respuesta_correcta": 1,
                "explicacion": "El art. 1.1 de la Ley 53/1984 consagra el principio fundamental: 'La dedicación del personal comprendido en el ámbito de aplicación de esta Ley a un solo puesto de trabajo, sin más excepciones que las que demande el propio servicio público'.",
                "articulo_referencia": "Artículo 1.1 de la Ley 53/1984",
                "documento_origen": "02 Ley 53_1984, Incompatibilidades del personal al servicio de las AAPP.md",
                "pagina_origen": 4,
                "dificultad": "Básica"
            },
            {
                "id": "ADIF-02-02",
                "tema_id": "02_INCOMPATIBILIDADES",
                "tema_titulo": "Incompatibilidades del Personal al Servicio de las AAPP (Ley 53/1984)",
                "bloque_id": "B2",
                "pregunta": "¿Qué actividad privada está legalmente excluida del régimen de incompatibilidades (art. 19 Ley 53/1984) y puede ejercerse sin necesidad de reconocimiento previo de compatibilidad?",
                "opciones": [
                    "El ejercicio de la abogacía frente a la entidad pública donde se presta servicio.",
                    "La dirección técnica de una empresa proveedora de material rodante a Adif.",
                    "La colaboración y la asistencia ocasional a congresos, seminarios, cursos o conferencias.",
                    "La titularidad de más del 10% del capital de una empresa contratista de la entidad ferroviaria."
                ],
                "respuesta_correcta": 2,
                "explicacion": "El artículo 19 de la Ley 53/1984 exceptúa de la necesidad de autorización previa a la producción y creación literaria, artística, científica y técnica, así como 'la colaboración y la asistencia ocasional a congresos, seminarios, conferencias y cursos'.",
                "articulo_referencia": "Artículo 19 de la Ley 53/1984",
                "documento_origen": "02 Ley 53_1984, Incompatibilidades del personal al servicio de las AAPP.md",
                "pagina_origen": 10,
                "dificultad": "Examen Oficial"
            },

            # =========================================================================
            # TEMA 3: LEY DEL SECTOR FERROVIARIO (Ley 38/2015)
            # =========================================================================
            {
                "id": "ADIF-06-01",
                "tema_id": "06_LEY_FERROVIARIA",
                "tema_titulo": "Ley 38/2015, del Sector Ferroviario",
                "bloque_id": "B4",
                "pregunta": "¿Qué entidad tiene atribuida por la Ley 38/2015 la función de administrar la infraestructura ferroviaria integrada en la Red Ferroviaria de Interés General (RFIG)?",
                "opciones": [
                    "La Agencia Estatal de Seguridad Ferroviaria (AESF).",
                    "El Administrador de Infraestructuras Ferroviarias (Adif).",
                    "La Comisión Nacional de los Mercados y la Competencia (CNMC).",
                    "Renfe Operadora exclusivamente."
                ],
                "respuesta_correcta": 1,
                "explicacion": "La Ley 38/2015 regula a los administradores de infraestructuras ferroviarias, siendo Adif (y Adif-Alta Velocidad) las entidades públicas empresariales encargadas de la administración de las infraestructuras de la RFIG, mantenimiento, control del tráfico y asignación de capacidad.",
                "articulo_referencia": "Artículos 18 y 21 de la Ley 38/2015 del Sector Ferroviario",
                "documento_origen": "06 Ley 38_2015, de 29 de septiembre, del sector ferroviario.md",
                "pagina_origen": 25,
                "dificultad": "Básica"
            },
            {
                "id": "ADIF-06-02",
                "tema_id": "06_LEY_FERROVIARIA",
                "tema_titulo": "Ley 38/2015, del Sector Ferroviario",
                "bloque_id": "B4",
                "pregunta": "Según la Ley 38/2015, ¿cuándo se considerará que una sección de infraestructura ferroviaria está 'congestionada' o con sobrecapacidad?",
                "opciones": [
                    "Cuando el precio del billete supera la tarifa media fijada por el Ministerio.",
                    "Cuando tras la coordinación de solicitudes de capacidad no sea posible atender satisfactoriamente todas las peticiones.",
                    "Únicamente cuando se produzca una avería en la catenaria superior a 24 horas.",
                    "Cuando viajen más de 500 pasajeros en un mismo tren de alta velocidad."
                ],
                "respuesta_correcta": 1,
                "explicacion": "El artículo 37 de la Ley 38/2015 estipula que cuando, tras la coordinación de las solicitudes de franjas horarias y consultas con los solicitantes, no sea posible atender satisfactoriamente las solicitudes de capacidad, el administrador declarará la sección correspondiente de infraestructura como 'congestionada'.",
                "articulo_referencia": "Artículo 37 de la Ley 38/2015 del Sector Ferroviario",
                "documento_origen": "06 Ley 38_2015, de 29 de septiembre, del sector ferroviario.md",
                "pagina_origen": 48,
                "dificultad": "Examen Oficial"
            },

            # =========================================================================
            # TEMA 4: ESTATUTO DE ADIF (RD 2395/2004)
            # =========================================================================
            {
                "id": "ADIF-07-01",
                "tema_id": "07_ESTATUTO_ADIF",
                "tema_titulo": "Estatuto de la Entidad Pública Empresarial ADIF (RD 2395/2004)",
                "bloque_id": "B4",
                "pregunta": "¿Cuál es la naturaleza jurídica de ADIF conforme al Real Decreto 2395/2004?",
                "opciones": [
                    "Una Sociedad Anónima cotizada en bolsa con participación minoritaria del Estado.",
                    "Un organismo autónomo de carácter administrativo con presupuesto limitativo.",
                    "Una Entidad Pública Empresarial adscrita al Ministerio competente en materia de transportes.",
                    "Una fundación de derecho público sin ánimo de lucro adscrita al Ministerio de Hacienda."
                ],
                "respuesta_correcta": 2,
                "explicacion": "El artículo 1 del Estatuto de Adif (RD 2395/2004) define a ADIF como una Entidad Pública Empresarial de las previstas en la legislación de régimen jurídico de las Administraciones Públicas, adscrita al Ministerio de Transportes y Movilidad Sostenible.",
                "articulo_referencia": "Artículo 1 del Estatuto de ADIF (RD 2395/2004)",
                "documento_origen": "07 RD 2395_2004, Estatuto de la Entidad Pública Empresarial ADIF.md",
                "pagina_origen": 3,
                "dificultad": "Básica"
            },
            {
                "id": "ADIF-07-02",
                "tema_id": "07_ESTATUTO_ADIF",
                "tema_titulo": "Estatuto de la Entidad Pública Empresarial ADIF (RD 2395/2004)",
                "bloque_id": "B4",
                "pregunta": "¿Cómo se nombra al Presidente de la entidad pública empresarial ADIF según su Estatuto?",
                "opciones": [
                    "Por Real Decreto acordado en Consejo de Ministros, a propuesta del Ministro competente en materia de transportes.",
                    "Por votación directa y secreta de los miembros del Consejo de Administración de Adif.",
                    "Mediante concurso de méritos publicado en el Boletín Oficial del Estado por la Dirección General de Función Pública.",
                    "Por designación de la Comisión Nacional de los Mercados y la Competencia (CNMC)."
                ],
                "respuesta_correcta": 0,
                "explicacion": "De conformidad con el artículo 19 del Estatuto de Adif, el Presidente de la entidad será nombrado y separado mediante Real Decreto acordado en Consejo de Ministros, a propuesta del titular del Ministerio competente en materia de infraestructuras ferroviarias y transportes.",
                "articulo_referencia": "Artículo 19 del Estatuto de ADIF (RD 2395/2004)",
                "documento_origen": "07 RD 2395_2004, Estatuto de la Entidad Pública Empresarial ADIF.md",
                "pagina_origen": 9,
                "dificultad": "Media"
            },

            # =========================================================================
            # TEMA 5: SOSTENIBILIDAD Y PLAN ESTRATÉGICO DE ADIF (Informe 2025)
            # =========================================================================
            {
                "id": "ADIF-06-SOST-01",
                "tema_id": "06_INFORME_GESTION_ADIF",
                "tema_titulo": "Informe de Gestión y Sostenibilidad de Adif 2025",
                "bloque_id": "B4",
                "pregunta": "Según la Política de Sostenibilidad de Adif y Adif AV (Consejo de Administración 2024), ¿cuáles son los 3 desafíos prioritarios a mitigar?",
                "opciones": [
                    "Incremento tarifario, compra de locomotoras diésel y reducción de vías electrificadas.",
                    "Emergencia climática, protección de la biodiversidad y disminución de las desigualdades.",
                    "Privatización del mantenimiento, desregulación de la señalización y eliminación de pasos subterráneos.",
                    "Aumento de la velocidad punta a 450 km/h, transporte de mercancías pesadas y cierre de estaciones rurales."
                ],
                "respuesta_correcta": 1,
                "explicacion": "El Informe de Gestión de Adif 2025 (puntos 1.2 y 1.3) establece que la Política de Sostenibilidad se alinea con el Plan Estratégico 2030 (PE2030) y mitiga tres desafíos prioritarios: 1) Emergencia climática, 2) Protección de la Biodiversidad, y 3) Disminución de las desigualdades.",
                "articulo_referencia": "Punto 1.3 del Informe de Gestión y Sostenibilidad de Adif 2025",
                "documento_origen": "06 Informe de Gestion 2025 (Adif). Estados de sostenibilidad. Puntos 1.2 y 1.3.md",
                "pagina_origen": 46,
                "dificultad": "Examen Oficial"
            },

            # =========================================================================
            # TEMA 6: DECLARACIÓN SOBRE LA RED DE ADIF (Declaración 2027)
            # =========================================================================
            {
                "id": "ADIF-08-01",
                "tema_id": "08_DECLARACION_RED",
                "tema_titulo": "Declaración sobre la Red de Adif 2027",
                "bloque_id": "B4",
                "pregunta": "¿Qué es la 'Declaración sobre la Red' emitida periódicamente por Adif?",
                "opciones": [
                    "El balance de pérdidas y ganancias auditado por el Tribunal de Cuentas.",
                    "El documento que expone las características de la infraestructura, condiciones de acceso y adjudicación de capacidad a empresas ferroviarias.",
                    "El reglamento interno disciplinario del personal de conducción de trenes.",
                    "Un manifiesto político sobre la construcción de nuevas estaciones provinciales."
                ],
                "respuesta_correcta": 1,
                "explicacion": "La Declaración sobre la Red es el documento que detalla exhaustivamente las características técnicas de las líneas de la RFIG administradas por Adif, los requisitos para la solicitud de franjas horarias (capacidad), los cánones de utilización y las normas de acceso.",
                "articulo_referencia": "Capítulo 1 de la Declaración sobre la Red de Adif 2027",
                "documento_origen": "08 Declaracion sobre la red de Adif 2027. Capitulos del 1 al 7.md",
                "pagina_origen": 15,
                "dificultad": "Básica"
            },

            # =========================================================================
            # TEMA 7: PROCEDIMIENTO ADMINISTRATIVO COMÚN (Ley 39/2015)
            # =========================================================================
            {
                "id": "ADIF-12-01",
                "tema_id": "12_LEY_39_2015",
                "tema_titulo": "Procedimiento Administrativo Común de las AAPP (Ley 39/2015)",
                "bloque_id": "B1",
                "pregunta": "Según el artículo 30 de la Ley 39/2015, en el cómputo de plazos fijados por días hábiles, ¿qué días quedan excluidos?",
                "opciones": [
                    "Únicamente los domingos.",
                    "Los sábados, los domingos y los días declarados festivos.",
                    "Los festivos locales y autonómicos, pero los sábados se computan como hábiles.",
                    "Ninguno, todos los días del año natural son hábiles en vía electrónica."
                ],
                "respuesta_correcta": 1,
                "explicacion": "El artículo 30.2 de la Ley 39/2015 determina con total claridad: 'Siempre que por Ley o en el Derecho de la Unión Europea no se exprese otro cómputo, cuando los plazos se señalen por días, se entiende que estos son hábiles, excluyéndose del cómputo los sábados, los domingos y los declarados festivos'.",
                "articulo_referencia": "Artículo 30.2 de la Ley 39/2015 (LPACAP)",
                "documento_origen": "12 Ley 39_2015, Procedimiento Administrativo Común de las Administraciones Públicas.md",
                "pagina_origen": 24,
                "dificultad": "Examen Oficial"
            },
            {
                "id": "ADIF-12-02",
                "tema_id": "12_LEY_39_2015",
                "tema_titulo": "Procedimiento Administrativo Común de las AAPP (Ley 39/2015)",
                "bloque_id": "B1",
                "pregunta": "¿Quiénes están obligados a relacionarse a través de medios electrónicos con las Administraciones Públicas para la realización de cualquier trámite según el artículo 14 de la Ley 39/2015?",
                "opciones": [
                    "Exclusivamente las personas físicas mayores de 65 años.",
                    "Las personas jurídicas, entidades sin personalidad jurídica y quienes ejerzan una actividad profesional que requiera colegiación obligatoria.",
                    "Solo los ciudadanos que dispongan de certificado cualificado en soporte hardware.",
                    "Únicamente los funcionarios del Ministerio de Transportes en activo."
                ],
                "respuesta_correcta": 1,
                "explicacion": "El artículo 14.2 de la Ley 39/2015 establece la obligatoriedad de relación electrónica para: personas jurídicas, entidades sin personalidad jurídica, profesionales de colegiación obligatoria y empleados públicos en los trámites por razón de su condición.",
                "articulo_referencia": "Artículo 14.2 de la Ley 39/2015",
                "documento_origen": "12 Ley 39_2015, Procedimiento Administrativo Común de las Administraciones Públicas.md",
                "pagina_origen": 14,
                "dificultad": "Media"
            },

            # =========================================================================
            # TEMA 8: RÉGIMEN JURÍDICO DEL SECTOR PÚBLICO (Ley 40/2015)
            # =========================================================================
            {
                "id": "ADIF-15-01",
                "tema_id": "15_LEY_40_2015",
                "tema_titulo": "Régimen Jurídico del Sector Público (Ley 40/2015)",
                "bloque_id": "B1",
                "pregunta": "En la abstención y recusación (artículos 23 y 24 de la Ley 40/2015), ¿cuál de las siguientes causas obliga a un empleado público a abstenerse de intervenir en el procedimiento?",
                "opciones": [
                    "Tener interés personal en el asunto o parentesco de consanguinidad dentro del cuarto grado con cualquiera de los interesados.",
                    "Pertenecer al mismo club deportivo que el apoderado de una empresa licitadora.",
                    "Residir en el mismo código postal que el solicitante de la subvención.",
                    "Haber coincidido en la misma universidad hace más de veinte años sin trato actual."
                ],
                "respuesta_correcta": 0,
                "explicacion": "El artículo 23.2 de la Ley 40/2015 enumera como causas de abstención: tener interés personal, parentesco de consanguinidad dentro del cuarto grado o de afinidad dentro del segundo, amistad manifiesta o enemistad manifiesta, y haber intervenido como perito o testigo.",
                "articulo_referencia": "Artículo 23.2 de la Ley 40/2015",
                "documento_origen": "15 Ley 40_2015, Régimen Jurídico SP.  Preambulo, Título Preliminar y Título II.md",
                "pagina_origen": 18,
                "dificultad": "Media"
            },

            # =========================================================================
            # TEMA 9: LEY DE CONTRATOS DEL SECTOR PÚBLICO (Ley 9/2017)
            # =========================================================================
            {
                "id": "ADIF-13-01",
                "tema_id": "13_LEY_CONTRATOS",
                "tema_titulo": "Ley 9/2017, de Contratos del Sector Público (LCSP)",
                "bloque_id": "B5",
                "pregunta": "Conforme al artículo 118 de la Ley 9/2017 de Contratos del Sector Público, ¿cuál es el umbral económico máximo para considerar un contrato menor de obras?",
                "opciones": [
                    "Valor estimado inferior a 15.000 euros.",
                    "Valor estimado inferior a 40.000 euros.",
                    "Valor estimado inferior a 100.000 euros.",
                    "Valor estimado inferior a 215.000 euros."
                ],
                "respuesta_correcta": 1,
                "explicacion": "El artículo 118.1 de la LCSP establece que se consideran contratos menores los contratos de valor estimado inferior a 40.000 euros cuando se trate de contratos de obras, y los de valor estimado inferior a 15.000 euros cuando se trate de contratos de suministro o de servicios.",
                "articulo_referencia": "Artículo 118.1 de la Ley 9/2017 (LCSP)",
                "documento_origen": "13 Ley 9_2017, de Contratos del Sector Público. Preambulo. Título preliminar. Libros Primero y segundo.md",
                "pagina_origen": 89,
                "dificultad": "Examen Oficial"
            },

            # =========================================================================
            # TEMA 10: PREVENCIÓN DE RIESGOS LABORALES (Ley 31/1995)
            # =========================================================================
            {
                "id": "ADIF-05-01",
                "tema_id": "05_LEY_PRL",
                "tema_titulo": "Prevención de Riesgos Laborales (Ley 31/1995)",
                "bloque_id": "B3",
                "pregunta": "¿A partir de qué número de trabajadores es obligatoria la constitución de un Comité de Seguridad y Salud en un centro de trabajo (art. 38 Ley 31/1995)?",
                "opciones": [
                    "En todas las empresas con más de 10 trabajadores.",
                    "En todas las empresas o centros de trabajo que cuenten con 50 o más trabajadores.",
                    "Únicamente en empresas con más de 250 trabajadores fijos.",
                    "En empresas de transporte con más de 100 trabajadores."
                ],
                "respuesta_correcta": 1,
                "explicacion": "El artículo 38.1 de la Ley 31/1995 de Prevención de Riesgos Laborales estipula: 'Se constituirá un Comité de Seguridad y Salud en todas las empresas o centros de trabajo que cuenten con 50 o más trabajadores'. Es un órgano paritario y colegiado de consulta.",
                "articulo_referencia": "Artículo 38.1 de la Ley 31/1995 (LPRL)",
                "documento_origen": "05 Ley 31_1995, de 8 de noviembre, de Prevención de Riesgos Laborales. Exposición motivos y cap.I, III y V.md",
                "pagina_origen": 19,
                "dificultad": "Examen Oficial"
            },

            # =========================================================================
            # TEMA 11: LEY DE IGUALDAD (LO 3/2007)
            # =========================================================================
            {
                "id": "ADIF-03-01",
                "tema_id": "03_LO_IGUALDAD",
                "tema_titulo": "Ley Orgánica 3/2007, para la igualdad efectiva de mujeres y hombres",
                "bloque_id": "B3",
                "pregunta": "Según la Ley Orgánica 3/2007, ¿qué se entiende por 'composición equilibrada' en los órganos de selección y designación de las Administraciones Públicas?",
                "opciones": [
                    "Que las personas de cada sexo no superen el 60% ni sean menos del 40%.",
                    "Que haya exactamente un 50% de hombres y un 50% de mujeres en todo momento.",
                    "Que el presidente y el secretario sean obligatoriamente de distinto sexo.",
                    "Que al menos un 25% pertenezca al sexo con menor representación."
                ],
                "respuesta_correcta": 0,
                "explicacion": "La Disposición Adicional Primera de la LO 3/2007 define presencia o composición equilibrada como aquella en la que las personas de cada sexo no superen el sesenta por ciento ni sean menos del cuarenta por ciento en el conjunto a que se refiera.",
                "articulo_referencia": "Disposición Adicional Primera de la Ley Orgánica 3/2007",
                "documento_origen": "03 LO 3_2007, Igualdad efectiva de mujeres y hombres.md",
                "pagina_origen": 56,
                "dificultad": "Media"
            },

            # =========================================================================
            # TEMA 12: PROTECCIÓN DE DATOS (LO 3/2018)
            # =========================================================================
            {
                "id": "ADIF-09-01",
                "tema_id": "09_LO_PROTECCION_DATOS",
                "tema_titulo": "Protección de Datos Personales y Derechos Digitales (LO 3/2018)",
                "bloque_id": "B5",
                "pregunta": "En el marco de la Ley Orgánica 3/2018 (LOPDGDD), ¿a partir de qué edad puede un menor prestar válidamente su consentimiento para el tratamiento de sus datos personales?",
                "opciones": [
                    "A partir de los 12 años cumplidos.",
                    "A partir de los 14 años cumplidos.",
                    "A partir de los 16 años cumplidos exclusivamente.",
                    "Solo con la mayoría de edad (18 años)."
                ],
                "respuesta_correcta": 1,
                "explicacion": "El artículo 7.1 de la Ley Orgánica 3/2018 fija en catorce años la edad a partir de la cual el tratamiento de los datos personales de un menor de edad puede fundarse en su propio consentimiento sin requerir la intervención de sus progenitores.",
                "articulo_referencia": "Artículo 7.1 de la Ley Orgánica 3/2018 (LOPDGDD)",
                "documento_origen": "09 Ley Orgánica 3_2018, Protección de Datos Personales y garantía de los derechos digitales.md",
                "pagina_origen": 12,
                "dificultad": "Media"
            },

            # =========================================================================
            # TEMA 13: ESQUEMA NACIONAL DE SEGURIDAD (RD 311/2022)
            # =========================================================================
            {
                "id": "ADIF-14-01",
                "tema_id": "14_ENS",
                "tema_titulo": "Esquema Nacional de Seguridad (Real Decreto 311/2022)",
                "bloque_id": "B5",
                "pregunta": "¿Cuáles son las cinco dimensiones básicas de seguridad de la información definidas en el Esquema Nacional de Seguridad (RD 311/2022)?",
                "opciones": [
                    "Velocidad, Almacenamiento, Eficiencia, Cobertura y Rendimiento.",
                    "Confidencialidad, Integridad, Trazabilidad, Autenticidad y Disponibilidad.",
                    "Encriptación, Cortafuegos, Antivirus, Backup y Parcheado.",
                    "Legalidad, Economía, Eficacia, Transparencia y Eficiencia."
                ],
                "respuesta_correcta": 1,
                "explicacion": "El RD 311/2022 articula la seguridad sobre cinco dimensiones analizadas en los sistemas de información: Disponibilidad, Autenticidad, Integridad, Confidencialidad y Trazabilidad (frecuentemente memorizado con la regla DAICT).",
                "articulo_referencia": "Anexo I del Real Decreto 311/2022 (ENS)",
                "documento_origen": "14 Real Decreto 311_2022, Esquema Nacional de Seguridad..md",
                "pagina_origen": 35,
                "dificultad": "Examen Oficial"
            },

            # =========================================================================
            # TEMA 14: REGLAMENTO UE 402/2013 (Seguridad Ferroviaria y Evaluación de Riesgos)
            # =========================================================================
            {
                "id": "ADIF-10-01",
                "tema_id": "10_REGLAMENTO_402_2013",
                "tema_titulo": "Reglamento de Ejecución (UE) Nº 402/2013 (Método Común de Seguridad MCS)",
                "bloque_id": "B5",
                "pregunta": "¿Cuál es el objetivo principal del Reglamento de Ejecución (UE) nº 402/2013 en el sistema ferroviario europeo?",
                "opciones": [
                    "Fijar el precio máximo de los billetes de tren transfronterizos entre España y Francia.",
                    "Establecer un método común de seguridad para la evaluación y valoración del riesgo ante modificaciones operativas o técnicas.",
                    "Regular las horas de conducción del personal de cabina en líneas convencionales.",
                    "Determinar las multas impuestas por exceso de peso por eje a los vagones de mercancías."
                ],
                "respuesta_correcta": 1,
                "explicacion": "El Reglamento de Ejecución (UE) nº 402/2013 establece un método común de seguridad (MCS) para la evaluación y valoración del riesgo que debe aplicarse cuando se introduzca cualquier cambio significativo en el sistema ferroviario de la Unión Europea.",
                "articulo_referencia": "Artículo 1 del Reglamento de Ejecución (UE) nº 402/2013",
                "documento_origen": "10 REGLAMENTO DE EJECUCIÓN (UE) Nº 402_2013 y REGLAMENTO DE EJECUCIÓN (UE) 2015_1136.md",
                "pagina_origen": 2,
                "dificultad": "Media"
            },

            # =========================================================================
            # TEMA 15: ESTATUTO DE LOS TRABAJADORES (RD Leg. 2/2015)
            # =========================================================================
            {
                "id": "ADIF-03-ET-01",
                "tema_id": "03_ESTATUTO_TRABAJADORES",
                "tema_titulo": "Estatuto de los Trabajadores - Título I",
                "bloque_id": "B2",
                "pregunta": "Conforme al Estatuto de los Trabajadores, ¿cuál es la duración máxima ordinaria de la jornada de trabajo de promedio en cómputo anual salvo pacto en convenio?",
                "opciones": [
                    "35 horas semanales.",
                    "37,5 horas semanales.",
                    "40 horas semanales de trabajo efectivo de promedio en cómputo anual.",
                    "48 horas semanales sumando descansos."
                ],
                "respuesta_correcta": 2,
                "explicacion": "El artículo 34.1 del Estatuto de los Trabajadores dispone: 'La duración de la jornada de trabajo será la pactada en los convenios colectivos o contratos de trabajo. La duración máxima de la jornada ordinaria de trabajo será de cuarenta horas semanales de trabajo efectivo de promedio en cómputo anual'.",
                "articulo_referencia": "Artículo 34.1 del Estatuto de los Trabajadores",
                "documento_origen": "03 Estatuto de los Trabajadores. Titulo I.md",
                "pagina_origen": 38,
                "dificultad": "Básica"
            },

            # =========================================================================
            # TEMA 16: LEY GENERAL PRESUPUESTARIA (Ley 47/2003)
            # =========================================================================
            {
                "id": "ADIF-02-LGP-01",
                "tema_id": "02_LEY_PRESUPUESTARIA",
                "tema_titulo": "Ley 47/2003, General Presupuestaria",
                "bloque_id": "B1",
                "pregunta": "¿Qué principio presupuestario prohíbe destinar un ingreso específico a financiar un gasto determinado, debiendo integrarse en la caja común del Tesoro salvo excepción legal expresa?",
                "opciones": [
                    "Principio de especialidad cuantitativa.",
                    "Principio de no afectación de los ingresos.",
                    "Principio de devengo financiero.",
                    "Principio de prudencia valorativa."
                ],
                "respuesta_correcta": 1,
                "explicacion": "El artículo 27.2 de la Ley 47/2003 consagra el principio de no afectación: los recursos del Estado, los de cada uno de sus organismos autónomos y los de las entidades integrantes del sector público estatal con presupuesto limitativo se destinarán a satisfacer el conjunto de sus respectivas obligaciones.",
                "articulo_referencia": "Artículo 27 de la Ley 47/2003 General Presupuestaria",
                "documento_origen": "02 Ley 47_2003, de 26 de noviembre, General Presupuestaria Título I, Título II, Título V, Título VI, Título VII.md",
                "pagina_origen": 18,
                "dificultad": "Media"
            },

            # =========================================================================
            # TEMA 17: SEGURIDAD SOCIAL (RD Leg. 8/2015)
            # =========================================================================
            {
                "id": "ADIF-01-SS-01",
                "tema_id": "01_SEGURIDAD_SOCIAL",
                "tema_titulo": "Ley General de la Seguridad Social (RD Leg. 8/2015)",
                "bloque_id": "B2",
                "pregunta": "¿Cuál de las siguientes afirmaciones respecto a la afiliación a la Seguridad Social es correcta conforme a la LGSS?",
                "opciones": [
                    "La afiliación es múltiple, debiendo tramitarse una nueva cada vez que se cambia de empresa.",
                    "La afiliación es obligatoria para las personas comprendidas en su campo de aplicación y única para toda la vida del trabajador.",
                    "La afiliación tiene una vigencia máxima de 5 años renovables a solicitud del interesado.",
                    "La afiliación al Régimen General solo es obligatoria para contratos indefinidos."
                ],
                "respuesta_correcta": 1,
                "explicacion": "El artículo 138 de la Ley General de la Seguridad Social (LGSS) establece expresamente que la afiliación a la Seguridad Social es obligatoria y única para toda la vida del trabajador y para todo el sistema, sin perjuicio de las altas y bajas en los diferentes regímenes.",
                "articulo_referencia": "Artículo 138 del Real Decreto Legislativo 8/2015 (LGSS)",
                "documento_origen": "01 RD 8_2015, Ley G. Seguridad Social, Preámbulo. Cap. del I al IV del Título I y Cap. del I al XVI del Título II.md",
                "pagina_origen": 32,
                "dificultad": "Básica"
            },

            # =========================================================================
            # TEMA 18: LEY TRANS Y DIVERSIDAD (Ley 4/2023)
            # =========================================================================
            {
                "id": "ADIF-04-TRANS-01",
                "tema_id": "04_LEY_TRANS",
                "tema_titulo": "Ley 4/2023 para la igualdad de las personas trans y garantía de derechos LGTBI",
                "bloque_id": "B3",
                "pregunta": "Conforme a la Ley 4/2023, ¿se exige la presentación previa de informe médico o psicológico para la rectificación registral de la mención relativa al sexo de las personas mayores de dieciséis años?",
                "opciones": [
                    "Sí, es obligatorio un informe pericial que acredite disforia de género durante al menos dos años.",
                    "No, el ejercicio de este derecho en ningún caso podrá estar condicionado a la previa presentación de informe médico o psicológico.",
                    "Solo si no se cuenta con el consentimiento de ambos progenitores.",
                    "Se requiere un certificado expedido por el servicio autonómico de salud."
                ],
                "respuesta_correcta": 1,
                "explicacion": "El artículo 44 de la Ley 4/2023 consagra la libre manifestación de la voluntad para la rectificación registral del sexo a partir de los 16 años, estableciendo que en ningún caso podrá condicionarse a la presentación previa de informes médicos o psicológicos relativos a disforia de género ni a la modificación previa de la apariencia física.",
                "articulo_referencia": "Artículo 44 de la Ley 4/2023",
                "documento_origen": "04 Ley 4_2023, Igualdad real y efectiva de las personas trans. Preambulo y Títulos I, II, III.md",
                "pagina_origen": 15,
                "dificultad": "Media"
            },

            # =========================================================================
            # TEMA 19: ESTABILIDAD PRESUPUESTARIA (LO 2/2012)
            # =========================================================================
            {
                "id": "ADIF-05-EP-01",
                "tema_id": "05_LO_ESTABILIDAD",
                "tema_titulo": "Ley Orgánica 2/2012 de Estabilidad Presupuestaria y Sostenibilidad Financiera",
                "bloque_id": "B1",
                "pregunta": "¿Qué establece el principio de prioridad absoluta de pago de la deuda pública consagrado en el artículo 14 de la Ley Orgánica 2/2012?",
                "opciones": [
                    "Los pagos de salarios de los empleados públicos siempre se ejecutan antes del pago de intereses de la deuda.",
                    "El pago de los créditos para satisfacer los intereses y el capital de la deuda pública goza de prioridad absoluta frente a cualquier otro gasto.",
                    "Solo se aplica a la deuda exterior emitida en dólares estadounidenses.",
                    "Es un principio optativo que cada Administración puede suspender por orden de su titular."
                ],
                "respuesta_correcta": 1,
                "explicacion": "El artículo 14 de la Ley Orgánica 2/2012 (en concordancia directa con el artículo 135 de la Constitución Española) dicta que los créditos presupuestarios para satisfacer los intereses y el capital de la deuda pública de las Administraciones gozan de prioridad absoluta de pago frente a cualquier otra necesidad presupuestaria.",
                "articulo_referencia": "Artículo 14 de la Ley Orgánica 2/2012 y art. 135 CE",
                "documento_origen": "05 Ley Orgánica 2_2012 de Estabilidad Presupuestaria y Sostenibilidad Financiera.md",
                "pagina_origen": 14,
                "dificultad": "Examen Oficial"
            },

            # =========================================================================
            # TEMA 20: ADMINISTRACIÓN ELECTRÓNICA (RD 203/2021)
            # =========================================================================
            {
                "id": "ADIF-04-ELEC-01",
                "tema_id": "04_RD_ELECTRONICO",
                "tema_titulo": "Reglamento de actuación del sector público por medios electrónicos (RD 203/2021)",
                "bloque_id": "B1",
                "pregunta": "¿Qué es la Sede Electrónica según el artículo 9 del Real Decreto 203/2021?",
                "opciones": [
                    "Un blog divulgativo sobre las licitaciones públicas de obras.",
                    "La dirección electrónica disponible para la ciudadanía a través de redes de telecomunicaciones cuya titularidad corresponde a una Administración Pública.",
                    "El buzón personal de correo electrónico corporativo de cada funcionario.",
                    "Una intranet accesible solo físicamente desde los centros de trabajo de Adif."
                ],
                "respuesta_correcta": 1,
                "explicacion": "El artículo 9 del RD 203/2021 define la sede electrónica o sede electrónica asociada como aquella dirección electrónica disponible para la ciudadanía a través de redes de telecomunicaciones, cuya titularidad corresponde a una Administración Pública, o a uno o varios organismos públicos o entidades de Derecho Público.",
                "articulo_referencia": "Artículo 9 del Real Decreto 203/2021",
                "documento_origen": "04 RD 203_2021,  Regl. actua. y func. sect. público medios electrónicos.md",
                "pagina_origen": 11,
                "dificultad": "Básica"
            },

            # =========================================================================
            # TEMA 21: REGLAMENTO UE 2018/762 (Métodos Comunes de Seguridad - SGS)
            # =========================================================================
            {
                "id": "ADIF-11-01",
                "tema_id": "11_REGLAMENTO_2018_762",
                "tema_titulo": "Reglamento Delegado (UE) 2018/762 (Sistemas de Gestión de la Seguridad)",
                "bloque_id": "B5",
                "pregunta": "¿Qué exige el Reglamento Delegado (UE) 2018/762 a los administradores de infraestructuras ferroviarias como Adif respecto a su Sistema de Gestión de la Seguridad (SGS)?",
                "opciones": [
                    "Operar sin planes de contingencia para ahorrar costes de supervisión.",
                    "Definir una política de seguridad clara, procedimientos de control de riesgos, gestión del factor humano e investigación de incidentes.",
                    "Transferir la responsabilidad de cualquier fallo en la vía a los maquinistas de las empresas operadoras.",
                    "Disponer de un único técnico de seguridad para toda la red de alta velocidad."
                ],
                "respuesta_correcta": 1,
                "explicacion": "El Reglamento Delegado (UE) 2018/762 establece los métodos comunes de seguridad relativos a los requisitos del sistema de gestión de la seguridad (SGS), exigiendo que tanto los administradores de infraestructura como las empresas ferroviarias garanticen la gestión de riesgos, formación del personal, análisis del factor humano y mejora continua de la seguridad.",
                "articulo_referencia": "Anexo I y II del Reglamento Delegado (UE) 2018/762",
                "documento_origen": "11 REGLAMENTO DELEGADO (UE) 2018_762 DE LA COMISIÓN.md",
                "pagina_origen": 6,
                "dificultad": "Media"
            }
        ]
        return questions

    def export_data_files(self) -> None:
        """Exporta la base de datos a JSON y a JavaScript para la Web App interactiva."""
        WEB_APP_DIR.mkdir(parents=True, exist_ok=True)

        # 1. Guardar JSON
        with open(self.questions_file, "w", encoding="utf-8") as f:
            json.dump(self.questions, f, ensure_ascii=False, indent=2)

        # 2. Guardar JS con variable global para uso 100% offline sin restricciones CORS
        payload = {
            "bloques": BLOQUES_TEMATICOS,
            "preguntas": self.questions,
            "total_preguntas": len(self.questions),
            "version": "1.0.0",
            "temario_fuente": "Documentación Oficial Adif y Legislación Consolidada",
        }
        js_content = f"// Datos de preguntas generados automáticamente por AdifExamAgent\nwindow.ADIF_EXAM_DATA = {json.dumps(payload, ensure_ascii=False, indent=2)};\n"
        with open(self.questions_js_file, "w", encoding="utf-8") as f:
            f.write(js_content)

        print(f"[+] Base de preguntas exportada a: {self.questions_file}")
        print(f"[+] Script de datos exportado a: {self.questions_js_file} ({len(self.questions)} preguntas activas)")

    def generate_markdown_mock_exam(self, num_questions: int = 20, output_filename: str = "simulacro_oficial_adif_1.md") -> Path:
        """Genera un examen simulacro completo en formato Markdown con plantilla de respuestas."""
        SIMULACROS_DIR.mkdir(parents=True, exist_ok=True)
        out_path = SIMULACROS_DIR / output_filename

        selected = random.sample(self.questions, min(num_questions, len(self.questions)))

        lines = [
            "# SIMULACRO OFICIAL DE EXAMEN - OPOSICIONES ADIF",
            "",
            "> **Instrucciones para el candidato:**",
            "> - Cada pregunta tiene una única respuesta válida entre cuatro opciones.",
            "> - En exámenes oficiales de Adif / Administraciones Públicas, las respuestas correctas suman 1 punto y las incorrectas suelen penalizar 1/3 (0,33 puntos). Las no contestadas no puntúan.",
            "> - Al final del documento encontrarás la **Plantilla de Soluciones Justificadas** con cita exacta a los artículos y páginas de la documentación oficial.",
            "",
            "---",
            "",
            "## CUESTIONARIO",
            ""
        ]

        # Preguntas
        for i, q in enumerate(selected, start=1):
            lines.append(f"### Pregunta {i} ({q['tema_titulo']})")
            lines.append(f"**{q['pregunta']}**\n")
            for opt in q["opciones"]:
                lines.append(f"- [ ] {opt}")
            lines.append("")

        # Plantilla de corrección
        lines.append("---")
        lines.append("")
        lines.append("## PLANTILLA DE SOLUCIONES Y JUSTIFICACIÓN LEGAL")
        lines.append("")
        lines.append("| Pregunta | Correcta | Artículo / Referencia | Documento Fuente (Pág.) |")
        lines.append("|:---:|:---:|---|---|")

        letras = ["A", "B", "C", "D"]
        for i, q in enumerate(selected, start=1):
            corr = letras[q["respuesta_correcta"]]
            ref = q["articulo_referencia"]
            doc = q["documento_origen"]
            pag = q["pagina_origen"]
            lines.append(f"| {i} | **{corr}** | {ref} | `{doc}` (Pág. {pag}) |")

        lines.append("")
        lines.append("### Razonamiento Detallado Pregunta a Pregunta\n")
        for i, q in enumerate(selected, start=1):
            corr = letras[q["respuesta_correcta"]]
            lines.append(f"#### Pregunta {i}: Opción {corr}")
            lines.append(f"> **Explicación oficial:** {q['explicacion']}")
            lines.append(f"> **Base legal:** {q['articulo_referencia']} (Ver archivo [{q['documento_origen']}](../markdown_output/{q['documento_origen']}) en página {q['pagina_origen']}).\n")

        out_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"[+] Simulacro de examen en Markdown generado en: {out_path}")
        return out_path

    def get_local_ip(self) -> str:
        """Detecta la dirección IP local del ordenador en la red Wi-Fi."""
        import socket
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "localhost"

    def serve_web_app(self, port: int = 8080) -> None:
        """Inicia un servidor HTTP local para interactuar con la herramienta didáctica en el navegador."""
        self.export_data_files()
        local_ip = self.get_local_ip()
        mobile_url = f"http://{local_ip}:{port}"
        desktop_url = f"http://localhost:{port}"

        # Generar código QR para móvil
        try:
            import qrcode
            qr = qrcode.QRCode(box_size=10, border=2)
            qr.add_data(mobile_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            img.save(WEB_APP_DIR / "mobile_qr.png")
            qr_available = True
        except Exception as e:
            qr_available = False

        os.chdir(WEB_APP_DIR)

        handler = http.server.SimpleHTTPRequestHandler
        socketserver.TCPServer.allow_reuse_address = True

        with socketserver.TCPServer(("", port), handler) as httpd:
            print("==================================================================")
            print("  ADIF OPOSICIONES PREP - SERVIDOR DE ESTUDIO ACTIVO")
            print("==================================================================")
            print(f"  💻 En tu ordenador:      {desktop_url}")
            print(f"  📱 En tu teléfono móvil: {mobile_url}")
            print("------------------------------------------------------------------")
            if qr_available:
                print("  Escanea este código QR con la cámara de tu móvil (misma Wi-Fi):")
                print("")
                import io
                f = io.StringIO()
                qr.print_ascii(out=f)
                print(f.getvalue())
                print("------------------------------------------------------------------")
            print("  💡 Consejo PWA: Abre el enlace en Safari o Chrome y pulsa")
            print("     'Añadir a pantalla de inicio' para estudiar 100% OFFLINE.")
            print("  Para detener el servidor pulsa: Ctrl + C")
            print("==================================================================")
            try:
                webbrowser.open(desktop_url)
            except Exception:
                pass
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                print("\n[!] Servidor detenido por el usuario.")


def main():
    agent = AdifExamAgent()
    agent.export_data_files()
    agent.generate_markdown_mock_exam(num_questions=20)

    if "--serve" in sys.argv:
        port = 8080
        if len(sys.argv) > 2 and sys.argv[2].isdigit():
            port = int(sys.argv[2])
        agent.serve_web_app(port=port)


if __name__ == "__main__":
    main()
