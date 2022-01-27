/* global askbot, setupButtonEventHandlers, showMessage */
$(document).ready(function () {
  //todo: convert to "control" class
  var publishBtns = $('.js-answer-publish, .js-answer-unpublish');
  publishBtns.each(function (idx, btn) {
    setupButtonEventHandlers($(btn), function () {
      var answerId = $(btn).data('postId');
      $.ajax({
        type: 'POST',
        dataType: 'json',
        data: {'answer_id': answerId},
        url: askbot.urls.publishAnswer,
        success: function (data) {
          if (data.success) {
            window.location.reload(true);
          } else {
            showMessage($(btn), data.message, $(btn));
          }
        }
      });
    });
  });
});
