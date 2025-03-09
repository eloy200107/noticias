<?php

error_reporting(E_ALL);
ini_set('display_errors', 0);
ini_set('log_errors', 1);
ini_set('error_log', 'D:/XAMPP/htdocs/php_error.log'); // Guardar errores en un log

if (php_sapi_name() === "cli" || $_SERVER['REQUEST_METHOD'] === 'POST') {
    header('Content-Type: application/json');
    
    // Determinar la fuente de entrada
    if (!empty($_POST['text'])) {
        $text = isset($_POST['text']) && !empty($_POST['text']) ? trim($_POST['text']) : '';
    } elseif (!empty($_POST['url'])) {
        $url = trim($_POST['url']);
        $text = obtenerTextoDesdeURL($url);
    } elseif (!empty($_FILES['file']['tmp_name'])) {
        $text = file_get_contents($_FILES['file']['tmp_name']);
    } else {
        echo json_encode(['error' => 'No se recibió ninguna entrada']);
        exit;
    }
    
    // Si no hay texto válido
    if (empty($text)) {
        echo json_encode(['error' => 'No se pudo extraer texto válido']);
        exit;
    }
    
    // Ejecutar Python para obtener la categoría
    $pythonPath = "D:/Python 3.12.2/python.exe";
    $scriptPath = "D:/XAMPP/htdocs/modelo_noticias.py";
    $command = "\"$pythonPath\" \"$scriptPath\" " . escapeshellarg($text);
    $output = shell_exec($command . " 2>&1"); // Captura errores de Python también

    // Registrar el comando ejecutado y la salida
    file_put_contents("D:/XAMPP/htdocs/debug.txt", "Comando ejecutado: $command\nSalida: $output");

    if ($output === null) {
        echo json_encode(['error' => 'Error al ejecutar el script de Python']);
        exit;
    }
    
    // Enviar respuesta JSON
    echo json_encode(['category' => trim($output)]);
    exit;
}

// Función para extraer texto de una URL
function obtenerTextoDesdeURL($url) {
    $html = @file_get_contents($url);
    if (!$html) return '';
    
    libxml_use_internal_errors(true);
    $dom = new DOMDocument();
    $dom->loadHTML($html);
    $xpath = new DOMXPath($dom);
    
    $parrafos = $xpath->query('//p');
    $texto = '';
    foreach ($parrafos as $p) {
        $texto .= $p->nodeValue . " ";
        if (strlen($texto) > 500) break; // Limitar la cantidad de texto
    }
    
    return trim($texto);
}

?>
