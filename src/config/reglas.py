# BASE DE CONOCIMIENTO Y REGLAS DE NEGOCIO

BASE_CONOCIMIENTO = {
    # Argumentos para defender la marca
    "argumentos_valor": {
        "precio": "Entiendo que la economía es prioridad. Pero recuerda que en Netlife garantizamos velocidad simétrica, vital para videollamadas, algo que los planes económicos de la competencia no ofrecen.",
        "tecnico": "Lamento los inconvenientes. La fibra óptica es muy estable, por lo que estos fallos suelen ser de configuración del router o saturación de canal WiFi, algo totalmente corregible.",
        "competencia": "Comprendo. Solo ten en cuenta que muchas promociones de la competencia son 'precios de introducción' que suben al mes 6. Nosotros mantenemos tu tarifa fija sin sorpresas.",
        "mudanza": "Entiendo el estrés de la mudanza. Recuerda que tenemos cobertura nacional y mantener tu antigüedad te da beneficios que perderías al iniciar contrato nuevo en otro lado."
    },
    
    # ESCALERA DE RETENCIÓN (Oferta Nivel 1 -> Oferta Nivel 2)
    "ofertas_escalonadas": {
        "precio": [
            "Descuento del 15% en tu factura por los próximos 6 meses.",
            "Descuento especial del 25% por 3 meses + Upgrade de velocidad sin costo."
        ],
        "tecnico": [
            "Visita técnica prioritaria (Ticket Platinum - 24h).",
            "Cambio de Router a nueva generación WiFi 6 (Dual Band) sin costo de instalación."
        ],
        "competencia": [
            "Duplicar tu velocidad actual por 1 año manteniendo el mismo precio.",
            "Igualación de la tarifa de la competencia durante 6 meses (Price Match)."
        ],
        "mudanza": [
            "Traslado de servicio sin costo de instalación.",
            "Suspensión temporal del servicio (Plan Viajero) sin cobro mensual."
        ]
    }
}
