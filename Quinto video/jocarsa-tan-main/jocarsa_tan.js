function rgbToHsl(rgbString) {
    const match = rgbString.match(/^rgb\((\d{1,3}),\s*(\d{1,3}),\s*(\d{1,3})\)$/);
    if (!match) {
        throw new Error("Formato RGB inválido. Use 'rgb(x, y, z)'.");
    }

    let r = parseInt(match[1], 10);
    let g = parseInt(match[2], 10);
    let b = parseInt(match[3], 10);

    r /= 255;
    g /= 255;
    b /= 255;

    const max = Math.max(r, g, b);
    const min = Math.min(r, g, b);

    let h, s, l = (max + min) / 2;

    if (max === min) {
        h = s = 0; // acromático
    } else {
        const delta = max - min;
        s = l > 0.5 ? delta / (2 - max - min) : delta / (max + min);
        switch (max) {
            case r:
                h = (g - b) / delta + (g < b ? 6 : 0);
                break;
            case g:
                h = (b - r) / delta + 2;
                break;
            case b:
                h = (r - g) / delta + 4;
                break;
        }
        h /= 6;
    }

    h = Math.round(h * 360);
    s = Math.round(s * 100);
    l = Math.round(l * 100);

    return `hsl(${h}, ${s}%, ${l}%)`;
}

// Función para modificar la luminosidad en un color HSL
function modifyHslLightness(hslString, newLightness) {
    if (newLightness < 0 || newLightness > 100) {
        throw new Error("El valor de luminosidad debe estar entre 0 y 100.");
    }

    const match = hslString.match(/^hsl\((\d{1,3}),\s*(\d{1,3})%,\s*(\d{1,3})%\)$/);
    if (!match) {
        throw new Error("Formato HSL inválido. Use 'hsl(x, y%, z%)'.");
    }

    const h = parseInt(match[1], 10);
    const s = parseInt(match[2], 10);

    return `hsl(${h}, ${s}%, ${newLightness}%)`;
}

// Función para interpolar dos colores HSL
function interpolateHsl(hsl1, hsl2, percentage) {
    const match1 = hsl1.match(/^hsl\((\d{1,3}),\s*(\d{1,3})%,\s*(\d{1,3})%\)$/);
    const match2 = hsl2.match(/^hsl\((\d{1,3}),\s*(\d{1,3})%,\s*(\d{1,3})%\)$/);
    
    if (!match1 || !match2) {
        throw new Error("Formato HSL inválido para interpolación.");
    }

    let h1 = parseInt(match1[1], 10);
    let s1 = parseInt(match1[2], 10);
    let l1 = parseInt(match1[3], 10);

    let h2 = parseInt(match2[1], 10);
    let s2 = parseInt(match2[2], 10);
    let l2 = parseInt(match2[3], 10);

    let deltaH = h2 - h1;
    if (deltaH > 180) deltaH -= 360;
    if (deltaH < -180) deltaH += 360;
    let h = (h1 + percentage * deltaH) % 360;
    if (h < 0) h += 360;

    let s = s1 + percentage * (s2 - s1);
    let l = l1 + percentage * (l2 - l1);

    return `hsl(${Math.round(h)}, ${Math.round(s)}%, ${Math.round(l)}%)`;
}

// Función que actualiza el mapa de calor para las tablas con clase "jocarsa-tan"
function updateHeatMap() {
    let tablas = document.querySelectorAll(".jocarsa-tan");

    tablas.forEach(function(tabla) {
        let color = window.getComputedStyle(tabla).color;
        let bgColor = window.getComputedStyle(tabla).backgroundColor;

        if (!color || color === 'rgba(0, 0, 0, 0)' || color === 'transparent') {
            color = "rgb(255, 0, 0)";
        }

        let colorHsl = rgbToHsl(color);
        let bgColorHsl = bgColor && bgColor !== 'rgba(0, 0, 0, 0)' && bgColor !== 'transparent' ? rgbToHsl(bgColor) : null;

        let celdas = tabla.querySelectorAll("tbody td");
        let valores = [];

        celdas.forEach(function(celda) {
            let valor = parseFloat(celda.textContent);
            if (!isNaN(valor)) {
                valores.push(valor);
            }
        });

        if (valores.length === 0) {
            console.warn("No se encontraron valores numéricos en la tabla:", tabla);
            return;
        }

        let maximo = Math.max(...valores);
        let minimo = Math.min(...valores);
        let range = maximo - minimo;
        if (range === 0) range = 1;

        celdas.forEach(function(celda) {
            let valor = parseFloat(celda.textContent);
            if (isNaN(valor)) return;

            // Se fija el color del texto en negro
            celda.style.color = "black";

            // Calcula el porcentaje normalizado del valor
            let porcentaje = ((valor - minimo) / range);

            let backgroundColorHsl;
            if (bgColorHsl) {
                // Gradiente dual: interpola entre color y bgColor
                backgroundColorHsl = interpolateHsl(colorHsl, bgColorHsl, porcentaje);
            } else {
                // Gradiente simple: modifica la luminosidad
                backgroundColorHsl = modifyHslLightness(colorHsl, 100 - Math.round(porcentaje * 100 / 2));
            }

            celda.style.backgroundColor = backgroundColorHsl;
        });

        tabla.style.background = "none";
        tabla.style.color = "inherit";
    });
}

// Función para randomizar los valores numéricos en la tabla
function randomizeTableValues() {
    let tablas = document.querySelectorAll(".jocarsa-tan");
    tablas.forEach(function(tabla) {
        let celdas = tabla.querySelectorAll("tbody td");
        celdas.forEach(function(celda) {
            celda.textContent = Math.floor(Math.random() * 500) + 1;
        });
    });
}

// Actualiza el mapa de calor al cargar la página
updateHeatMap();

// Al hacer clic en el botón, se randomizan los números y se actualiza el mapa de calor
document.getElementById("randomizeButton").addEventListener("click", function() {
    randomizeTableValues();
    updateHeatMap();
});
