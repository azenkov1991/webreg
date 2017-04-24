$(document).ready(function () {
    var errorContainer = $('#error-message');
    var commentContainer = $('#comment-message');
    var departmentSelect = $('#id_department');
    var specialitySelect = $('#id_speciality');
    var specialistSelect = $('#id_specialist');
    var specialityForm = $('#speciality-form');
    var specialistForm = $('#specialist-form');

    // Для хранения полученных специализаций
    var specializations = {};

    var setError = function (errorMessage) {
        errorContainer.html(errorMessage);
        errorContainer.slideDown();
    };

    var showComment = function (commentMessage) {
        commentContainer.html('<b>' + commentMessage + '</b>');
        commentContainer.slideDown();
    };

    var clearError = function (){
        errorContainer.slideUp();
    };
    var clearComment = function(){
        commentContainer.slideUp();
    };
    // Функция получения доступных специальностей для подразделения
    // Вставка в селект специализаций
    var getSpecializations = function (departmentId) {
       $.ajax('/api/pwriter/specializations_for_dep/' + departmentId, {
                success: function (specializationMas) {
                    var options = specialitySelect.children();
                    options.slice(1,options.length).remove();
                    if (!specializationMas.length || !(specializationMas instanceof Object)){
                        setError('Для этого подразделения нет доступных специальностей');
                    }
                    else{
                        for (var i=0; i<specializationMas.length; i++) {
                            var optionHtml = $('<option value=' + specializationMas[i].id +
                                             '>' + specializationMas[i].name +'</option>');
                            specializations[specializationMas[i].id] = specializationMas[i];
                            specialitySelect.append(optionHtml);
                        }
                        specialitySelect.val(-1);
                        specialityForm.slideDown();
                        specialistForm.hide();
                    }
                },
                error: function (request, errorType, errorMessage) {
                    setError('Ошибка: ' + errorType + ' ' + errorMessage);
                }
            }
        )
    };

    // Функция получения доступных специалистов
    // Вставка в селект специалистов
    var getSpecialists = function (departmentId, specializationId){
        $.ajax('/api/pwriter/avail_specialists/' + departmentId + "/" + specializationId, {
            success: function (specialistMas){
                var options = specialistSelect.children();
                options.slice(1,options.length).remove();
                if (!specialistMas.length || !(specialistMas instanceof Object)){
                    setError('Для этой специальности нет доступных специалистов');
                }
                else{
                    for (var i=0; i<specialistMas.length; i++){
                        var optionHtml = $('<option value=' + specialistMas[i].id +
                                '>' + specialistMas[i].fio + '</option>'
                        );
                        specialistSelect.append(optionHtml);
                    }
                    specialistSelect.val(-1);
                    specialistForm.slideDown();
                }
            },
            error: function(request, errorType, errorMessage){
                setError('Ошибка: ' + errorType + ' ' + errorMessage);
            }
        })
    };

    specialitySelect.on('change', function (event) {
        var specialityId = $(this).val();
        var departmentId = departmentSelect.val();
        getSpecialists(departmentId, specialityId);
        clearComment();
        if (specializations[specialityId].is_show_comment &&
            specializations[specialityId].comment
        ){
            showComment(specializations[specialityId].comment);
        }
    });

    departmentSelect.on('change', function (event) {
        var departmentId = $(this).val();
        getSpecializations(departmentId);
    });

    // При изменении формы убирается окно с ошибками
    $('#input_form_2').on('change',function () {
        clearError();
    });
    departmentSelect.val(-1);
});
