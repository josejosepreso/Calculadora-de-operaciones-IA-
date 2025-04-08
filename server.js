//
//const express = require('express');
//const fs = require('fs');
//const path = require('path');
//const cors = require('cors');
//const bodyParser = require('body-parser');
//
//const app = express();
//const PORT = 3000;
//
//// Middleware
//app.use(cors());
//app.use(bodyParser.json({ limit: '10mb' }));
//
//// Carpeta donde se guardarán las imágenes
//const imageDir = path.join(__dirname, 'imagenes');
//if (!fs.existsSync(imageDir)) {
//    fs.mkdirSync(imageDir);
//}
//
//// Función para calcular el resultado de una operación
//function calcularOperacion(operacion) {
//    const match = operacion.match(/(\d+)([+\-*/])(\d+)/);
//    if (!match) return null;
//
//    const num1 = parseInt(match[1]);
//    const operador = match[2];
//    const num2 = parseInt(match[3]);
//    let resultado;
//
//    switch (operador) {
//        case '+': resultado = num1 + num2; break;
//        case '-': resultado = num1 - num2; break;
//        case '*': resultado = num1 * num2; break;
//        case '/': resultado = num2 !== 0 ? num1 / num2 : null; break;
//        default: return null;
//    }
//
//    return { numeros: [num1, num2], operacion: operador, resultado };
//}
//
//// Ruta para guardar la imagen y actualizar JSON
//app.post('/guardar', (req, res) => {
//    const { imagen, operacion } = req.body;
//    
//    if (!imagen || !operacion) {
//        return res.status(400).json({ error: 'Faltan datos en la solicitud' });
//    }
//
//    // Leer el archivo JSON existente o crear uno nuevo
//    const jsonFilePath = path.join(__dirname, 'datos.json');
//    let jsonData = [];
//    
//    if (fs.existsSync(jsonFilePath)) {
//        const jsonContent = fs.readFileSync(jsonFilePath, 'utf-8');
//        jsonData = jsonContent ? JSON.parse(jsonContent) : [];
//    }
//
//    // Nombre de la imagen (img_001.png, img_002.png, etc.)
//    const fileName = `img_${String(jsonData.length + 1).padStart(3, '0')}.png`;
//    const imagePath = path.join(imageDir, fileName);
//
//    // Guardar la imagen en la carpeta
//    const base64Data = imagen.replace(/^data:image\/png;base64,/, "");
//    fs.writeFileSync(imagePath, base64Data, 'base64');
//
//    // Calcular los resultados
//    const resultados = calcularOperacion(operacion);
//
//    // Agregar la nueva entrada al JSON
//    jsonData.push({ imagen: fileName, operacion, resultados });
//    fs.writeFileSync(jsonFilePath, JSON.stringify(jsonData, null, 4));
//
//    res.json({ mensaje: 'Imagen guardada y JSON actualizado', archivo: fileName });
//});
//
//// Iniciar el servidor
//app.listen(PORT, () => {
//    console.log(`Servidor corriendo en http://localhost:${PORT}`);
//});

const express = require('express');
const fs = require('fs');
const path = require('path');
const cors = require('cors');
const bodyParser = require('body-parser');

const app = express();
const PORT = 3000;

// Middleware
app.use(cors());
app.use(bodyParser.json({ limit: '10mb' }));

// Carpeta donde se guardarán las imágenes
const imageDir = path.join(__dirname, 'imagenes');
if (!fs.existsSync(imageDir)) {
    fs.mkdirSync(imageDir);
}

// Función para calcular el resultado de una operación
function calcularOperacion(operacion) {
    const match = operacion.match(/(\d+)([+\-*/])(\d+)/);
    if (!match) return null;

    const num1 = parseInt(match[1]);
    const operador = match[2];
    const num2 = parseInt(match[3]);
    let resultado;

    switch (operador) {
        case '+': resultado = num1 + num2; break;
        case '-': resultado = num1 - num2; break;
        case '*': resultado = num1 * num2; break;
        case '/': resultado = num2 !== 0 ? num1 / num2 : null; break;
        default: return null;
    }

    return { 
        primer_numero: num1, 
        segundo_numero: num2, 
        operacion: operador, 
        resultado: resultado 
    };
}

// Ruta para guardar la imagen y actualizar JSON
app.post('/guardar', (req, res) => {    
    const { imagen, operacion, prediccion } = req.body;
    
    if ((!imagen || !operacion) && !prediccion) {
        return res.status(400).json({ error: 'Faltan datos en la solicitud' });
    }

    // Leer el archivo JSON existente o crear uno nuevo
    const jsonFilePath = path.join(__dirname, 'datos.json');
    let jsonData = [];
    
    if (fs.existsSync(jsonFilePath)) {
        const jsonContent = fs.readFileSync(jsonFilePath, 'utf-8');
        jsonData = jsonContent ? JSON.parse(jsonContent) : [];
    }

    // Nombre de la imagen (img_001.png, img_002.png, etc.)
    const fileName = `img_${String(jsonData.length + 1).padStart(3, '0')}.png`;
    const imagePath = path.join(imageDir, fileName);

    // Guardar la imagen en la carpeta
    const base64Data = imagen.replace(/^data:image\/png;base64,/, "");
    fs.writeFileSync(imagePath, base64Data, 'base64');

    // Calcular los resultados
    const resultados = calcularOperacion(operacion);

    // Agregar la nueva entrada al JSON
    jsonData.push({ imagen: fileName, operacion, resultados });
    fs.writeFileSync(jsonFilePath, JSON.stringify(jsonData, null, 4));

    if (req.body.prediccion) {
	let resp = "";
	
	fetch("http://localhost:5000/", {
	    method: "POST",
	    headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
		img_name: fileName
	    })
	})
	    .then(res => res.json())
	    .then(data => {
		res.status(200).json({ response: data, predict: true });
	    })
	    .catch(err => {
		console.log(err);
	    });
	
	return;
    }

    res.json({ mensaje: 'Imagen guardada y JSON actualizado', archivo: fileName, predict: false });    
});

// Iniciar el servidor
app.listen(PORT, () => {
    console.log(`Servidor corriendo en http://localhost:${PORT}`);
});

