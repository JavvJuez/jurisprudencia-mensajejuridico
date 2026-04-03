import re
import sys
import os
import json

def generar_base_datos_json(archivo_entrada):
    if not os.path.exists(archivo_entrada):
        print(f"❌ Error: El archivo '{archivo_entrada}' no existe en esta ruta.")
        sys.exit(1)

    nombre_base = os.path.splitext(os.path.basename(archivo_entrada))[0]
    archivo_salida = f"{nombre_base}_BaseDatos.json"

    print(f"⏳ Extrayendo datos y generando JSON desde '{archivo_entrada}'...")

    with open(archivo_entrada, 'r', encoding='utf-8') as f:
        contenido = f.read()

    # Cortar los bloques respetando puntos, dos puntos o guiones
    bloques_brutos = re.split(r'\n(?=DDP\s+\d+[:\.\-]?)', '\n' + contenido)
    
    lista_json = []
    errores = []

    # Base de datos de firmas (Motor de búsqueda codicioso)
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
        matches = list(patron_completo.finditer(cuerpo_limpio))

        if matches:
            ultimo_match = matches[-1]
            texto_temas = cuerpo_limpio[:ultimo_match.start()].strip()
            firma_completa = ultimo_match.group(1).strip() 
            texto_extra = cuerpo_limpio[ultimo_match.end():].strip()
            
            firma_completa_upper = firma_completa.upper()

            # Lógica de limpieza de radicados
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

            # --- LA SEPARACIÓN Y LIMPIEZA DE TEMAS ---
            temas_separados = re.split(r'\([ivxlcdm]+\)', texto_temas, flags=re.IGNORECASE)
            
            lista_temas_limpios = []
            for t in temas_separados:
                t = t.strip()
                if t:
                    # Expresión para atrapar comillas externas (dobles, simples o tipográficas)
                    # incluso si terminan con un punto (ej: "texto".)
                    match_comillas = re.match(r'^["“”«»\'‘’](.*)["“”«»\'‘’]\.?$', t, re.DOTALL)
                    
                    if match_comillas:
                        # Extraemos todo lo que estaba adentro de las comillas externas
                        interior = match_comillas.group(1).strip()
                        # Si el original terminaba en punto, se lo devolvemos
                        if t.endswith('.'):
                            t = interior + '.'
                        else:
                            t = interior
                            
                    lista_temas_limpios.append(t)

            # --- ARMADO DEL DICCIONARIO JSON ---
            lista_json.append({
                "ddp": int(num_ddp),
                "numero_providencia": num_providencia,
                "radicacion": radicacion,
                "decision": texto_extra if texto_extra else None,
                "temas": lista_temas_limpios
            })
        else:
            errores.append(bloque)

    # Escribir el archivo JSON final
    with open(archivo_salida, 'w', encoding='utf-8') as f_out:
        json.dump(lista_json, f_out, ensure_ascii=False, indent=4)
            
    if errores:
        with open("Lineas_Para_Revision_JSON.txt", 'w', encoding='utf-8') as f:
            f.write("\n\n--- SIGUIENTE BLOQUE NO RECONOCIDO ---\n\n".join(errores))

    print(f"✅ ¡Proceso terminado!")
    print(f"   - Providencias estructuradas: {len(lista_json)}")
    print(f"   - Archivo generado: {archivo_salida}")
    print(f"   - Casos enviados a revisión manual: {len(errores)}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso incorrecto. Faltan parámetros.")
        print("Ejemplo: python generador_json.py mi_archivo.txt")
        sys.exit(1)
        
    archivo_a_procesar = sys.argv[1]
    generar_base_datos_json(archivo_a_procesar)