(function($) {
    $(function() {
        var jcarousel = $('.jcarousel');
        var controlPrev = $('.jcarousel-control-prev');
        var controlNext = $('.jcarousel-control-next');
        jcarousel
            .on('jcarousel:reload jcarousel:create', function (event) {
                var carousel = $(this);
                var width = carousel.innerWidth();
                // подгонка ширины карусели под количесвто столбцов
                var cellWidth = carousel.find('li').innerWidth();
                var numberOfColumns = carousel.find('ul li').length;
                var numberColumnsFits = Math.floor(carousel.parent().innerWidth() / (cellWidth));
                var numberOfVisibleColumns = numberColumnsFits;

                if (numberOfColumns <= numberColumnsFits){
                    numberOfVisibleColumns = numberOfColumns;
                    controlPrev.hide();
                    controlNext.hide();
                }
                else{
                    controlPrev.show();
                    controlNext.show();
                }
                var calcWidth = Math.floor(numberOfVisibleColumns * (cellWidth));
                jcarousel.css('width',  calcWidth + 'px');
            })
            .jcarousel();
        controlPrev.jcarouselControl({
                target: '-=1'
        });
        controlNext.jcarouselControl({
                target: '+=1'
        });

        $('.jcarousel-wrapper').swipe( {
            swipeRight:function(event) {
                jcarousel.jcarousel('scroll', '-=1')
            },
            swipeLeft:function(event) {
                jcarousel.jcarousel('scroll', '+=1')
            }
        });

    });
})(jQuery);
