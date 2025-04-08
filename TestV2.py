# test.py
import numpy as np
import tensorflow as tf
import cv2
import os

# Configuración
TAMAÑO_ENTRADA = (128, 128)
RUTA_MODELO = 'modelo_clasificador.keras'

# Mapeo inverso (etiquetas a caracteres)
MAPEO_INVERSO = {
    0: '0', 1: '1', 2: '2', 3: '3', 4: '4', 5: '5', 
    6: '6', 7: '7', 8: '8', 9: '9', 
    10: '+', 11: '-', 12: '*', 13: '/'
}

def cargar_modelo():
    """Carga el modelo entrenado"""
    return tf.keras.models.load_model(RUTA_MODELO)

def redimensionar_componente(componente, tamaño=TAMAÑO_ENTRADA):
    """Redimensiona un componente manteniendo relación de aspecto"""
    h, w = componente.shape
    escala = min(tamaño[0]/h, tamaño[1]/w)
    nueva_h, nueva_w = int(h * escala), int(w * escala)
    redimensionado = cv2.resize(componente, (nueva_w, nueva_h))
    
    # Rellenar con blanco
    delta_h = tamaño[0] - nueva_h
    delta_w = tamaño[1] - nueva_w
    top = delta_h // 2
    bottom = delta_h - top
    left = delta_w // 2
    right = delta_w - left
    
    return cv2.copyMakeBorder(redimensionado, top, bottom, left, right, 
                             cv2.BORDER_CONSTANT, value=1.0)

def segmentar_imagen(imagen, min_ancho=20, min_altura=40):
    """Segmenta la imagen en componentes individuales"""
    # Binarizar la imagen
    _, binaria = cv2.threshold(imagen, 0.5, 1.0, cv2.THRESH_BINARY_INV)
    binaria = binaria.astype(np.uint8)
    
    # Encontrar componentes conectados
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(binaria)
    
    componentes = []
    for i in range(1, num_labels):
        x, y, w, h, area = stats[i]
        
        # Filtrar componentes pequeños
        if w >= min_ancho and h >= min_altura:
            componente = imagen[y:y+h, x:x+w]
            componente = redimensionar_componente(componente)
            componentes.append((x, componente))
    
    # Ordenar componentes de izquierda a derecha
    componentes.sort(key=lambda c: c[0])
    return [comp for (x, comp) in componentes]

def procesar_operacion(imagen, modelo):
    """Procesa una imagen completa con una operación matemática"""
    # Preprocesar imagen
    if len(imagen.shape) == 3 and imagen.shape[2] == 3:
        imagen = cv2.cvtColor(imagen, cv2.COLOR_BGR2GRAY)
    imagen = cv2.resize(imagen, (640, 128))
    imagen = imagen / 255.0
    
    # Segmentar la imagen
    componentes = segmentar_imagen(imagen)
    
    # Clasificar cada componente
    caracteres = []
    for comp in componentes:
        # Preparar para el modelo
        comp_input = np.expand_dims(np.expand_dims(comp, -1), 0)
        pred = modelo.predict(comp_input, verbose=0)
        etiqueta = np.argmax(pred)
        caracteres.append(MAPEO_INVERSO[etiqueta])
    
    # Construir y evaluar la operación
    operacion = ''.join(caracteres)
    
    try:
        resultado = eval(operacion)
    except:
        resultado = None
    
    return {
        'operacion': operacion,
        'resultado': resultado,
        'componentes': caracteres
    }

def main(file_path):
    # Cargar modelo
    print(f"Cargando modelo desde {RUTA_MODELO}...")
    modelo = cargar_modelo()
    
    # Procesar imágenes de prueba
    carpeta_pruebas = './imagene'
    if os.path.exists(carpeta_pruebas):
        print("\nProcesando imágenes de prueba:")
        for archivo in os.listdir(carpeta_pruebas):
            if archivo.lower().endswith(('.png', '.jpg', '.jpeg')):
                ruta_imagen = os.path.join(carpeta_pruebas, archivo)
                imagen = cv2.imread(ruta_imagen)
                
                resultado = procesar_operacion(imagen, modelo)
                
                print(f"\nImagen: {archivo}")
                print(f"Operación detectada: {resultado['operacion']}")
                print(f"Resultado calculado: {resultado['resultado']}")
                print(f"Componentes: {resultado['componentes']}")
    else:
        print(f"\nCarpeta '{carpeta_pruebas}' no encontrada. Crea una carpeta con imágenes para probar.")

    # Ejemplo con imagen específica
    # ejemplo_path = './imagenes/img_174.png'
    ejemplo_path = './imagenes/' + file_path
    resultado = ""
    if os.path.exists(ejemplo_path):
        # print("\nProcesando imagen de ejemplo:")
        imagen = cv2.imread(ejemplo_path)
        resultado = procesar_operacion(imagen, modelo)
        """
        print(f"\nImagen: {ejemplo_path}")
        print(f"Operación detectada: {resultado['operacion']}")
        print(f"Resultado calculado: {resultado['resultado']}")
        print(f"Componentes: {resultado['componentes']}")
        """
        
    return str(resultado)

if __name__ == "__main__":
    main()
