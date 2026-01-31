# Semillero-ia-Agente-Anti-Cancelacin-InteliCore
Este proyecto implementa un Agente de Retención diseñado para un ISP (Proveedor de Internet). El agente utiliza procesamiento de lenguaje natural (NLP) y lógica basada en datos para detectar intenciones de cancelación y negociar con el cliente de forma autónoma.

##Funcionalidades Principales

1.  Proactividad:Analiza datos simulados del CRM (fallas, facturación) antes de iniciar la conversación.
2.  Análisis de Sentimiento:Detecta frustración o ira utilizando TextBlob para priorizar la atención.
3.  Lógica Difusa (Fuzzy Logic):Entiende inputs con errores ortográficos (ej: "kiero canselar").
4.  Escalera de Retención:Implementa una estrategia de negociación de dos niveles (Oferta Estándar -> Oferta Supervisor).
5.  Manejo de Estados:Capaz de diferenciar entre soporte técnico, consultas de facturación y solicitudes de baja.

##Estructura del Proyecto

- src/main.py: Código principal y bucle de ejecución.
- src/config/reglas.py: Base de conocimiento, argumentos de venta y catálogo de ofertas.
- requirements.txt: Librerías necesarias.

## 🛠️ Instalación y Uso

1. Clonar el repositorio.
2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
