import time
import sys
import difflib
from textblob import TextBlob
import nltk

try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
    nltk.download('punkt_tab')

# --- BASE DE CONOCIMIENTO (Reglas de Negocio) ---
BASE_CONOCIMIENTO = {
    "argumentos_valor": {
        "precio": "Entiendo que la economía es prioridad. Pero recuerda que en Netlife garantizamos velocidad simétrica, vital para videollamadas, algo que los planes económicos de la competencia no ofrecen.",
        "tecnico": "Lamento los inconvenientes. La fibra óptica es muy estable, por lo que estos fallos suelen ser de configuración del router o saturación de canal WiFi, algo totalmente corregible.",
        "competencia": "Comprendo. Solo ten en cuenta que muchas promociones de la competencia son 'precios de introducción' que suben al mes 6. Nosotros mantenemos tu tarifa fija sin sorpresas.",
        "mudanza": "Entiendo el estrés de la mudanza. Recuerda que tenemos cobertura nacional y mantener tu antigüedad te da beneficios que perderías al iniciar contrato nuevo en otro lado."
    },
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

# --- FUNCIONES DE PROCESAMIENTO DE LENGUAJE (NLP) ---
def es_texto_similar(texto_usuario, lista_palabras_clave, umbral=0.8):
    if not texto_usuario: return False
    palabras_usuario = texto_usuario.lower().split()
    for palabra in palabras_usuario:
        coincidencias = difflib.get_close_matches(palabra, lista_palabras_clave, n=1, cutoff=umbral)
        if coincidencias: return True
    return False

def analizar_sentimiento(texto):
    blob = TextBlob(texto)
    score = blob.sentiment.polarity 
    texto_lower = texto.lower()
    
    keywords_ira = ["pesimo", "horrible", "lento", "basura", "estafa", "odio", "harto", "malo", "asco", "porqueria", "sirve", "mierda", "verga"]
    
    if es_texto_similar(texto, keywords_ira, 0.85): score = -0.8
    elif any(x in texto_lower for x in ["excelente", "bueno", "gracias", "rapido", "genial", "ok"]): score = 0.8
    
    if score < -0.3: return "Enojado/Frustrado", score
    elif score > 0.3: return "Satisfecho", score
    return "Neutral", score

def detectar_intencion(texto):
    k_precio = ["caro", "dinero", "pagar", "economico", "bajar", "precio", "costo", "factura", "plata"]
    k_tecnico = ["lento", "lenta", "sirve", "corta", "internet", "wifi", "falla", "tecnico", "velocidad", "lag"]
    k_competencia = ["claro", "movistar", "cnt", "xtrim", "competencia", "netuno", "oferta", "cambiarme", "otro", "megas", "gigas"]
    k_mudanza = ["mudanza", "casa", "viaje", "pais", "ciudad", "traslado"]

    if es_texto_similar(texto, k_precio, 0.8): return "precio"
    elif es_texto_similar(texto, k_tecnico, 0.8): return "tecnico"
    elif es_texto_similar(texto, k_competencia, 0.8): return "competencia"
    elif es_texto_similar(texto, k_mudanza, 0.8): return "mudanza"
    return "desconocido"

def es_solicitud_baja(texto):
    palabras_peligro = ["cancelar", "baja", "cortar", "anular", "retirar", "irme", "eliminar", "renunciar"]
    return es_texto_similar(texto, palabras_peligro, 0.8) 

# --- CLASE PRINCIPAL DEL AGENTE ---
class AgenteNetlife:
    def __init__(self, datos_cliente):
        self.datos_cliente = datos_cliente
        self.cliente = datos_cliente['cliente']
        self.retencion_activa = False 
        self.datos_sesion = {
            "motivo_detectado": None,
            "sentimiento_acumulado": [],
            "oferta_presentada": None,
            "decision_final": "En proceso",
            "nivel_oferta": 0
        }
        self.diagnostico_inicial() 

    def diagnostico_inicial(self):
        fallas = self.datos_cliente.get('fallas_internet', 0)
        intermitencia = self.datos_cliente.get('casos_de_intermitencia', 0)
        facturacion = self.datos_cliente.get('problemas_facturacion', 0)
        
        if fallas + intermitencia > 10:
            self.datos_sesion['motivo_detectado'] = "tecnico"
            print(f"⚠️ SISTEMA: Cliente crítico detectado ({fallas} fallas).")
        elif facturacion > 2:
            self.datos_sesion['motivo_detectado'] = "precio"
            print(f"⚠️ SISTEMA: Cliente con reclamos de facturación.")

    def generar_respuesta(self, input_usuario):
        sentimiento, score = analizar_sentimiento(input_usuario)
        self.datos_sesion['sentimiento_acumulado'].append(score)
        texto_lower = input_usuario.lower()
        
        # --- FASE 0: MONITOREO ---
        if not self.retencion_activa:
            intencion = detectar_intencion(input_usuario)
            es_baja = es_solicitud_baja(input_usuario)
            activar_por_datos = (intencion == self.datos_sesion['motivo_detectado'])
            
            # Consultas Operativas
            if "revisar" in texto_lower or "ver" in texto_lower or "factura" in texto_lower:
                if "factura" in texto_lower or "costo" in texto_lower:
                    return "✅ Entendido. Puedes descargar tu factura detallada ingresando a: www.netlife.ec/mi-cuenta."

            # Derivación a Soporte
            keywords_soporte = ["soporte", "tecnico", "técnico", "ayuda", "revisen", "arreglen", "vengan", "visita"]
            if any(k in texto_lower for k in keywords_soporte) and not es_baja:
                 self.datos_sesion['decision_final'] = "DERIVADO_A_SOPORTE"
                 return "✅ Entendido. He generado el Ticket #INC-2026. 🛠️ Transferencia a técnico humano iniciada."

            # GATILLOS DE RETENCIÓN (Prioridad Alta)
            if es_baja or sentimiento == "Enojado/Frustrado" or activar_por_datos or intencion == "competencia":
                self.retencion_activa = True
                if not self.datos_sesion['motivo_detectado']:
                    self.datos_sesion['motivo_detectado'] = intencion
                
                motivo = self.datos_sesion['motivo_detectado']
                
                # Respuestas Proactivas
                if motivo == "tecnico":
                    fallas = self.datos_cliente.get('fallas_internet', 0)
                    oferta = BASE_CONOCIMIENTO["ofertas_escalonadas"]["tecnico"][0]
                    self.datos_sesion['oferta_presentada'] = oferta
                    self.datos_sesion['nivel_oferta'] = 1
                    return f"Entiendo tu molestia. El sistema reporta {fallas} fallas recientes. 😟\nQueremos solucionarlo YA: >> {oferta} <<\n¿Nos permites realizar esta corrección?"
                
                elif motivo == "precio":
                    oferta = BASE_CONOCIMIENTO["ofertas_escalonadas"]["precio"][0]
                    self.datos_sesion['oferta_presentada'] = oferta
                    self.datos_sesion['nivel_oferta'] = 1
                    return f"Entiendo. Veo tus reportes de facturación. Te ofrezco: >> {oferta} << ¿Te gustaría mantener el servicio con este beneficio?"
                
                elif motivo == "competencia":
                    argumento = BASE_CONOCIMIENTO["argumentos_valor"]["competencia"]
                    oferta = BASE_CONOCIMIENTO["ofertas_escalonadas"]["competencia"][0]
                    self.datos_sesion['oferta_presentada'] = oferta
                    self.datos_sesion['nivel_oferta'] = 1
                    return f"{argumento}\n\nPara demostrarte que somos mejores, te ofrezco: >> {oferta} <<\n¿Te parece bien?"
                else:
                    return "He detectado tu intención de cancelar. Lamento escuchar eso. ¿El motivo es Precio, Fallas Técnicas o Competencia?"

            # Despedida (Prioridad Baja)
            keywords_adios = ["nada", "gracias", "chao", "adios", "ninguna", "todo bien", "no", "listo"]
            es_frase_corta = len(input_usuario.split()) < 4
            if es_texto_similar(input_usuario, keywords_adios, 0.8) and es_frase_corta:
                self.datos_sesion['decision_final'] = "CONSULTA_RESUELTA"
                return "¡Me alegra haberte ayudado! ¡Que tengas un excelente día! 👋"

            if intencion == "tecnico": return "¿Deseas soporte técnico o estás pensando en cancelar?"
            elif intencion == "precio": return "¿Deseas revisar tu factura o estás considerando la baja?"
            else: return f"Hola {self.cliente}, ¿En qué puedo ayudarte hoy?"

        # --- FASE 1: RETENCIÓN ---
        else:
            if self.datos_sesion['nivel_oferta'] == 0:
                intencion = detecting_intencion(input_usuario) # Fallback
                return "Te ofrezco..." # Simplificado por seguridad

            else:
                keywords_si = ["acepto", "bien", "acuerdo", "dale", "bueno", "ok", "si", "va", "solucionen", "arreglen", "revisen", "mejor"]
                rechazo_fuerte = "no quiero" in texto_lower or "no me interesa" in texto_lower or "no deseo" in texto_lower

                if es_texto_similar(input_usuario, keywords_si, 0.7) and not rechazo_fuerte:
                    self.datos_sesion['decision_final'] = "RETENIDO"
                    return "¡Excelente decisión! ✅ He agendado el beneficio en tu cuenta. Tu servicio sigue activo."
                
                elif es_solicitud_baja(input_usuario) or es_texto_similar(input_usuario, ["no", "nada", "tampoco", "nunca"], 0.8) or rechazo_fuerte:
                    if self.datos_sesion['nivel_oferta'] == 1:
                        motivo = self.datos_sesion['motivo_detectado']
                        oferta_nivel_2 = BASE_CONOCIMIENTO["ofertas_escalonadas"][motivo][1]
                        self.datos_sesion['nivel_oferta'] = 2
                        self.datos_sesion['oferta_presentada'] = oferta_nivel_2 
                        return f"¡Espera! ✋ Entiendo que la oferta anterior no fue suficiente. No quiero perderte como cliente.\n\nHe solicitado una autorización especial a mi supervisor y me permite ofrecerte esto SOLO POR HOY:\n\n⭐ >> {oferta_nivel_2} << ⭐\n\nEs mi mejor oferta final. ¿Te animas a quedarte con nosotros?"
                    else:
                        self.datos_sesion['decision_final'] = "CANCELADO"
                        return "Entiendo. 😔 He hecho todo lo posible. Respetamos tu decisión. Procederemos con la baja del servicio."
                else:
                    return "Es válida tu duda. Esta solución está garantizada. Si no funciona, revertimos el cambio. ¿Te animas a probarla?"

    def reporte_final(self):
        promedio = sum(self.datos_sesion['sentimiento_acumulado']) / len(self.datos_sesion['sentimiento_acumulado']) if self.datos_sesion['sentimiento_acumulado'] else 0
        print("\n" + "█"*60)
        print(f"📋 REPORTE FINAL - CLIENTE: {self.cliente}")
        print(f"► Motivo: {str(self.datos_sesion['motivo_detectado']).upper()}")
        print(f"► Sentimiento Final: {round(promedio, 2)}")
        print(f"► Resultado: [{self.datos_sesion['decision_final']}]")
        print("█"*60)

# --- EJECUCIÓN DEL SISTEMA ---
if __name__ == "__main__":
    print("🛠️ CONFIGURACIÓN DEL ESCENARIO DE PRUEBA 🛠️")
    try:
        nombre_input = input("1. Nombre del Cliente: ") or "Cliente Prueba"
        plan_input = int(input("2. Plan actual (ej. 650): ") or 650)
        fallas_input = int(input("3. N° de Fallas de Internet recientes: ") or 0)
        inter_input = int(input("4. N° de Casos de Intermitencia: ") or 0)
        fact_input = int(input("5. N° de Reclamos de Facturación: ") or 0)

        datos_dinamicos = {
            'cliente': nombre_input, 
            'plan_internet': plan_input, 
            'fallas_internet': fallas_input,        
            'casos_de_intermitencia': inter_input, 
            'problemas_facturacion': fact_input
        }

        print("\n" + "="*60)
        print(f"   🌐 INICIANDO AGENTE NETLIFE PARA: {nombre_input.upper()}")
        print("="*60)
        
        bot = AgenteNetlife(datos_dinamicos)

        # Saludo Proactivo
        if bot.datos_sesion['motivo_detectado'] == 'tecnico':
            print(f"\n🤖 Agente: Hola {nombre_input}. El sistema me alerta de inconvenientes técnicos. ¿Es por eso que nos contactas?")
        elif bot.datos_sesion['motivo_detectado'] == 'precio':
            print(f"\n🤖 Agente: Hola {nombre_input}. Veo una alerta relacionada con tu facturación. ¿En qué te puedo ayudar?")
        else:
            print(f"\n🤖 Agente: Hola {nombre_input}, veo que tienes un plan de {plan_input}Mbps activo. ¿En qué puedo ayudarte?") 

        while True:
            usuario_input = input(f"👤 {nombre_input}: ")
            if usuario_input.lower() == "exit": break
            time.sleep(0.5)
            respuesta = bot.generar_respuesta(usuario_input)
            print(f"🤖 Agente: {respuesta}")
            if bot.datos_sesion['decision_final'] != "En proceso":
                bot.reporte_final()
                break
    except ValueError:
        print("❌ Error de datos.")
