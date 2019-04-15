$(function() {
    $('.dateinput').mask('99.99.9999');
    $('.mobile-phone-input').mask('+7 (999) 999-99-99');

    // Автофокус на следующее поле
    $('.phone-input-part').on('input', function () {
        if (this.value.length == this.maxLength) {
            $(this).next('input.phone-input-part').focus();
        };
       });
});
