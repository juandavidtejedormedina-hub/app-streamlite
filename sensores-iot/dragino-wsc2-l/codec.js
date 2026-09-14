/*
 * Dragino WSC2-L - Decoder para ChirpStack v4
 *
 * Correcciones principales:
 *   - El mapa de segmentos dinamicos empieza en 0x00.
 *   - 0x00 = velocidad del viento (WSS-22).
 *   - 0x01 = angulo/direccion del viento (WSS-22).
 *   - 0x0B = PAR (WSS-27).
 *   - A1..A4 son canales RS485 DIY y no se usan como alias de WSS-22/WSS-27.
 *   - Se filtran los codigos de sensor ausente/error para evitar valores falsos.
 */

function decodeUplink(input) {
    return {
        data: Decode(input.fPort, input.bytes, input.variables)
    };
}

function Decode(fPort, bytes, variables) {
    if (!bytes || bytes.length === 0) {
        return { error: "Payload vacio" };
    }

    if (fPort === 0x05) {
        return decodeDeviceStatus(bytes);
    }

    if (fPort === 0x02) {
        return decodeSensorPayload(bytes);
    }

    return { error: "FPort no soportado: " + fPort };
}

function decodeDeviceStatus(bytes) {
    if (bytes.length < 7) {
        return { error: "Payload FPort 5 demasiado corto" };
    }

    var frequencyBands = {
        0x01: "EU868",
        0x02: "US915",
        0x03: "IN865",
        0x04: "AU915",
        0x05: "KZ865",
        0x06: "RU864",
        0x07: "AS923",
        0x08: "AS923_1",
        0x09: "AS923_2",
        0x0A: "AS923_3",
        0x0B: "CN470",
        0x0C: "EU433",
        0x0D: "KR920",
        0x0E: "MA869",
        0x0F: "AS923_4"
    };

    return {
        SENSOR_MODEL: bytes[0] === 0x2E ? "WSC2-L" : "UNKNOWN",
        FIRMWARE_VERSION:
            (bytes[1] & 0x0F) + "." +
            ((bytes[2] >> 4) & 0x0F) + "." +
            (bytes[2] & 0x0F),
        FREQUENCY_BAND: frequencyBands[bytes[3]] || "UNKNOWN",
        SUB_BAND: bytes[4] === 0xFF ? "NULL" : bytes[4],
        BAT: round(u16(bytes, 5) / 1000, 3)
    };
}

function decodeSensorPayload(bytes) {
    var decode = {};

    if (bytes.length < 11) {
        return { error: "Payload FPort 2 demasiado corto" };
    }

    decode.BatV = round((u16(bytes, 0) & 0x3FFF) / 1000, 3);
    decode.Payload_Ver = bytes[2];

    var factor = bytes[9] & 0x0F;
    var divisor = bytes[10];
    var rainRaw = u32(bytes, 3);

    decode.rain = factor > 0 && divisor > 0
        ? round(rainRaw * factor / divisor, 3)
        : 0;

    var dsRaw = u16(bytes, 7);
    var dsSigned = s16(dsRaw);

    if (
        dsRaw === 0xFFFF ||
        dsRaw === 0x0CCC ||
        dsSigned < -400 ||
        dsSigned > 800
    ) {
        decode.temp_DS18B20 = null;
    } else {
        decode.temp_DS18B20 = round(dsSigned / 10, 1);
    }

    decode.i_flag = (bytes[9] >> 5) & 0x01;
    decode.Mod = (bytes[9] >> 7) & 0x01;

    var i = 11;

    /* Payload fijo antiguo. Los segmentos adicionales empiezan en el byte 39. */
    if (decode.Payload_Ver === 1) {
        if (bytes.length < 39) {
            decode.error = "Payload version 1 incompleto";
            return decode;
        }

        decodeFixedPayloadV1(decode, bytes);
        i = 39;
    }

    /* Payload fijo del WSS integrado. Los segmentos extra empiezan en el byte 21. */
    if (decode.Payload_Ver === 4) {
        if (bytes.length < 21) {
            decode.error = "Payload version 4 incompleto";
            return decode;
        }

        decodeFixedPayloadV4(decode, bytes);
        i = 21;
    }

    while (i + 1 < bytes.length) {
        var sensorType = bytes[i];
        var len = bytes[i + 1];
        var dataStart = i + 2;
        var next = dataStart + len;

        if (next > bytes.length) {
            decode.payload_warning =
                "Segmento 0x" + toHex(sensorType, 2) + " incompleto";
            break;
        }

        /* Un segmento de longitud cero no contiene una medicion. */
        if (len === 0) {
            i = next;
            continue;
        }

        if (sensorType >= 0xA1 && sensorType <= 0xA4) {
            decodeDiySensor(decode, bytes, sensorType, dataStart, len);
        } else {
            decodeStandardSensor(decode, bytes, sensorType, dataStart, len);
        }

        i = next;
    }

    updateWss22Status(decode);
    return decode;
}

