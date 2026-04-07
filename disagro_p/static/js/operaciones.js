let multiplicar = (a,b) => numero_tres_decimales(parseFloat(a)*parseFloat(b));
let sumar = (a,b) => numero_tres_decimales(parseFloat(a)+parseFloat(b));
let dividir = (a,b) => numero_tres_decimales(parseFloat(a)/parseFloat(b));
let restar = (a,b) => numero_tres_decimales(parseFloat(a)-parseFloat(b));

export { multiplicar,sumar,dividir,restar};