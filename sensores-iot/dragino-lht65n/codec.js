function decodeUplink(input) {
    var bytes;
    var fPort;

    // Soporta tanto {bytes: [...], fPort: ...}
    // como una llamada directa desde Decode(bytes, port)
    if (input && typeof input === 'object' && input.bytes !== undefined) {
        bytes = input.bytes;
        fPort = input.fPort !== undefined ? input.fPort : 0;
    } else {
        bytes = input;
        fPort = 0;
    }

    function bytesToHex(byteArray) {
        var hex = '';
        for (var i = 0; i < byteArray.length; i++) {
            var b = byteArray[i];
            if (b < 0) b += 256;
            var h = b.toString(16);
            if (h.length === 1) h = '0' + h;
            hex += h;
        }
        return hex;
    }

    function strPad(byte) {
        var zero = '00';
        var hex = byte.toString(16);
        var tmp = 2 - hex.length;
        return zero.substr(0, tmp) + hex + ' ';
    }

    function getZf(num) {
        var n = parseInt(num, 10);
        return n < 10 ? '0' + n : '' + n;
    }

    function getMyDate(timestampStr) {
        var ts = parseInt(timestampStr, 10);
        var date = ts > 9999999999 ? new Date(ts) : new Date(ts * 1000);

        var year = date.getFullYear();
        var month = getZf(date.getMonth() + 1);
        var day = getZf(date.getDate());
        var hour = getZf(date.getHours());
        var minute = getZf(date.getMinutes());
        var second = getZf(date.getSeconds());

        return year + '-' + month + '-' + day + ' ' +
               hour + ':' + minute + ':' + second;
    }

    function dataLog(startIdx, buf) {
        var ext = buf[6] & 0x0F;
        var bb;

        if (ext === 1 || ext === 9) {
            bb = parseFloat(
                ((buf[startIdx] << 24 >> 16 | buf[startIdx + 1]) / 100).toFixed(2)
            );
        } else if (ext === 2 || ext === 10) {
            bb = parseFloat(
                ((buf[startIdx] << 24 >> 16 | buf[startIdx + 1]) / 100).toFixed(2)
            );
        } else if (ext === 4) {
            var extiPinLevel = buf[startIdx] ? "High" : "Low";
            var extiStatus = buf[startIdx + 1] ? "True" : "False";
            bb = extiPinLevel + extiStatus;
        } else if (ext === 5) {
            bb = buf[startIdx] << 8 | buf[startIdx + 1];
        } else if (ext === 6) {
            bb = (buf[startIdx] << 8 | buf[startIdx + 1]) / 1000;
        } else if (ext === 7) {
            bb = buf[startIdx] << 8 | buf[startIdx + 1];
        } else if (ext === 8 || ext === 14) {
            bb = buf[startIdx] << 8 | buf[startIdx + 1];
        } else if (ext === 11 || ext === 12) {
            bb = parseFloat(
                ((buf[startIdx] << 24 >> 16 | buf[startIdx + 1]) / 100).toFixed(2)
            );
        }

        var cc = parseFloat(
            ((buf[startIdx + 2] << 24 >> 16 | buf[startIdx + 3]) / 100).toFixed(2)
        );

        var dd = parseFloat(
            (((buf[startIdx + 4] << 8 | buf[startIdx + 5]) & 0xFFF) / 10).toFixed(1)
        );

        var timestamp =
            (buf[startIdx + 7] << 24 |
             buf[startIdx + 8] << 16 |
             buf[startIdx + 9] << 8 |
             buf[startIdx + 10]);

        var ee = getMyDate(timestamp.toString(10));

        return '[' + bb + ',' + cc + ',' + dd + ',' + ee + '],';
    }


    // =========================================================
    // FPORT 3
    // =========================================================

    if (fPort === 3 && bytes.length >= 3) {
        var byte2 = bytes[2];

        if (
            byte2 === 0x01 ||
            byte2 === 0x02 ||
            byte2 === 0x03 ||
            byte2 === 0x04
        ) {
            var batRaw = ((bytes[0] << 8) | bytes[1]) & 0x3FFF;
            var sensorType = bytes[2];
            var temps = [];

            for (var i = 3; i + 1 < bytes.length; i += 2) {
                var rawTemp = (bytes[i] << 8) | bytes[i + 1];

                if (rawTemp & 0x8000) {
                    rawTemp = rawTemp - 0x10000;
                }

                var tempC = parseFloat((rawTemp / 100).toFixed(2));
                temps.push(tempC);
            }

            var result = {
                Node_type: "LHT65N",
                bat: batRaw,
                Temp: temps
            };

            if (sensorType === 1) {
                result.sensor = "ds18b20";
            } else if (sensorType === 2) {
                result.sensor = "tmp117";
            } else if (sensorType === 3) {
                result.sensor = "gxht30";
            } else if (sensorType === 4) {
                result.sensor = "sht31";
            }

            return {
                data: result
            };
        }
    }


    // =========================================================
    // FPORT 5
    // =========================================================

    if (fPort === 5 && bytes.length >= 7) {
        var sensorModel = "";

        if (bytes[0] === 0x0B) {
            sensorModel = "LHT65N";
        } else if (bytes[0] === 0x1A) {
            sensorModel = "LHT65N-PIR";
        }

        var subBand = (bytes[4] === 0xFF) ? "NULL" : bytes[4];

        var freqBand = "";

        switch (bytes[3]) {
            case 0x01: freqBand = "EU868"; break;
            case 0x02: freqBand = "US915"; break;
            case 0x03: freqBand = "IN865"; break;
            case 0x04: freqBand = "AU915"; break;
            case 0x05: freqBand = "KZ865"; break;
            case 0x06: freqBand = "RU864"; break;
            case 0x07: freqBand = "AS923"; break;
            case 0x08: freqBand = "AS923_1"; break;
            case 0x09: freqBand = "AS923_2"; break;
            case 0x0A: freqBand = "AS923_3"; break;
            case 0x0B: freqBand = "CN470"; break;
            case 0x0C: freqBand = "EU433"; break;
            case 0x0D: freqBand = "KR920"; break;
            case 0x0E: freqBand = "MA869"; break;
            default: freqBand = "Unknown";
        }

        var firmVer =
            (bytes[1] & 0x0F) + '.' +
            ((bytes[2] >> 4) & 0x0F) + '.' +
            (bytes[2] & 0x0F);

        var batVoltage =
            ((bytes[5] << 8) | bytes[6]) / 1000;

        return {
            data: {
                SENSOR_MODEL: sensorModel,
                FIRMWARE_VERSION: firmVer,
                FREQUENCY_BAND: freqBand,
                SUB_BAND: subBand,
                BAT: batVoltage
            }
        };
    }


    // =========================================================
    // MENSAJES NORMALES LHT65N
    // =========================================================

    if (bytes.length < 7) {
        return {
            errors: ["Insufficient payload length"]
        };
    }

    var ext = bytes[6];
    var pollMsgStatus = (bytes[6] >> 6) & 0x03;
    var connectFlag = (bytes[6] & 0x80) >> 7;


    // =========================================================
    // POLL MESSAGE STATUS = 0
    // =========================================================

    switch (pollMsgStatus) {

        case 0:

            var decode = {
                Node_type: "LHT65N"
            };

            if (ext === 0x09) {

                decode.TempC_DS =
                    parseFloat(
                        ((bytes[0] << 24 >> 16 | bytes[1]) / 100).toFixed(2)
                    );

                decode.Bat_status = bytes[4] >> 6;

            } else if (ext === 0x0A) {

                decode.TempC_TMP117 =
                    parseFloat(
                        ((bytes[0] << 24 >> 16 | bytes[1]) / 100).toFixed(2)
                    );

                decode.Bat_status = bytes[4] >> 6;

            } else {

                var batVal =
                    ((bytes[0] << 8) | bytes[1]) & 0x3FFF;

                decode.BatV = batVal / 1000;

                var batStatusBits = bytes[0] >> 6;

                if (batStatusBits === 3) {
                    decode.Bat_status = "Good";
                } else if (batStatusBits === 2) {
                    decode.Bat_status = "OK";
                } else if (batStatusBits === 1) {
                    decode.Bat_status = "Low";
                } else {
                    decode.Bat_status = "Ultra Low";
                }
            }


            // SHT
            if (
                ext !== 0x0F &&
                ext !== 0x10 &&
                ext !== 0x20 &&
                ext !== 0x0E &&
                bytes.length >= 6
            ) {

                decode.TempC_SHT =
                    parseFloat(
                        ((bytes[2] << 24 >> 16 | bytes[3]) / 100).toFixed(2)
                    );

                decode.Hum_SHT =
                    parseFloat(
                        (((bytes[4] << 8 | bytes[5]) & 0xFFF) / 10).toFixed(1)
                    );
            }


            if (connectFlag === 1) {
                decode.No_connect = "Sensor no connection";
            }


            // External sensor
            if (ext === 0x00) {

                decode.Ext_sensor = "No external sensor";

            } else if (ext === 0x01) {

                decode.Ext_sensor = "Temperature Sensor";

                if (bytes.length >= 9) {
                    decode.TempC_DS =
                        parseFloat(
                            ((bytes[7] << 24 >> 16 | bytes[8]) / 100).toFixed(2)
                        );
                }

            } else if (ext === 0x02) {

                decode.Ext_sensor = "Temperature Sensor";

                if (bytes.length >= 9) {
                    decode.TempC_TMP117 =
                        parseFloat(
                            ((bytes[7] << 24 >> 16 | bytes[8]) / 100).toFixed(2)
                        );
                }

            } else if (ext === 0x04) {

                decode.Work_mode = "Interrupt Sensor send";

                if (bytes.length >= 9) {
                    decode.Exti_pin_level =
                        bytes[7] ? "High" : "Low";

                    decode.Exti_status =
                        bytes[8] ? "True" : "False";
                }

            } else if (ext === 0x05) {

                decode.Work_mode = "Illumination Sensor";

                if (bytes.length >= 9) {
                    decode.ILL_lx =
                        (bytes[7] << 8) | bytes[8];
                }

            } else if (ext === 0x06) {

                decode.Work_mode = "ADC Sensor";

                if (bytes.length >= 9) {
                    decode.ADC_V =
                        ((bytes[7] << 8) | bytes[8]) / 1000;
                }

            } else if (ext === 0x07) {

                decode.Work_mode = "Interrupt Sensor count";

                if (bytes.length >= 9) {
                    decode.Exit_count =
                        (bytes[7] << 8) | bytes[8];
                }

            } else if (ext === 0x08) {

                decode.Work_mode = "Interrupt Sensor count";

                if (bytes.length >= 11) {
                    decode.Exit_count =
                        bytes[7] << 24 |
                        bytes[8] << 16 |
                        bytes[9] << 8 |
                        bytes[10];
                }

            } else if (ext === 0x09) {

                decode.Work_mode = "DS18B20 & timestamp";

                if (bytes.length >= 11) {
                    decode.Systimestamp =
                        bytes[7] << 24 |
                        bytes[8] << 16 |
                        bytes[9] << 8 |
                        bytes[10];
                }

            } else if (ext === 0x0A) {

                decode.Work_mode = "TMP117 & timestamp";

                if (bytes.length >= 11) {
                    decode.Systimestamp =
                        bytes[7] << 24 |
                        bytes[8] << 16 |
                        bytes[9] << 8 |
                        bytes[10];
                }

            } else if (ext === 0x0B) {

                decode.Work_mode = "SHT31 Sensor";

                if (bytes.length >= 11) {

                    decode.Ext_TempC_SHT =
                        parseFloat(
                            ((bytes[7] << 24 >> 16 | bytes[8]) / 100).toFixed(2)
                        );

                    decode.Ext_Hum_SHT =
                        parseFloat(
                            (((bytes[9] << 8 | bytes[10]) & 0xFFF) / 10).toFixed(1)
                        );
                }

            } else if (ext === 0x10) {

                decode.Work_mode = "SHT31ID";

                if (bytes.length >= 11) {

                    decode.ID =
                        strPad(bytes[2]) +
                        strPad(bytes[3]) +
                        strPad(bytes[4]) +
                        strPad(bytes[5]);

                    decode.Ext_TempC_SHT =
                        parseFloat(
                            ((bytes[7] << 24 >> 16 | bytes[8]) / 100).toFixed(2)
                        );

                    decode.Ext_Hum_SHT =
                        parseFloat(
                            (((bytes[9] << 8 | bytes[10]) & 0xFFF) / 10).toFixed(1)
                        );
                }

            } else if (ext === 0x20) {

                decode.Work_mode = "NE117ID";

                if (bytes.length >= 11) {

                    decode.ID =
                        strPad(bytes[2]) +
                        strPad(bytes[3]) +
                        strPad(bytes[4]) +
                        strPad(bytes[5]) +
                        strPad(bytes[9]) +
                        strPad(bytes[10]);

                    decode.TempC_TMP117 =
                        parseFloat(
                            ((bytes[7] << 24 >> 16 | bytes[8]) / 100).toFixed(2)
                        );
                }

            } else if (ext === 0x15) {

                decode.Work_mode = "DS18B20ID";

                if (bytes.length >= 11) {

                    decode.ID =
                        strPad(bytes[2]) +
                        strPad(bytes[3]) +
                        strPad(bytes[4]) +
                        strPad(bytes[5]) +
                        strPad(bytes[7]) +
                        strPad(bytes[8]) +
                        strPad(bytes[9]) +
                        strPad(bytes[10]);
                }
            }


            if (bytes.length === 11 || bytes.length === 15) {
                return {
                    data: decode
                };
            }

            break;


        // =====================================================
        // POLL MESSAGE STATUS = 1
        // =====================================================

        case 1:

            var logData = "";

            for (var k = 0; k + 10 < bytes.length; k += 11) {
                logData += dataLog(k, bytes);
            }

            return {
                data: {
                    Node_type: "LHT65N",
                    DATALOG: logData
                }
            };


        // =====================================================
        // POLL MESSAGE STATUS = 2
        // =====================================================

        case 2:

            var retransLog = "";

            for (var j = 0; j + 10 < bytes.length; j += 11) {
                retransLog += dataLog(j, bytes);
            }

            return {
                data: {
                    Node_type: "LHT65N",
                    DATALOG: retransLog,
                    retransmission_Status: "retransmission_Status"
                }
            };


        default:

            return {
                errors: ["Unknown poll_message_status"]
            };
    }

    return {
        errors: ["Decoding failed"]
    };
}


// =============================================================
// COMPATIBILIDAD CON SERVIDORES QUE LLAMAN Decode()
// =============================================================

function Decode(fPort, bytes, variables) {
    var output = decodeUplink({
        bytes: bytes,
        fPort: fPort,
        variables: variables || {}
    });

    // ChirpStack v3 espera directamente el objeto con las mediciones.
    if (output && output.data !== undefined) {
        return output.data;
    }

    // Evita que un payload no reconocido detenga todo el codec.
    if (output && output.errors && output.errors.length > 0) {
        return {
            codec_error: output.errors.join('; ')
        };
    }

    return output || {};
}
