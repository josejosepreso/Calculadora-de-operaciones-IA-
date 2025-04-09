# entrenamiento.py
import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models
import cv2
import os
import json
from sklearn.model_selection import train_test_split

class myCallback(tf.keras.callbacks.Callback):
  def on_epoch_end(self, epoch, logs={}):
    print(logs)
    if(logs.get('accuracy') > 0.99):
      self.model.stop_training = True

# Configuración
TAMAÑO_ENTRADA = (128, 128)  # Tamaño para cada dígito/operador
RUTA_MODELO = 'modelo_clasificador.keras'
RUTA_JSON = 'datos.json'
CARPETA_IMAGENES = 'imagenes'

# Mapeo de caracteres a etiquetas
MAPEO_CARACTERES = {
    '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, 
    '6': 6, '7': 7, '8': 8, '9': 9, 
    '+': 10, '-': 11, '*': 12, '/': 13
}

def crear_modelo_clasificador(input_shape=(128, 128, 1), num_classes=14):
    """Crea un modelo CNN para clasificar dígitos y operadores"""
    model = models.Sequential([
        layers.Conv2D(32, (3, 3), activation='relu', input_shape=input_shape),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(64, (3, 3), activation='relu'),
        layers.MaxPooling2D((2, 2)),
        layers.Conv2D(128, (3, 3), activation='relu'),
        layers.MaxPooling2D((2, 2)),
        layers.Flatten(),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(num_classes, activation='softmax')
    ])
    
    model.compile(optimizer='adam',
                 loss='sparse_categorical_crossentropy',
                 metrics=['accuracy'])
    return model

def redimensionar_componente(componente, tamaño=TAMAÑO_ENTRADA):
    """Redimensiona un componente manteniendo relación de aspecto"""
    h, w = componente.shape
    escala = min(tamaño[0]/h, tamaño[1]/w)
    nueva_h, nueva_w = int(h * escala), int(w * escala)
    redimensionado = cv2.resize(componente, (nueva_w, nueva_h))
    
    # Rellenar con blanco para alcanzar el tamaño deseado
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

def cargar_datos_entrenamiento():
    """Carga y prepara los datos de entrenamiento"""
    with open(RUTA_JSON, 'r') as f:
        datos = json.load(f)
    
    X = []
    y = []
    
    for item in datos:
        img_path = os.path.join(CARPETA_IMAGENES, item["imagen"])
        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            continue
        
        img = cv2.resize(img, (640, 128))
        img = img / 255.0
        
        # Segmentar la imagen
        componentes = segmentar_imagen(img)
        
        # Obtener los caracteres reales
        primer_num = str(item['resultados']['primer_numero'])
        segundo_num = str(item['resultados']['segundo_numero'])
        operador = item['resultados']['operacion']
        caracteres = list(primer_num) + [operador] + list(segundo_num)
        
        # Verificar coincidencia
        if len(componentes) != len(caracteres):
            continue
        
        # Agregar a los datos
        for comp, char in zip(componentes, caracteres):
            X.append(comp)
            y.append(MAPEO_CARACTERES[char])
    
    return np.array(X), np.array(y)

def main():
    print("Cargando datos de entrenamiento...")
    X, y = cargar_datos_entrenamiento()
    
    # Redimensionar para el modelo (agregar canal)
    X = np.expand_dims(X, -1)
    
    print(f"Datos cargados: {X.shape[0]} muestras")
    
    # Dividir en entrenamiento y validación
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2)
    
    print("Creando y entrenando modelo...")
    modelo = crear_modelo_clasificador()

    callbacks = myCallback()
    
    modelo.fit(X_train, y_train,
              epochs=5,
              batch_size=32,
              validation_data=(X_val, y_val),
              callbacks=[callbacks]
    )
    
    print(f"Guardando modelo en {RUTA_MODELO}...")
    modelo.save(RUTA_MODELO)
    print("Entrenamiento completado!")

if __name__ == "__main__":
    main()
