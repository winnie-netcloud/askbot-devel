/**
 * decorates elements with .js-post-flags class
 * which are normally
 * <span class='js-post-flags' data-post-id='some-id'>report ...</span>
 * On click opens a menu:
 *
 * some flag/(count)
 * other flag/(count)
 * manage flags <- admin only function
 */
(function () {
  var PostFlagger = function () {
    this.postId = undefined
    this.flagCounters = {}; //refs to the spans containing the flag counts
  };

  PostFlagger.prototype.setPostId = function(postId) {
    this.postId = postId;
  };

  PostFlagger.prototype.registerFlagCounter = function(postId, element) {
    this.flagCounters[postId] = element;
  }

  PostFlagger.prototype.updateFlagCounter = function(postId, count) {
    this.flagCounters[postId].html(count);
  }

  PostFlagger.prototype.getOpenMenuHandler = function (postId) {
    return function () {
      btn.data('postId');
      flagger.setPostId(postId);
      dialog.show();
    };
  };

  PostFlagger.prototype.getModerationHandler = function () {
    var me = this;
    /** ajax flag post with reason
     * receive flag count and update the flag counter
     * and close the moderation menu.
     */
    return function (reasonId) {
      var postData = {
        reason_id: reasonId,
        post_id: me.postId
      }
      $.ajax({
        type: 'POST',
        cache: false,
        dataType: 'json',
        data: JSON.stringify(postData),
        url: askbot.urls.flagPost,
        success: function (responseData) {
          if (responseData.success) {
            debugger
            me.updateFlagCounter(postId, responseData.flag_count);
          }
        }
      });
    }
  };

  var dialog = new ManageModerationReasonsDialog('post_moderation');
  dialog.setMode('moderate');
  dialog.setBimodal(true);
  dialog.decorate($('#manage-post_moderation-reasons-modal'));

  var flagger = new PostFlagger();
  dialog.setModerationHandler(flagger.getModerationHandler());

  var flagBtns = $('.post .js-post-flags')
  for (var idx = 0; idx < flagBtns.length; idx++) {
    var btn = $(flagBtns[idx]);
    var postId = btn.data('postId');
    flagger.registerFlagCounter(postId, btn.find('.js-post-flag-count'));
    var handler = flagger.getOpenMenuHandler(postId);
    setupButtonEventHandlers(btn, handler);
  }
})();
