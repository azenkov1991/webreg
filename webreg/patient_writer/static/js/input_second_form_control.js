$(document).ready(function () {
    $('#id_department').val(0)
    $('#department-form').on('change','.select',function (event) {
        var departmentId = $(this).val();
        // TODO: получить c сервера список доступных специалитов для подразделения
        $('#speciality-form').slideDown();

    })
    }
);
