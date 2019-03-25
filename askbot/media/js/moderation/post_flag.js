var PostFlag = function () {
  WrappedElement.call(this)
  this.reasonId = undefined
  this.name = undefined
  this.postId = undefined
  this.count = 0
  this.flaggedByUser = false
  this.mode = undefined
}
inherits(PostFlag, WrappedElement)

PostFlag.prototype.setMode = function (mode) {
  this.mode = mode
  if (mode === 'edit') {
    this._count.hide()
    this._flagRemover.hide()
  } else if (mode === 'moderate') {
    if (this.count > 0) {
      this._count.show()
    }
    if (this.flaggedByUser) {
      this._flagRemover.show()
    }
  }
}

PostFlag.prototype.setReasonId = function (reasonId) {
  this.reasonId = reasonId
}

PostFlag.prototype.setPostId = function (postId) {
  this.postId = postId
}

PostFlag.prototype.setContent = function (name) {
  return this.setName(name)
}

PostFlag.prototype.setName = function (name) {
  this.name = name
  if (this._name) {
    this._name.text(name)
  }
}

PostFlag.prototype.getName = function () {
  return this.name
}

PostFlag.prototype.setFlagCount = function (count) {
  this.count = count
  if (this._count) {
    if (count) {
      this._count.removeClass('no-flags')
      this._count.text(count)
      if (this.mode === 'moderate') {
        this._count.show()
      } else {
        this._count.hide()
      }
    } else {
      this._count.addClass('no-flags')
    }
  }
}

PostFlag.prototype.setTotalFlagCount = function (count) {
  var postElement = document.getElementById('post-id-' + this.postId);
  if (postElement) {
    var postFlagCounter = $(postElement).find('.js-post-flag-count')
    if (postFlagCounter.length) {
      postFlagCounter.html('(' + count + ')')
      if (count > 0) {
        postFlagCounter.show()
      } else {
        postFlagCounter.hide()
      }
    }
  }
}

PostFlag.prototype.setFlaggedByUser = function (isFlagged) {
  this.flaggedByUser = isFlagged
  if (this._flagRemover) {
    if (isFlagged && this.mode === 'moderate') {
      this._flagRemover.show()
    } else {
      this._flagRemover.hide()
    }
  }
}

PostFlag.prototype.getFlagCountFromResponse = function (response) {
  var flagsInfo = response.post_flags
  for (var idx = 0; idx < flagsInfo.length; idx++) {
    var flagInfo = flagsInfo[idx]
    if (flagInfo.id === this.reasonId) {
      return flagInfo.flag_count
    }
  }
  return 0
}

PostFlag.prototype.getTotalFlagCountFromResponse = function (response) {
  var totalCount = 0
  var flagsInfo = response.post_flags
  for (var idx = 0; idx < flagsInfo.length; idx++) {
    var flagInfo = flagsInfo[idx]
    totalCount += flagInfo.flag_count
  }
  return totalCount
}

PostFlag.prototype.getFlagPostHandler = function () {
  var me = this
  /** ajax flag post with reason
   * receive flag count and update the flag counter
   */
  return function () {
    if (me.mode !== 'moderate') {
      return
    }
    var postData = {
      reason_id: me.reasonId,
      post_id: me.postId
    }
    $.ajax({
      type: 'POST',
      cache: false,
      dataType: 'json',
      data: JSON.stringify(postData),
      url: askbot.urls.flagPost,
      success: function (response) {
        if (response.success) {
          var flagCount = me.getFlagCountFromResponse(response)
          me.setFlagCount(flagCount)
          var totalFlagCount = me.getTotalFlagCountFromResponse(response)
          me.setTotalFlagCount(totalFlagCount)
          me.setFlaggedByUser(true)
        } else {
          alert(response.message)
        }
      }
    })
  }
}

PostFlag.prototype.getUnflagPostHandler = function () {
  var me = this
  return function () {
    if (me.mode !== 'moderate') {
      return false
    }
    var postData = {
      post_id: me.postId,
      reason_id: me.reasonId,
      cancel: true
    }
    $.ajax({
      type: 'POST',
      cache: false,
      dataType: 'json',
      data: JSON.stringify(postData),
      url: askbot.urls.flagPost,
      success: function (response) {
        if (response.success) {
          var flagCount = me.getFlagCountFromResponse(response)
          me.setFlagCount(flagCount)
          var totalFlagCount = me.getTotalFlagCountFromResponse(response)
          me.setTotalFlagCount(totalFlagCount)
          me.setFlaggedByUser(false)
        } else {
          alert(response.message)
        }
      }
    })
    return false;
  }
}

PostFlag.prototype.createDom = function () {
  this._element = this.makeElement('div')
  this._element.addClass('moderation-post-flag')
  this._name = this.makeElement('span')
  if (this.name) {
    this.setName(this.name)
  }
  this._element.append(this._name)

  var countAndRemover = this.makeElement('span')
  this._element.append(countAndRemover)

  this._count = this.makeElement('span')
  this._count.addClass('moderation-post-flag-count')
  this._count.click(function () { return false })
  if (this.count) {
    this.setFlagCount(this.count)
  } else {
    this.setFlagCount(0)
  }
  countAndRemover.append(this._count)

  this._flagRemover = this.makeElement('span')
  this._flagRemover.text(gettext('remove'))
  this._flagRemover.addClass('moderation-post-flag-remove')
  countAndRemover.append(this._flagRemover)

  this.setFlaggedByUser(this.flaggedByUser)
  setupButtonEventHandlers(this._flagRemover, this.getUnflagPostHandler())

  setupButtonEventHandlers(this._element, this.getFlagPostHandler())
}

var PostFlagWrapper = function () {
  SelectBoxItem.call(this)
  this._content_class = PostFlag
}
inherits(PostFlagWrapper, SelectBoxItem)

PostFlagWrapper.prototype.setMode = function (mode) {
  var content = this.getContent()
  content.setMode(mode)
}

PostFlagWrapper.prototype.setData = function (data) {
  var cls = getSuperClass(PostFlagWrapper)
  cls.setData.call(this, data)
  var content = this.getContent()
  content.setFlagCount(data.flag_count)
  content.setFlaggedByUser(data.flagged_by_user)
  content.setPostId(data.post_id)
  content.setReasonId(data.id)
}
