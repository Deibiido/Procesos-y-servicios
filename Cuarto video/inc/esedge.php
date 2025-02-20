<?php
    // Función para detectar si el navegador es Microsoft Edge
    function isEdge() {
        // Verificar que exista el User-Agent y buscar 'Edge' o 'Edg' en él
        return isset($_SERVER['HTTP_USER_AGENT']) && (strpos($_SERVER['HTTP_USER_AGENT'], 'Edge') !== false || strpos($_SERVER['HTTP_USER_AGENT'], 'Edg') !== false);
    }

    if (isEdge()) {
        $file = 'lock.txt';

        // Crear el archivo si no existe
        if (!file_exists($file)) {
            $handle = fopen($file, 'w'); // Abrir el archivo para escribir
            if ($handle) {
                fwrite($handle, "Este archivo se creó porque el navegador es Microsoft Edge.");
                fclose($handle);
            } else {
                // Aquí podrías manejar el error de no poder abrir el archivo
            }
        } else {
            // Aquí podrías manejar el caso en que el archivo ya existe
        }
    } else {
        // Aquí podrías manejar el caso en que el navegador no es Edge
    }
?>
