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
    this.flagCounters = {} // refs to the spans containing the flag counts
    this.dialog = undefined
  }

  PostFlagger.prototype.setDialog = function (dialog) {
    this.dialog = dialog
  }

  PostFlagger.prototype.setPostId = function (postId) {
    this.postId = postId
  }

  PostFlagger.prototype.registerFlagCounter = function (postId, element) {
    this.flagCounters[postId] = element
  }

  PostFlagger.prototype.updateFlagCounter = function (postId, count) {
    this.flagCounters[postId].html(count)
  }

  PostFlagger.prototype.loadPostFlags = function (postId) {
    var dialog = this.dialog
    $.ajax({
      type: 'GET',
      cache: false,
      dataType: 'json',
      data: { post_id: postId },
      url: askbot.urls.getPostFlags,
      success: function (response) {
        if (response.success) {
          dialog.setItemsData(response.post_flags)
        }
      }
    })
  }

  PostFlagger.prototype.getOpenMenuHandler = function (postId) {
    var me = this
    return function () {
      flagger.setPostId(postId)
      me.dialog.show()
      me.loadPostFlags(postId)
    }
  }

  PostFlagger.prototype.getOnReasonSaveHandler = function () {
    var me = this
    return function () {
      var postId = me.postId
      me.loadPostFlags(postId)
    }
  }

  var dialog = new ManageModerationReasonsDialog('post_moderation')
  dialog.setSelectBoxItemClass(PostFlagWrapper)
  dialog.setBimodal(true)
  dialog.decorate($('#manage-post_moderation-reasons-modal'))
  dialog.setTitleText(
    'edit',
    gettext('Manage flags')
  )
  dialog.setTitleText(
    'moderate',
    gettext('Flag/unflag the post')
  )
  dialog.setInfoMessage(
    'edit',
    gettext('Note: reasons with an asterisk* in are system-defined and cannot be edited here. Select a reason to edit or delete.')
  );
  dialog.setInfoMessage(
    'moderate',
    gettext('Flag the posts by selecting one of the reasons below. Reasons with an asterisk* are system-defined.')
  )
  dialog.setMode('moderate')

  var flagger = new PostFlagger()
  flagger.setDialog(dialog)
  dialog.setOnReasonSaveHandler(flagger.getOnReasonSaveHandler())

  var flagBtns = $('.post .js-post-flags')
  for (var idx = 0; idx < flagBtns.length; idx++) {
    var btn = $(flagBtns[idx])
    var postId = btn.data('postId')
    flagger.registerFlagCounter(postId, btn.find('.js-post-flag-count'))
    var handler = flagger.getOpenMenuHandler(postId)
    setupButtonEventHandlers(btn, handler)
  }

})()
