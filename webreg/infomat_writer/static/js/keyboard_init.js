$( function() {
    $('#id_polis_number').keyboard({
        usePreview: false,
        autoAccept: true,
        maxLength: 16,
        layout: 'custom',
        customLayout: {
            'normal' : [
                '1 2 3 4 5 6 7 8 9 0 {bksp}',
            ],
        },
        display: {
            'bksp': 'Удалить',
        },
        css: {
            input: '',
            container: '',
            buttonDefault: '',
            buttonHover: '',
            buttonAction: '',
            buttonDisabled: ''
        },
    });

    $('.phone-input-part').keyboard({
        usePreview: false,
        autoAccept: true,
        layout: 'custom',
        keyBinding: 'mousedown touchstart keydown',
        customLayout: {
            'normal' : ['1 2 3 4 5 6 7 8 9 0 {bksp}',
            ],

        },
        display: {
            'bksp': 'Удалить',
        },
        position: {
           of: $('#id_phone_0'), // null = attach to input/textarea; use $(sel) to attach elsewhere
            my: 'left top',
            at: 'left-50 bottom',
            at2: 'left-75 bottom' // used when "usePreview" is false
        },
        css: {
            input: '',
            container: '',
            buttonDefault: '',
            buttonHover: '',
            buttonAction: '',
            buttonDisabled: ''
        },
    });


   $('.phone-input-part').on('keyboardChange', function (e) {
        if (this.value.length >= this.maxLength){
            $(this).next('.phone-input-part').focus();
            $(this).val(this.value.slice(0,this.maxLength));

        }
        if (e.action == 'bksp' && this.value.length == 0) {
            $(this).prev('.phone-input-part').focus();
        }
       console.log('kbChange');
       console.log(e);
       }
   );

   $('#id_polis_seria').keyboard({
        usePreview: false,
        autoAccept: true,
        maxLength: 16,
        layout: 'custom',
        customLayout: {
            'normal': [
                'Й Ц У К Е Н Г Ш Щ З Х Ъ {bksp}',
                'Ф Ы В А П Р О Л Д Ж Э',
                'Я Ч С М И Т Ь Б Ю {accept}',

            ],

        },
        display: {
            'bksp': 'Удалить',
            'accept': 'Ввод',
        },
        css: {
            input: '',
            container: '',
            buttonDefault: '',
            buttonHover: '',
            buttonAction: '',
            buttonDisabled: ''
        },
    });

});
