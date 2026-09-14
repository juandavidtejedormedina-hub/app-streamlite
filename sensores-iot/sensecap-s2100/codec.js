/*
 * Codec organizado para SenseCAP S2100 Data Logger - Reservorios
 *
 * Trama correcta esperada:
 *   fPort      : 3
 *   Longitud   : 11 bytes
 *   Byte 1     : 0x31
 *   Byte 2     : canales 1 y 2 (0x12)
 *   Byte 3     : bandera reservada
 *   Bytes 4-7  : nivel/distancia, int32 big-endian
 *   Bytes 8-11 : temperatura, int32 big-endian
 *
 * Conversión validada con PAYLOAD_RESERVORIOS.xlsx:
 *   medida_mm    = valor 1 / 1.000
 *   medida_cm    = valor 1 / 10.000
 *   medida_m     = valor 1 / 1.000.000
 *   temperatura  = valor 2 / 1.000
 *
 * Regla de diagnóstico solicitada:
 *   Si el payload comienza en 0x12, se marca como
 *   NO_FUNCIONANDO_CORRECTAMENTE y no se calculan medidas.
 */

function decodeReservorios(fPort, bytes) {
    bytes = bytes || [];

    var lectura = {
        payload: bytes2HexString(bytes),
        estado: "PENDIENTE",
        funcionando_correctamente: false
    };

    var resultado = {
        lectura_reservorio: lectura
    };

    // Validación del puerto usado por el S2100 de reservorios.
    if (Number(fPort) !== 3) {
        marcarError(
            lectura,
            "ERROR_FPORT",
            "FPort incorrecto. Se esperaba fPort 3 y se recibio fPort " + fPort + "."
        );
        return resultado;
    }

    // No se recibió ningún byte.
    if (bytes.length === 0) {
        marcarError(
            lectura,
            "ERROR_PAYLOAD_VACIO",
            "No se recibieron datos en el payload."
        );
        return resultado;
    }

    /*
     * Trama anómala observada en campo:
     * 12010001031501000203
     *
     * No se decodifica como una medición, porque no corresponde
     * a la trama válida 0x31. Así se evita generar valores falsos.
     */
    if (bytes[0] === 0x12) {
        marcarError(
            lectura,
            "ERROR_TRAMA_12",
            "El payload inicia en 0x12 y no corresponde a una medicion valida 0x31. Revisar el sensor, la alimentacion, el cableado RS485 y la configuracion Modbus."
        );
        return resultado;
    }

    // El reservorio debe enviar una trama de medición tipo 0x31.
    if (bytes[0] !== 0x31) {
        marcarError(
            lectura,
            "ERROR_TIPO_TRAMA",
            "Tipo de trama no soportado. Se esperaba 0x31 y se recibio 0x" + byteToHex(bytes[0]) + "."
        );
        return resultado;
    }

    // La trama 0x31 con dos mediciones debe tener exactamente 11 bytes.
    if (bytes.length !== 11) {
        marcarError(
            lectura,
            "ERROR_LONGITUD",
            "Longitud incorrecta. La trama 0x31 debe tener 11 bytes y se recibieron " + bytes.length + "."
        );
        return resultado;
    }

    var canalUno = (bytes[1] >> 4) & 0x0F;
    var canalDos = bytes[1] & 0x0F;

    // Para esta instalación se esperan los canales 1 y 2.
    if (canalUno !== 1 || canalDos !== 2) {
        marcarError(
            lectura,
            "ERROR_CANALES",
            "Canales inesperados. Se esperaban los canales 1 y 2."
        );
        return resultado;
    }

    var medidaUnoRaw = readInt32BE(bytes, 3);
    var medidaDosRaw = readInt32BE(bytes, 7);

    // 0x80000000 significa que la medición no está disponible.
    if (medidaUnoRaw === null || medidaDosRaw === null) {
        lectura.medidas = {
            medida_cm: medidaUnoRaw === null ? null : round(medidaUnoRaw / 10000, 4),
            medida_m: medidaUnoRaw === null ? null : round(medidaUnoRaw / 1000000, 6),
            medida_mm: medidaUnoRaw === null ? null : round(medidaUnoRaw / 1000, 3),
            temperatura_c: medidaDosRaw === null ? null : round(medidaDosRaw / 1000, 3)
        };

        marcarError(
            lectura,
            "ERROR_MEDICION_NO_DISPONIBLE",
            "Una o más mediciones llegaron con el valor reservado 0x80000000."
        );
        return resultado;
    }

    // Salida correcta y organizada con las cuatro variables juntas.
    lectura.estado = "FUNCIONANDO_CORRECTAMENTE";
    lectura.funcionando_correctamente = true;
    lectura.medidas = {
        medida_cm: round(medidaUnoRaw / 10000, 4),
        medida_m: round(medidaUnoRaw / 1000000, 6),
        medida_mm: round(medidaUnoRaw / 1000, 3),
        temperatura_c: round(medidaDosRaw / 1000, 3)
    };

    return resultado;
}

function marcarError(lectura, codigo, mensaje) {
    lectura.estado = "NO_FUNCIONANDO_CORRECTAMENTE";
    lectura.funcionando_correctamente = false;
    lectura.error = {
        codigo: codigo,
        mensaje: mensaje
    };
}

// Interfaz compatible con el codec actualmente usado en ChirpStack.
function Decode(fPort, bytes, variables) {
    return {
        data: decodeReservorios(fPort, bytes)
    };
}

// Interfaz compatible con versiones recientes de ChirpStack.
function decodeUplink(input) {
    return {
        data: decodeReservorios(input.fPort, input.bytes)
    };
}

function readInt32BE(bytes, offset) {
    var unsignedValue =
        bytes[offset] * 16777216 +
        bytes[offset + 1] * 65536 +
        bytes[offset + 2] * 256 +
        bytes[offset + 3];

    if (unsignedValue === 2147483648) {
        return null;
    }

    return unsignedValue > 2147483647
        ? unsignedValue - 4294967296
        : unsignedValue;
}

function round(value, decimals) {
    var factor = Math.pow(10, decimals);
    return Math.round(value * factor) / factor;
}

function byteToHex(value) {
    var hex = Number(value).toString(16).toUpperCase();
    return hex.length === 1 ? "0" + hex : hex;
}

function bytes2HexString(bytes) {
    var hex = "";
    for (var i = 0; i < bytes.length; i++) {
        hex += byteToHex(bytes[i]);
    }
    return hex;
}
