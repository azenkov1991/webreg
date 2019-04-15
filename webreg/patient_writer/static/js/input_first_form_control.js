$(document).ready(function () {
    var disabeSeriaFunction = function () {
          var val = $(this).val();
          console.log($(this).val());
          if (( 5 < val.length ) && ( val.length < 8 )){
              $('#id_polis_seria').removeAttr('disabled');
          }
          else{
              $('#id_polis_seria').attr('disabled', 'disabled');
          }
      };

    // Блокирование серии полиса если номер не соответствует длине
    $('#id_polis_number').on('input', disabeSeriaFunction);
    $('#id_polis_number').change(disabeSeriaFunction);
    $('#id_polis_number').on('keyboardChange',disabeSeriaFunction);

});
