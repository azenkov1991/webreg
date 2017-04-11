$(document).ready(function () {
    console.log($('#id_department').val())
    if ($('#id_department').val()!=null) {
        $('#speciality-form').slideDown();
    }
    $('#department-form').on('change','.select',function (event) {
        var departmentId = $(this).val();
        // TODO: получить c сервера список доступных специализаций для подразделения
        $('#speciality-form').slideDown();

    })
    }
);
