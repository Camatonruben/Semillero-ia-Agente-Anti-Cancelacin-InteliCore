import time
import sys
import difflib
from textblob import TextBlob
import nltk

# Importamos la configuración desde la carpeta config
try:
    from config.reglas import BASE_CONOCIMIENTO
except ImportError:
    # Parche por si se ejecuta el archivo directamente desde src/
    from reglas import BASE_CONOCIMIENTO

# Descarga necesaria para análisis de texto
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

# --- FUNCIONES DE NLP ---
def es_texto_similar(texto_usuario, lista_palabras_clave, umbral=0.8):
    palabras_usuario = texto_usuario.lower().split()
    for palabra in palabras_usuario:
        coincidencias = difflib.get_close_matches(palabra, lista_palabras_clave, n=1, cutoff=umbral)
        if coincidencias: return True
    return False

def analizar_sentimiento(texto):
    blob = TextBlob(texto)
    score = blob.sentiment.polarity 
    texto_lower = texto.lower()
    keywords_ira = ["pesimo", "horrible", "lento", "basura", "estafa", "odio", "harto", "malo", "asco", "porqueria", "sirve"]
    if es_texto_similar(texto, keywords_ira, 0.85): score = -0.8
    elif any(x in texto_lower for x in ["excelente", "bueno", "gracias", "rapido", "genial", "ok"]): score = 0.8
    if score < -0.3: return "Enojado/Frustrado", score
    elif score > 0.3: return "Satisfecho", score
    return "Neutral", score

def detectar_intencion(texto):
    k_precio = ["caro", "dinero", "pagar", "economico", "bajar", "precio", "costo", "factura", "plata"]
    k_tecnico = ["lento", "lenta", "sirve", "corta", "internet", "wifi", "falla", "tecnico", "velocidad", "lag"]
    k_competencia = ["claro", "movistar", "cnt", "xtrim", "competencia", "netuno", "oferta", "cambiarme", "otro"]
    k_mudanza = ["mudanza", "casa", "viaje", "pais", "ciudad", "traslado"]
    if es_texto_similar(texto, k_precio, 0.8): return "precio"
    elif es_texto_similar(texto, k_tecnico, 0.8): return "tecnico"
    elif es_texto_similar(texto, k_competencia, 0.8): return "competencia"
    elif es_texto_similar(texto, k_mudanza, 0.8): return "mudanza"
    return "desconocido"

def es_solicitud_baja(texto):
    palabras_peligro = ["cancelar", "baja", "cortar", "anular", "retirar", "irme", "eliminar", "renunciar"]
    return es_texto_similar(texto, palabras_peligro, 0.8) 