function decodeFixedPayloadV1(decode, bytes) {
    decode.wind_speed = validOrScaled(u16(bytes, 11), 10);
    decode.wind_speed_max = validOrScaled(u16(bytes, 13), 10);
    decode.wind_speed_average = validOrScaled(u16(bytes, 15), 10);
    decode.wind_speed_level = validOrValue(u16(bytes, 17));
    decode.wind_direction_index = validOrValue(u16(bytes, 19));
    decode.wind_direction = directionName(decode.wind_direction_index);
    decode.wind_direction_angle = validOrScaled(u16(bytes, 21), 10);
    decode.wind_angle = decode.wind_direction_angle;
    decode.Humidity = validOrScaled(u16(bytes, 23), 10);
    decode.Temperature = signedOrScaled(u16(bytes, 25), 10);
    decode.Noise = validOrScaled(u16(bytes, 27), 10);

    if (decode.Mod === 0) {
        decode.CO2 = validOrValue(u16(bytes, 29));
    } else {
        decode.PM2_5 = validOrValue(u16(bytes, 29));
        decode.PM10 = validOrValue(u16(bytes, 31));
    }

    decode.Pressure = validOrScaled(u16(bytes, 33), 10);
    decode.illumination = u32(bytes, 35);
}

function decodeFixedPayloadV4(decode, bytes) {
    decode.WSS_Humidity = validOrScaled(u16(bytes, 11), 10);
    decode.WSS_Temperature = signedOrScaled(u16(bytes, 13), 10);
    decode.WSS_Pressure = validOrScaled(u16(bytes, 15), 10);
    decode.WSS_illumination = u32(bytes, 17);
}

function decodeStandardSensor(decode, bytes, sensorType, start, len) {
    switch (sensorType) {
        case 0x00:
            decodeWindSpeed(decode, bytes, start, len);
            break;

        case 0x01:
            decodeWindDirection(decode, bytes, start, len);
            break;

        case 0x02:
            /* Iluminacion: el formato dinamico usa un valor de 16 bits x 10. */
            if (len >= 4) {
                decode.illumination = u32(bytes, start);
            } else if (len >= 2) {
                var illuminationRaw = u16(bytes, start);
                decode.illumination = illuminationRaw === 0xFFFF
                    ? null
                    : illuminationRaw * 10;
            }
            break;

        case 0x03:
            decode.rain_snow = bytes[start] === 0xFF ? null : bytes[start];
            break;

        case 0x04:
            if (len >= 2) {
                decode.CO2 = validOrValue(u16(bytes, start));
                decode["WSS-CO2"] = decode.CO2;
            }
            break;

        case 0x05:
            if (len >= 2) {
                decode.Temperature = signedOrScaled(u16(bytes, start), 10);
                decode.TEM = decode.Temperature;
            }
            break;

        case 0x06:
            if (len >= 2) {
                decode.Humidity = validOrScaled(u16(bytes, start), 10);
                decode.HUM = decode.Humidity;
            }
            break;

        case 0x07:
            if (len >= 2) {
                decode.Pressure = validOrScaled(u16(bytes, start), 10);
                decode.pressure = decode.Pressure;
            }
            break;

        case 0x08:
            if (len >= 2) {
                decode.rain_gauge = validOrScaled(u16(bytes, start), 10);
            }
            break;

        case 0x09:
            if (len >= 2) {
                decode.PM2_5 = validOrValue(u16(bytes, start));
            }
            break;

        case 0x0A:
            if (len >= 2) {
                decode.PM10 = validOrValue(u16(bytes, start));
            }
            break;

        case 0x0B:
            /* WSS-27: radiacion fotosinteticamente activa (PAR). */
            if (len >= 2) {
                var parRaw = u16(bytes, start);
                decode.WSS27_raw = toHex(parRaw, 4);

                if (parRaw === 0xFFFF) {
                    decode.PAR = null;
                    decode.WSS27_PAR = null;
                    decode.WSS27_status = "NO_VALID_DATA";
                } else {
                    decode.PAR = parRaw;
                    decode.WSS27_PAR = parRaw;
                    decode.WSS27_status = "OK";
                }
            }
            break;

        case 0x0C:
            if (len >= 2) {
                decode.TSR = validOrScaled(u16(bytes, start), 10);
            }
            break;

        default:
            /* Sensor estandar desconocido: se conserva el segmento en HEX. */
            decode["sensor_0x" + toHex(sensorType, 2) + "_raw"] =
                bytesToHex(bytes, start, len);
            break;
    }
}

