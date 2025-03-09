// Función para cambiar de sección al hacer clic en un botón
function showSection(tipo) {
    // Ocultar todas las secciones
    document.querySelectorAll('.input-section').forEach(seccion => {
        seccion.style.display = 'none';
    });

    // Mostrar la sección correspondiente
    const seccionMostrar = document.getElementById(tipo);
    if (seccionMostrar) {
        seccionMostrar.style.display = 'block';
    }

    // Remover la clase 'active' de todos los botones
    document.querySelectorAll('.input-group button').forEach(btn => {
        btn.classList.remove('active');
    });

    // Añadir la clase 'active' al botón correspondiente
    const activeButton = document.querySelector(`button[data-section="${tipo}"]`);
    if (activeButton) {
        activeButton.classList.add('active');
    }
}

// Función para detectar la categoría de la noticia
function detectarSeccion(contenido) {
    const palabrasClave = {
        "Alimentación": ["comida", "nutrición", "alimento"],
        "Astronomía": ["planetas", "espacio", "NASA"],
        "Deportes": ["fútbol", "baloncesto", "tenis"],
        "Economía": ["bolsa", "dinero", "mercado"],
        "Informática": ["computadora", "programación", "software"],
        "Política": ["gobierno", "elecciones", "senado"],
        "Salud": ["hospital", "medicina", "enfermedad"]
    };

    contenido = contenido.toLowerCase();  // Convertimos a minúsculas para evitar problemas

    let categoriaDetectada = "Desconocido";
    let maxCoincidencias = 0;

    for (const [categoria, palabras] of Object.entries(palabrasClave)) {
        let coincidencias = palabras.filter(palabra => contenido.includes(palabra)).length;
        if (coincidencias > maxCoincidencias) {
            maxCoincidencias = coincidencias;
            categoriaDetectada = categoria;
        }
    }

    return categoriaDetectada;
}

// Función para clasificar el contenido usando la red neuronal (simulación)
async function clasificarConRedNeuronal(contenido) {
    try {
        const response = await fetch('http://localhost:5000/predict/text', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text: contenido })
        });

        if (!response.ok) {
            throw new Error('Error al clasificar la noticia');
        }

        const data = await response.json();
        return data.category;
    } catch (error) {
        console.error('Error:', error);
        return "Desconocido";
    }
}

// Función para analizar el contenido
async function analizarContenido(tipo) {
    try {
        let contenido = '';

        if (tipo === 'url') {
            const url = document.getElementById('urlInput').value.trim();
            if (!url) throw new Error('Introduce una URL válida');
            contenido = await obtenerContenidoURL(url);
        }
        else if (tipo === 'file') {
            const archivo = document.getElementById('fileInput').files[0];
            if (!archivo) throw new Error('Selecciona un archivo');
            contenido = await leerArchivo(archivo);
        }

        if (!contenido) throw new Error('No se encontró un párrafo válido');

        // Detectar la categoría de la noticia (por ejemplo, usando la detección de palabras clave)
        const seccion = detectarSeccion(contenido);

        // Descargar el archivo .txt con el contenido y la categoría
        descargarNoticia(contenido, seccion);

    } catch (error) {
        mostrarError(error.message);
    }
}




// Función para obtener el color según la categoría
function getColor(categoria) {
    const colores = {
        "Alimentación": "#FF9800",
        "Astronomía": "#673AB7",
        "Deportes": "#E91E63",
        "Economía": "#2196F3",
        "Informática": "#009688",
        "Política": "#3F51B5",
        "Salud": "#4CAF50"
    };
    return colores[categoria] || "#607D8B"; // Color gris por defecto
}

// Función para mostrar el resultado
function mostrarResultadoCombinado(seccion, prediccionNeuronal) {
    const resultDiv = document.getElementById('result');
    resultDiv.textContent = `Sección: ${seccion} | Predicción: ${prediccionNeuronal}`;
    resultDiv.style.backgroundColor = getColor(seccion);
    resultDiv.classList.add('con-resultado');
}

// Función para mostrar un error
function mostrarError(mensaje) {
    const resultDiv = document.getElementById('result');
    resultDiv.textContent = `Error: ${mensaje}`;
    resultDiv.style.backgroundColor = '#FF6B6B';
    resultDiv.classList.remove('con-resultado');
}

// Función para obtener el primer párrafo del contenido
// Función para obtener el contenido de una URL
// Función para obtener el contenido de una URL
async function obtenerContenidoURL(url) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error('Error al obtener el contenido de la URL');
        }

        // Obtener el texto de la página (esto es una simplificación)
        const text = await response.text();

        if (text.trim() === '') {
            throw new Error('La URL no contiene contenido visible.');
        }

        // Extraer el primer párrafo (esto es solo un ejemplo, puedes mejorar la extracción)
        return obtenerPrimerParrafo(text);
    } catch (error) {
        console.error("Error al obtener contenido de la URL:", error);
        throw new Error("No se pudo obtener el contenido de la URL");
    }
}


// Función para obtener el primer párrafo del contenido
function obtenerPrimerParrafo(contenido) {
    const div = document.createElement('div');
    div.innerHTML = contenido;

    // Suponemos que el primer párrafo es el primero dentro del <body>
    const primerParrafo = div.querySelector('p');
    return primerParrafo ? primerParrafo.textContent : '';
}



function leerArchivo(archivo) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        
        if (archivo.type === "application/pdf") {
            // Usar pdf.js para leer PDF
            reader.onload = async (event) => {
                const pdfData = new Uint8Array(event.target.result);
                try {
                    const pdf = await pdfjsLib.getDocument({ data: pdfData }).promise;
                    let text = "";

                    // Extraer texto de todas las páginas
                    for (let i = 1; i <= pdf.numPages; i++) {
                        const page = await pdf.getPage(i);
                        const content = await page.getTextContent();
                        text += content.items.map(item => item.str).join(" ") + "\n";
                    }

                    // Resolver con el texto extraído
                    resolve(text.trim());
                } catch (error) {
                    reject("Error al leer el archivo PDF: " + error.message);
                }
            };
            reader.readAsArrayBuffer(archivo);
        } else {
            // Leer como texto normal si no es un PDF
            reader.onload = (event) => resolve(event.target.result);
            reader.readAsText(archivo);
        }

        reader.onerror = (error) => reject(error);
    });
}






// Función para descargar la noticia como archivo .txt
// Función para descargar el archivo .txt con el contenido
function descargarNoticia(contenido, categoria) {
    const blob = new Blob([contenido], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement("a");
    a.href = url;
    a.download = `Noticia_${categoria}.txt`;  // El nombre del archivo incluirá la categoría
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}




fetch("http://localhost:5000/predict/url", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url: "https://ejemplo.com/noticia" })
})
.then(response => response.json())
.then(data => console.log(data))
.catch(error => console.error("Fetch error:", error));
