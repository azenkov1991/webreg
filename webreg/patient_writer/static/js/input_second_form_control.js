$(document).ready(function () {
    var errorContainer = $('#error-message');
    var departmentSelect = $('#id_department');
    var specialitySelect = $('#id_speciality');

    var setError = function (errorMessage) {
        errorContainer.html(errorMessage);
        errorContainer.slideDown();
    };
    var clearError = function (){
        errorContainer.slideUp();
    };
    // Функция получения доступных специальностей для подразделения
    // Вставка в селект специализаций
    var getSpecializations = function (departmentId) {
       $.ajax('/api/pwriter/specializations_for_dep/' + departmentId, {
                success: function (specializationMas) {
                    var options = specialitySelect.children() ;
                    options.slice(1,options.length).remove();
                    if (!specializationMas.length){
                        setError('Для этого подразделения нет доступных специальностей');
                    }
                    else{
                        for (var i=0; i<specializationMas.length; i++) {
                            var optionHtml = $('<option value=' + specializationMas[i].id +
                                             '>' + specializationMas[i].name +'</option>');
                            specialitySelect.append(optionHtml);
                        }
                        specialitySelect.val(-1)
                    }

                },
                error: function (request, errorType, errorMessage) {
                    setError('Ошибка: ' + errorType + ' ' + errorMessage);
                }
            }
        )
    };

    //При изменении формы убирается окно с ошибками
    $('#input_form_2').on('change',function () {
        clearError();
    });

    departmentSelect.val(-1);

    $('#department-form').on('change','.select',function (event) {
        var departmentId = $(this).val();
        getSpecializations(departmentId);
        $('#speciality-form').slideDown();
    })
    }
);
