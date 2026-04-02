import re
import sys
import os

def estructurar_jurisprudencia(archivo_entrada, tamano_lote=500):
    if not os.path.exists(archivo_entrada):
        print(f"❌ Error: El archivo '{archivo_entrada}' no existe en esta ruta.")
        sys.exit(1)

    nombre_base = os.path.splitext(os.path.basename(archivo_entrada))[0]
    prefijo_salida = f"{nombre_base}_Estructurado"

    print(f"⏳ Procesando '{archivo_entrada}' en lotes de {tamano_lote}...")

    with open(archivo_entrada, 'r', encoding='utf-8') as f:
        contenido = f.read()

    # Cortar los bloques respetando puntos, dos puntos o guiones
    bloques_brutos = re.split(r'\n(?=DDP\s+\d+[:\.\-]?)', '\n' + contenido)
    
    providencias_exitosas = []
    errores = []

    # 1. Base de datos de firmas (Se exige que RAD y Providencia se lean como uno solo)
    patron_firma_base = (
        r'(?:'
        r'(?:AP|SP|AHP|SEP|ATP|STP|SPS|STC|AEP|CP|ATL)\s*[\d\-–]+(?:-\d+)?\.?\s*(?:RAD\.?|CASACI[ÓO]N)\s*(?:MBU-)?[\d\-]+|'
        r'(?:AP|SP|AHP|SEP|ATP|STP|SPS|STC|AEP|CP|ATL)\s*[\d\-–]+(?:-\d+)?|'
        r'(?:SENTENCIA|PROVIDENCIA|AUTO)\s*(?:NO\.\s*)?(?:T|C|SU)?\s*-?\s*(?:DEL\s+|DE\s+)?[A-Za-z0-9°\.\s\-/]*(?:DE|DEL)?\s*\d{2,4}(?:\s*JEP)?|'
        r'RAD\.?\s+(?:T|C|TRIB\.?|MBU-)?\s*-?\s*[\d\-]+(?:\s+(?:DE|DEL|de)\s+(?:[A-Za-z0-9°\.\s]+\s+(?:DE|DEL|de)\s+)?\d{2,4})?|'
        r'(?:RAD\.?|EXTRADICI[ÓO]N)\s*(?:MBU-)?[\d\-]+|'
        r'(?:C\.?U\.?I\.?:?|EXP|REF\s*EXP\.?\s*(?:No\.?)?)\s*[\d\s\(\)-]+'
        r')'
    )

    # El patrón ya no es goloso. Simplemente busca firmas.
    patron_completo = re.compile(rf'({patron_firma_base})\.?', re.IGNORECASE)

    for bloque in bloques_brutos:
        bloque = bloque.strip()
        
        if not bloque or bloque.upper().startswith('SMS') or bloque.upper().startswith('HOJAS'):
            continue

        match_ddp = re.match(r'^DDP\s+(\d+)[:\.\-]?\s*(.*)', bloque, re.DOTALL)
        if not match_ddp:
            continue

        num_ddp = match_ddp.group(1)
        cuerpo = match_ddp.group(2).strip()

        if not cuerpo:
            continue 

        cuerpo_limpio = re.sub(r'\s*\n\s*', ' ', cuerpo)
        
        # 2. NUEVA ESTRATEGIA: Encontrar todas las firmas y tomar estrictamente la última
        matches = list(patron_completo.finditer(cuerpo_limpio))

        if matches:
            ultimo_match = matches[-1]
            # Todo lo que hay antes de la última firma son temas
            texto_temas = cuerpo_limpio[:ultimo_match.start()].strip()
            # La firma real
            firma_completa = ultimo_match.group(1).strip() 
            # Si sobró algo después (como "La corte absuelve...")
            texto_extra = cuerpo_limpio[ultimo_match.end():].strip()
            
            firma_completa_upper = firma_completa.upper()

            # 3. Lógica de limpieza y clasificación
            if re.match(r'^(?:C\.?U\.?I\.?|EXP|REF\s*EXP)\b', firma_completa_upper):
                num_providencia = "No especificado"
                radicacion = firma_completa
            elif re.match(r'^(?:RAD\.?|EXTRADICI[ÓO]N)\b', firma_completa_upper) and not re.search(r'(?:AP|SP|AHP|SEP|ATP|STP|SPS|STC|AEP|CP|ATL)', firma_completa_upper):
                num_providencia = "No especificado"
                radicacion = re.sub(r'^(RAD\.?|EXTRADICI[ÓO]N)\s*', '', firma_completa, flags=re.IGNORECASE).strip()
            elif re.search(r'(?:RAD\.?|CASACI[ÓO]N)', firma_completa_upper) and re.search(r'(?:AP|SP|AHP|SEP|ATP|STP|SPS|STC|AEP|CP|ATL)', firma_completa_upper):
                partes_firma = re.split(r'\.\s*(?=RAD|CASACI[ÓO]N)', firma_completa, flags=re.IGNORECASE)
                num_providencia = partes_firma[0].strip()
                if len(partes_firma) > 1:
                    radicacion_sucia = partes_firma[1].strip()
                    radicacion = re.sub(r'^(RAD\.?|CASACI[ÓO]N)\s*', '', radicacion_sucia, flags=re.IGNORECASE).strip()
                else:
                    radicacion = ""
            else:
                num_providencia = firma_completa
                radicacion = "No especificado"

            temas_verticales = re.sub(r'(\([ivxlcdm]+\))', r'\n\1', texto_temas, flags=re.IGNORECASE).strip()
            
            etiqueta_decision = f"\n**Decisión (DDP {num_ddp}):** {texto_extra}" if texto_extra else ""

            bloque_md = f"""# PROVIDENCIA DDP {num_ddp}

**Número de Providencia (DDP {num_ddp}):** {num_providencia}
**Radicación (DDP {num_ddp}):** {radicacion}{etiqueta_decision}

**Lista de Temas (DDP {num_ddp}):**
{temas_verticales}

---
"""
            providencias_exitosas.append(bloque_md)
        else:
            errores.append(bloque)

    for i in range(0, len(providencias_exitosas), tamano_lote):
        lote = providencias_exitosas[i:i + tamano_lote]
        num_parte = (i // tamano_lote) + 1
        nombre_archivo = f"{prefijo_salida}_Parte{num_parte}.md"
        
        with open(nombre_archivo, 'w', encoding='utf-8') as f:
            f.write("\n".join(lote))
            
    if errores:
        with open("Lineas_Para_Revision.txt", 'w', encoding='utf-8') as f:
            f.write("\n\n--- SIGUIENTE BLOQUE NO RECONOCIDO ---\n\n".join(errores))

    print(f"✅ ¡Proceso terminado con éxito!")
    print(f"   - Providencias estructuradas: {len(providencias_exitosas)}")
    print(f"   - Archivos generados: {(len(providencias_exitosas) // tamano_lote) + 1} ({tamano_lote} registros c/u)")
    print(f"   - Casos enviados a revisión manual: {len(errores)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso incorrecto. Faltan parámetros.")
        print("Ejemplo: python procesador_juris.py mi_archivo.txt [tamaño_lote]")
        sys.exit(1)
        
    archivo_a_procesar = sys.argv[1]
    
    if len(sys.argv) >= 3:
        try:
            lote_personalizado = int(sys.argv[2])
            estructurar_jurisprudencia(archivo_a_procesar, tamano_lote=lote_personalizado)
        except ValueError:
            print("❌ Error: El tamaño del lote debe ser un número (ej. 1000).")
            sys.exit(1)
    else:
        estructurar_jurisprudencia(archivo_a_procesar)