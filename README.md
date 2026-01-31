#Agente IA – Agente de Retención y Negociación Automatizada (Netlife)

## Integrantes
* ALAMA BARZALLO JERSON BLADIMIR
* CAMATON CORONEL RUBEN ANDRES
* MOREIRA MUYULEMA KAROL DENISSE

---

## Descripción del Agente
Este proyecto consiste en un Agente Inteligente de Retención diseñado específicamente para el sector de proveedores de internet (ISP). Su objetivo principal es reducir la tasa de cancelación (Churn Rate) automatizando la negociación con clientes en riesgo.

A diferencia de un chatbot convencional, este agente utiliza Lógica Difusa (Fuzzy Logic) y Análisis de Sentimiento para detectar no solo qué dice el cliente, sino cómo se siente. Implementa una estrategia de negociación escalonada (Oferta Estándar → Oferta de Supervisor) para maximizar la retención cuidando la rentabilidad de la empresa.

---

## ¿Qué hace el agente? (Funcionalidades)

### 1. Detección Proactiva de Riesgo
El agente no espera a que el cliente se queje. Al iniciar la sesión, analiza los datos simulados del CRM (fallas técnicas recientes, intermitencia, reclamos de facturación) y se anticipa al problema antes de que el usuario escriba.

### 2. Análisis de Sentimiento y NLP
Utiliza la librería TextBlob para medir la polaridad emocional del cliente.
* Si detecta Ira/Frustración (score < -0.3), activa inmediatamente el protocolo de contención.
* Si el cliente escribe con errores (ej: kiero canselar por fayas), el sistema de Lógica Difusa entiende la intención perfectamente.

### 3. Estrategia de Negociación Escalonada
El agente posee una "Escalera de Retención" para negociar beneficios:
* Nivel 1 (Estándar):Ofrece soluciones operativas o descuentos leves.
* Nivel 2 (Supervisor):Si el cliente rechaza la primera oferta, el agente "solicita autorización" y lanza una oferta final agresiva (ej: 25% descuento o Igualación de Precios de competencia).

### 4. Gestión de Intenciones Específicas
* Competencia:Contra-argumenta comparando servicios (ej: Fibra vs Cobre) y ofrece igualación de precios.
* Soporte Técnico:Si el cliente solicita explícitamente ayuda técnica, el agente genera un ticket y deriva a un humano (evita retener innecesariamente).
* Facturación:Provee enlaces directos para consultas operativas, filtrando llamadas innecesarias.

---

## Tecnologías Utilizadas
* Python 3.12+ (Lógica principal)
* TextBlob (Procesamiento de Lenguaje Natural)
* Difflib (Coincidencia de patrones y corrección de errores)
* NLTK (Tokenización de texto)

## Instrucciones de Ejecución

Para probar el agente en tu máquina local, sigue estos pasos:

1. Clonar el repositorio y entrar a la carpeta:
   ```bash
   git clone [TU_LINK_DE_GITHUB_AQUI]
   cd nombre-del-repo
   pip install -r requirements.txt
   cd src
   python main.py
