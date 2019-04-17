$(document).ready(function () {
    $("form").submit(function (e) {
        var button = $(this).find("button[type='submit']");
        button.attr("disabled", true);
        button.html('Ожидание...')
    });
});

