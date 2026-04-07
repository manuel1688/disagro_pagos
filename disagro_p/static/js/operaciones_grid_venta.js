import { multiplicar,sumar,dividir} from "/static/js/operaciones.js";

export let actualizar_totales = (tabla_grid_venta) => {
 
  let por_desc = 0.00;
  let total_neto_exe = 0.0;
  let total_neto_grabado = 0.0;
  let total_descuento = 0.00;

  for (var i = 0, row; row = tabla_grid_venta.rows[i]; i++) {

    // ANTES ARTICULO,DESCRIPCION,CANTIDAD,precio,monto_neto,porcentaje_descuento,monto_descuento,itbms,total
    // ARTICULO,DESCRIPCION,CANTIDAD 2,precio 3,porcentaje_descuento 4,PRECIO_NETO  5,monto_descuento 6,itbms,total

    por_desc = parseFloat(row.cells[4].innerHTML);
    let precio = parseFloat(row.cells[3].innerHTML); 
    let cantidad = parseFloat(row.cells[2].innerHTML);
    let sub_total = multiplicar(cantidad,parseFloat(row.cells[5].innerHTML));
    let total_descuento_linea = parseFloat(row.cells[6].innerHTML);
    
    if(por_desc > 0.00){
      total_descuento += total_descuento_linea;
      let total_linea_neto = sub_total;
      let itbms = parseFloat(row.cells[7].innerHTML);
      if(itbms > 0.00){
        total_neto_grabado += total_linea_neto;
      }else{
        total_neto_exe += total_linea_neto;
      }
    }else{
      let total_linea_neto = numero_tres_decimales(precio * cantidad);
      let itbms = parseFloat(row.cells[7].innerHTML);
      if(itbms > 0.00){
        total_neto_grabado += total_linea_neto;
      }else{
        total_neto_exe += total_linea_neto;
      }
    }
  }
  let total_itbms = numero_tres_decimales(total_neto_grabado * 0.07);
  let sub_total = total_neto_exe + total_neto_grabado;
  input_total_sub_total.value = numero_tres_decimales(sub_total);
  input_total_descuento.value = numero_tres_decimales(total_descuento);
  input_total_itbms.value = numero_tres_decimales(total_itbms);
  let total = sub_total + total_itbms;
  input_total.value = numero_tres_decimales(total);
}

export let articulo_para_venta = (articulo) => {
  let articulos_ls = JSON.parse(localStorage.getItem('articulos'));
  for (var i = 0; i < articulos_ls.length; i++){
    if (articulos_ls[i].CODIGO.toUpperCase() == articulo.toUpperCase()){ 
      return articulos_ls[i]
   }
  }
  return {}; 
}
