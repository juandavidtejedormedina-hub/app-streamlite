// Vectores sintéticos: comprueban conversiones y rechazos, sin dispositivos reales.
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');

function codec(folder) {
  const context = {};
  vm.createContext(context);
  vm.runInContext(fs.readFileSync(path.join(__dirname, folder, 'codec.js'), 'utf8'), context);
  return context;
}
const s = codec('sensecap-s2100');
function payload(nivel, temperatura) {
  const b = Buffer.alloc(11);
  b[0] = 0x31; b[1] = 0x12;
  b.writeInt32BE(nivel, 3); b.writeInt32BE(temperatura, 7);
  return Array.from(b);
}
const decode = (bytes, fPort = 3) => s.decodeUplink({bytes, fPort}).data.lectura_reservorio;
const valid = payload(1234000, 25000);
const result = decode(valid);
assert.equal(result.funcionando_correctamente, true);
assert.equal(result.medidas.medida_m, 1.234);
assert.equal(result.medidas.medida_cm, 123.4);
assert.equal(result.medidas.medida_mm, 1234);
assert.equal(result.medidas.temperatura_c, 25);
assert.equal(decode(payload(1234000, -5500)).medidas.temperatura_c, -5.5);
assert.equal(decode(valid, 2).error.codigo, 'ERROR_FPORT');
assert.equal(decode([]).error.codigo, 'ERROR_PAYLOAD_VACIO');
assert.equal(decode([0x12]).error.codigo, 'ERROR_TRAMA_12');
assert.equal(decode([0x31, 0x12]).error.codigo, 'ERROR_LONGITUD');
assert.equal(decode(payload(-2147483648, 25000)).error.codigo, 'ERROR_MEDICION_NO_DISPONIBLE');
const badChannels = valid.slice(); badChannels[1] = 0x13;
assert.equal(decode(badChannels).error.codigo, 'ERROR_CANALES');
const lht = codec('dragino-lht65n');
assert.equal(lht.decodeUplink({fPort: 2, bytes: []}).errors[0], 'Insufficient payload length');
assert.equal(typeof lht.Decode, 'function');
assert.match(lht.Decode(2, [], {}).codec_error, /Insufficient/);
const wsc = codec('dragino-wsc2-l');
assert.equal(wsc.decodeUplink({fPort: 2, bytes: []}).data.error, 'Payload vacio');
assert.match(wsc.decodeUplink({fPort: 5, bytes: [0x2e]}).data.error, /corto/);
assert.match(wsc.decodeUplink({fPort: 99, bytes: [1]}).data.error, /no soportado/);
const status = wsc.decodeUplink({fPort: 5, bytes: [0x2e, 1, 0x23, 2, 1, 0x0b, 0xb8]}).data;
assert.equal(status.SENSOR_MODEL, 'WSC2-L');
assert.equal(status.FIRMWARE_VERSION, '1.2.3');
assert.equal(status.FREQUENCY_BAND, 'US915');
assert.equal(status.BAT, 3);
console.log('22 comprobaciones correctas: S2100, LHT65N y WSC2-L.');
