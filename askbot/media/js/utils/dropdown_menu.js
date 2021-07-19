(function() {
  $('.js-dropdown-menu').each(function(_, elem) {

    var target = $(elem).find('.js-dropdown-target');

    function toggleMenu (evt) {
      evt.stopPropagation();
      if (target.hasClass('js-dropdown-active')) {
        target.removeClass('js-dropdown-active');
      } else {
        target.addClass('js-dropdown-active');
      }
    }

    $(elem).click(function(evt) {
      evt.stopPropagation();
    });

    var trigger = $(elem).find('.js-dropdown-trigger');
    trigger.click(toggleMenu);
    $(window).click(function () { target.removeClass('js-dropdown-active') });
  })
})();
