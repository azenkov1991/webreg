$(document).ready(function () {
    console.log('WORK');
    // Блокирование серии полиса если номер 16 цифр
    $('#id_polis_number').on('input',
      function () {
          var val = $(this).val();
          console.log($(this).val());
          if (( 5 < val.length ) && ( val.length < 8 )){
              $('#id_polis_seria').removeAttr('disabled');
          }
          else{
              $('#id_polis_seria').attr('disabled', 'disabled');
          }
      }
    );
});