function decodeWindSpeed(decode, bytes, start, len) {
    if (len < 2) {
        decode.WSS22_speed_status = "NO_VALID_DATA";
        return;
    }

    var speedRaw = u16(bytes, start);

    if (speedRaw === 0x02FE) {
        setWindSpeedNull(decode);
        decode.WSS22_speed_status = "NO_SENSOR";
        return;
    }

    if (speedRaw === 0x02EE) {
        setWindSpeedNull(decode);
        decode.WSS22_speed_status = "VALUE_ERROR";
        return;
    }

    if (speedRaw === 0xFFFF) {
        setWindSpeedNull(decode);
        decode.WSS22_speed_status = "NO_VALID_DATA";
        return;
    }

    decode.wind_speed = round(speedRaw / 10, 1);

    if (len >= 7) {
        decode.wind_speed_max = validOrScaled(u16(bytes, start + 2), 10);
        decode.wind_speed_average = validOrScaled(u16(bytes, start + 4), 10);

        var level = bytes[start + 6];
        decode.wind_speed_level = level <= 17 ? level : null;

        if (level === 0x15) {
            decode.WSS22_speed_status = "VALUE_ERROR";
        } else if (level === 0x14) {
            decode.WSS22_speed_status = "NO_SENSOR";
        } else {
            decode.WSS22_speed_status = "OK";
        }
    } else {
        decode.WSS22_speed_status = "OK";
    }
}

function decodeWindDirection(decode, bytes, start, len) {
    if (len < 2) {
        decode.WSS22_direction_status = "NO_VALID_DATA";
        return;
    }

    var angleRaw = u16(bytes, start);

    if (angleRaw === 0x0EFE) {
        setWindDirectionNull(decode);
        decode.WSS22_direction_status = "NO_SENSOR";
        return;
    }

    if (angleRaw === 0x0EEE) {
        setWindDirectionNull(decode);
        decode.WSS22_direction_status = "VALUE_ERROR";
        return;
    }

    if (angleRaw === 0xFFFF) {
        setWindDirectionNull(decode);
        decode.WSS22_direction_status = "NO_VALID_DATA";
        return;
    }

    decode.wind_direction_angle = round(angleRaw / 10, 1);
    decode.wind_angle = decode.wind_direction_angle;

    if (len >= 3) {
        var directionIndex = bytes[start + 2];

        if (directionIndex === 0x14) {
            decode.wind_direction_index = null;
            decode.wind_direction = null;
            decode.WSS22_direction_status = "NO_SENSOR";
        } else if (directionIndex === 0x15) {
            decode.wind_direction_index = null;
            decode.wind_direction = null;
            decode.WSS22_direction_status = "VALUE_ERROR";
        } else if (directionIndex <= 15) {
            decode.wind_direction_index = directionIndex;
            decode.wind_direction = directionName(directionIndex);
            decode.WSS22_direction_status = "OK";
        } else {
            decode.wind_direction_index = null;
            decode.wind_direction = null;
            decode.WSS22_direction_status = "NO_VALID_DATA";
        }
    } else {
        decode.WSS22_direction_status = "OK";
    }
}

