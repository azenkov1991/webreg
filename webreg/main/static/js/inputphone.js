$(function() {
    // Автофокус на следующее поле для ввода телефона
    $('.phone-input-part').keydown(function(e) {

        var keys = [8, 9, /*16, 17, 18,*/ 19, 20, 27, 33, 34, 35, 36, 37, 38, 39, 40, 45, 46, 144, 145];

        if (e.which == 8 && this.value.length == 0) {
            $(this).prev('.phone-input-part').focus();
        } else if ($.inArray(e.which, keys) >= 0) {
            return true;
        } else if (this.value.length >= this.maxLength) {
            $(this).next('.phone-input-part').focus();
            return false;
        } else if (e.shiftKey || e.which <= 47 || e.which >= 58) {
            return false;
        }
    }).keyup (function () {
        if (this.value.length >= this.maxLength) {
            $(this).next('.phone-input-part').focus();
            return false;
        }
    });
});

