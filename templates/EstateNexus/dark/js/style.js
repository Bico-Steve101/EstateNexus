$(document).ready(function () {
    $('.toggle-col').click(function () {
        $(this).closest('.row').find('.col').toggle();
    });
    
    $('.fe-upload').click(function () {
        var $cardBody = $(this).closest('.card-body').find('.swipe');
        $cardBody.slideToggle();
        $(this).toggleClass('rotate-180');

      // Toggle arrow direction
      if ($(this).hasClass('rotate-180')) {
          $(this).removeClass('fe-corner-down-left').addClass('fe-corner-down-right');
      } else {
          $(this).removeClass('fe-corner-down-right').addClass('fe-corner-down-left');
      }
  });
});