function decodeDiySensor(decode, bytes, sensorType, start, len) {
    var sensorName = "A" + (sensorType - 0xA0);
    var rawHex = bytesToHex(bytes, start, len);

    decode[sensorName + "_raw"] = rawHex;

    if (len < 2) {
        decode[sensorName] = null;
        decode[sensorName + "_status"] = "NO_VALID_DATA";
        return;
    }

    var rawValue = u16(bytes, start);

    if (rawValue === 0xFFFF) {
        decode[sensorName] = null;
        decode[sensorName + "_status"] = "NO_VALID_DATA";
    } else {
        decode[sensorName] = rawValue;
        decode[sensorName + "_status"] = "OK";
    }

    /*
     * Importante: A2 no se copia a WSS27_PAR.
     * El WSS-27 nativo llega en el segmento 0x0B.
     */
}

function setWindSpeedNull(decode) {
    decode.wind_speed = null;
    decode.wind_speed_max = null;
    decode.wind_speed_average = null;
    decode.wind_speed_level = null;
}

function setWindDirectionNull(decode) {
    decode.wind_direction_angle = null;
    decode.wind_angle = null;
    decode.wind_direction_index = null;
    decode.wind_direction = null;
}

function updateWss22Status(decode) {
    var speed = decode.WSS22_speed_status;
    var direction = decode.WSS22_direction_status;

    if (speed === undefined && direction === undefined) {
        return;
    }

    if (speed === "VALUE_ERROR" || direction === "VALUE_ERROR") {
        decode.WSS22_status = "VALUE_ERROR";
    } else if (speed === "NO_SENSOR" || direction === "NO_SENSOR") {
        decode.WSS22_status = "NO_SENSOR";
    } else if (speed === "NO_VALID_DATA" || direction === "NO_VALID_DATA") {
        decode.WSS22_status = "NO_VALID_DATA";
    } else if (
        (speed === "OK" || speed === undefined) &&
        (direction === "OK" || direction === undefined)
    ) {
        decode.WSS22_status = "OK";
    }
}

function directionName(index) {
    var directions = {
        0: "N",
        1: "NNE",
        2: "NE",
        3: "ENE",
        4: "E",
        5: "ESE",
        6: "SE",
        7: "SSE",
        8: "S",
        9: "SSW",
        10: "SW",
        11: "WSW",
        12: "W",
        13: "WNW",
        14: "NW",
        15: "NNW"
    };

    return index === null || index === undefined
        ? null
        : (directions[index] || null);
}

function validOrValue(raw) {
    return raw === 0xFFFF ? null : raw;
}

function validOrScaled(raw, divisor) {
    return raw === 0xFFFF ? null : round(raw / divisor, 1);
}

function signedOrScaled(raw, divisor) {
    return raw === 0xFFFF ? null : round(s16(raw) / divisor, 1);
}

function u16(bytes, index) {
    return ((bytes[index] << 8) | bytes[index + 1]) >>> 0;
}

function s16(value) {
    return (value & 0x8000) ? value - 0x10000 : value;
}

function u32(bytes, index) {
    return (
        bytes[index] * 0x1000000 +
        bytes[index + 1] * 0x10000 +
        bytes[index + 2] * 0x100 +
        bytes[index + 3]
    ) >>> 0;
}

function round(value, decimals) {
    var multiplier = Math.pow(10, decimals);
    return Math.round(value * multiplier) / multiplier;
}

function toHex(value, width) {
    var text = value.toString(16).toUpperCase();

    while (text.length < width) {
        text = "0" + text;
    }

    return text;
}

function bytesToHex(bytes, start, len) {
    var text = "";
    var end = start + len;

    for (var i = start; i < end; i++) {
        text += toHex(bytes[i], 2);
    }

    return text;
}
