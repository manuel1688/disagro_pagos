export let cargar_fecha = (input_fecha) =>{
  let today = new Date();
  let dia = today.getDate();
  let mes = today.getMonth()+1;
  let ano = today.getFullYear();
  if(parseFloat(dia)<10){
    dia = `0${dia}`;
  }
  if(parseFloat(mes)<10){
    mes = `0${mes}`;
  }
  input_fecha.value = `${ano}-${mes}-${dia}`;
}