# --- CLASE DEL AGENTE ---
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

    def animacion_escribiendo(self):
        sys.stdout.write("Agente escribiendo")
        for _ in range(3):
            sys.stdout.write(".")
            sys.stdout.flush()
            time.sleep(0.3)
        sys.stdout.write("\r" + " " * 20 + "\r")

    def generar_respuesta(self, input_usuario):
        sentimiento, score = analizar_sentimiento(input_usuario)
        self.datos_sesion['sentimiento_acumulado'].append(score)
        texto_lower = input_usuario.lower()
        
        if not self.retencion_activa:
            intencion = detectar_intencion(input_usuario)
            es_baja = es_solicitud_baja(input_usuario)
            activar_por_datos = (intencion == self.datos_sesion['motivo_detectado'])
            
            # Consultas operativas
            if "revisar" in texto_lower or "ver" in texto_lower or "factura" in texto_lower:
                if "factura" in texto_lower or "costo" in texto_lower:
                    return "✅ Entendido. Puedes descargar tu factura detallada ingresando a: www.netlife.ec/mi-cuenta. ¿Necesitas ayuda con algo más?"
            
            # Derivación Soporte
            keywords_soporte = ["soporte", "tecnico", "técnico", "ayuda", "revisen", "arreglen", "vengan", "visita"]
            if any(k in texto_lower for k in keywords_soporte) and not es_baja:
                 self.datos_sesion['decision_final'] = "DERIVADO_A_SOPORTE"
                 return "✅ Entendido. He generado el Ticket #INC-2026. 🛠️\nEstoy transfiriendo tu caso inmediatamente a un especialista técnico humano. ¡Gracias!"

            # Despedida
            keywords_adios = ["nada", "gracias", "chao", "adios", "ninguna", "todo bien", "no", "listo"]
            if es_texto_similar(input_usuario, keywords_adios, 0.8):
                self.datos_sesion['decision_final'] = "CONSULTA_RESUELTA"
                return "¡Me alegra haberte ayudado! ¡Que tengas un excelente día! 👋"

            if es_baja or sentimiento == "Enojado/Frustrado" or activar_por_datos:
                self.retencion_activa = True
                motivo = self.datos_sesion['motivo_detectado']
                if motivo == "tecnico":
                    fallas = self.datos_cliente['fallas_internet']
                    oferta = BASE_CONOCIMIENTO["ofertas_escalonadas"]["tecnico"][0]
                    self.datos_sesion['oferta_presentada'] = oferta
                    self.datos_sesion['nivel_oferta'] = 1
                    return f"Entiendo tu molestia. El sistema reporta {fallas} fallas recientes. 😟\nQueremos solucionarlo YA: >> {oferta} <<\n¿Nos permites realizar esta corrección?"
                elif motivo == "precio":
                    oferta = BASE_CONOCIMIENTO["ofertas_escalonadas"]["precio"][0]
                    self.datos_sesion['oferta_presentada'] = oferta
                    self.datos_sesion['nivel_oferta'] = 1
                    return f"Entiendo. Veo tus reportes de facturación. Te ofrezco: >> {oferta} << ¿Te gustaría mantener el servicio con este beneficio?"
                else:
                    return "He detectado tu intención de cancelar. Lamento escuchar eso. ¿El motivo es Precio, Fallas Técnicas o Competencia?"

            if intencion == "tecnico": return "¿Deseas soporte técnico o estás pensando en cancelar?"
            elif intencion == "precio": return "¿Deseas revisar tu factura o estás considerando la baja?"
            else: return f"Hola {self.cliente}, ¿En qué puedo ayudarte hoy?"

        else:
            if self.datos_sesion['nivel_oferta'] == 0:
                intencion = detectar_intencion(input_usuario)
                if intencion == "desconocido": 
                    intencion = self.datos_sesion['motivo_detectado'] if self.datos_sesion['motivo_detectado'] else "precio"
                self.datos_sesion['motivo_detectado'] = intencion
                
                argumento = BASE_CONOCIMIENTO["argumentos_valor"].get(intencion, "")
                oferta = BASE_CONOCIMIENTO["ofertas_escalonadas"][intencion][0]
                self.datos_sesion['oferta_presentada'] = oferta
                self.datos_sesion['nivel_oferta'] = 1
                return f"{argumento}\n\nPor eso, te ofrezco: >> {oferta} <<\n¿Te parece justo para continuar con el servicio?"

            else:
                keywords_si = ["acepto", "bien", "acuerdo", "dale", "bueno", "ok", "si", "va", "sirve", "solucionen", "arreglen", "revisen"]
                if es_texto_similar(input_usuario, keywords_si, 0.7):
                    self.datos_sesion['decision_final'] = "RETENIDO"
                    return "¡Excelente decisión! ✅ He agendado el beneficio en tu cuenta. Tu servicio sigue activo."
                elif es_solicitud_baja(input_usuario) or es_texto_similar(input_usuario, ["no", "nada", "tampoco", "nunca"], 0.8):
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
        if self.datos_sesion['decision_final'] == "DERIVADO_A_SOPORTE":
            print("\n" + "="*60 + "\n🛠️ GESTIÓN DE SOPORTE - CLIENTE: " + self.cliente + "\n   Estado: En espera de técnico humano\n" + "="*60)
            return
        if self.datos_sesion['decision_final'] == "CONSULTA_RESUELTA":
            print("\n" + "="*60 + "\n✅ SESIÓN FINALIZADA - CLIENTE: " + self.cliente + "\n   Estado: Atendido Exitosamente\n" + "="*60)
            return

        promedio = sum(self.datos_sesion['sentimiento_acumulado']) / len(self.datos_sesion['sentimiento_acumulado']) if self.datos_sesion['sentimiento_acumulado'] else 0
        print("\n" + "█"*60)
        print(f"📋 REPORTE FINAL - CLIENTE: {self.cliente}")
        print("█"*60)
        print(f"► Motivo: {str(self.datos_sesion['motivo_detectado']).upper()}")
        print(f"► Sentimiento Final: {round(promedio, 2)}")
        print(f"► Última Oferta: {self.datos_sesion['oferta_presentada']}")
        print(f"► Nivel de Negociación Alcanzado: {self.datos_sesion['nivel_oferta']}/2")
        print("-" * 60)
        print(f"► RESULTADO: [{self.datos_sesion['decision_final']}]")
        print("█"*60)

# --- EJECUCIÓN PRINCIPAL ---
if __name__ == "__main__":
    print("🛠️ CONFIGURACIÓN DEL ESCENARIO DE PRUEBA 🛠️")
    print("Ingrese los datos del cliente para simular la conexión al CRM:")
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

        if bot.datos_sesion['motivo_detectado'] == 'tecnico':
            print(f"\n🤖 Agente: Hola {nombre_input}. El sistema me alerta de inconvenientes técnicos. ¿Es por eso que nos contactas?")
        elif bot.datos_sesion['motivo_detectado'] == 'precio':
            print(f"\n🤖 Agente: Hola {nombre_input}. Veo una alerta relacionada con tu facturación. ¿En qué te puedo ayudar?")
        else:
            print(f"\n🤖 Agente: Hola {nombre_input}, veo que tienes un plan de {plan_input}Mbps activo. ¿En qué puedo ayudarte?") 

        continuar = True
        while continuar:
            usuario_input = input(f"👤 {nombre_input}: ")
            if usuario_input.lower() == "exit": break
            time.sleep(0.5)
            respuesta = bot.generar_respuesta(usuario_input)
            print(f"🤖 Agente: {respuesta}")
            if bot.datos_sesion['decision_final'] != "En proceso":
                bot.reporte_final()
                continuar = False

    except ValueError:
        print("❌ ERROR: Por favor ingresa solo números en los campos de Plan, Fallas y Reclamos.")
