/**
 * @constructor
 * manages post/edit moderation reasons
 * in the post moderation view
 */
var ManageModerationReasonsDialog = function (reasonType) {
  WrappedElement.call(this)
  this.reasonType = reasonType
  this._selected_edit_ids = null
  this._selected_reason_id = null
  this._state = 'select'// 'select', 'add-new'
  this._mode = 'edit' // moderate | edit
  this._isBimodal = false
  this._postModerationControls = []
  this._selectedEditDataReader = undefined
  this._onReasonSaveHandler = null
  this._infoMessages = {}
  this._titleTexts = {}
  this._selectBoxItemClass = null
  this._select_box = null
}
inherits(ManageModerationReasonsDialog, WrappedElement)

ManageModerationReasonsDialog.prototype.setOnReasonSaveHandler = function (func) {
  this._onReasonSaveHandler = func
}

ManageModerationReasonsDialog.prototype.getOnReasonSaveHandler = function () {
  return this._onReasonSaveHandler
}

ManageModerationReasonsDialog.prototype.setSelectBoxItemClass = function (cls) {
  this._selectBoxItemClass = cls
}

ManageModerationReasonsDialog.prototype.setItemsData = function (data) {
  this._select_box.setItemsData(data)
}

ManageModerationReasonsDialog.prototype.getSelectBox = function () {
  return this._select_box
}

ManageModerationReasonsDialog.prototype.setBimodal = function (value) {
  this._isBimodal = value
}

ManageModerationReasonsDialog.prototype.getMode = function () {
  return this._mode
}

ManageModerationReasonsDialog.prototype.setMode = function (mode) {
  this._mode = mode
  if (this._element) {
    if (mode === 'edit') {
      this._moderateButtons.hide()
      this._editButtons.show()
    } else if (mode === 'moderate') {
      this._moderateButtons.show()
      this._editButtons.hide()
    } else {
      throw 'Unsupported mode: "' + mode + '"'
    }
    this._menuTitleElement.html(this._titleTexts[mode])
    this._infoMessage.html(this._infoMessages[mode])
    if (this._select_box) {
      this._select_box.setMode(mode)
    }
  }
}

ManageModerationReasonsDialog.prototype.setInfoMessage = function (mode, message) {
  this._infoMessages[mode] = message
}

ManageModerationReasonsDialog.prototype.setTitleText = function (mode, title) {
  this._titleTexts[mode] = title
}

ManageModerationReasonsDialog.prototype.setMenu = function (menu) {
  this._reasonsMenu = menu
}

ManageModerationReasonsDialog.prototype.getMenu = function () {
  return this._reasonsMenu
}

ManageModerationReasonsDialog.prototype.setSelectedEditDataReader = function (func) {
  this._selectedEditDataReader = func
}

ManageModerationReasonsDialog.prototype.readSelectedEditData = function () {
  var data = this._selectedEditDataReader()
  this.setSelectedEditData(data)
  return data.id_list.length > 0
}

ManageModerationReasonsDialog.prototype.setSelectedEditData = function (data) {
  this._selected_edit_data = data
}

ManageModerationReasonsDialog.prototype.addPostModerationControl = function (control) {
  this._postModerationControls.push(control)
}

ManageModerationReasonsDialog.prototype.setState = function (state) {
  this._state = state
  this.clearErrors()
  if (this._element) {
    this._selector.hide()
    this._adder.hide()
    if (state === 'select') {
      this._selector.show()
    } else if (state === 'add-new') {
      this._adder.show()
    }
  }
}

ManageModerationReasonsDialog.prototype.show = function () {
  $(this._element).modal('show')
}

ManageModerationReasonsDialog.prototype.hide = function () {
  $(this._element).modal('hide')
}

ManageModerationReasonsDialog.prototype.resetInputs = function () {
  if (this._title_input) {
    this._title_input.reset()
  }
  if (this._details_input) {
    this._details_input.reset()
  }
  var selected = this._element.find('.selected')
  selected.removeClass('selected')
}

ManageModerationReasonsDialog.prototype.clearErrors = function () {
  var error = this._element.find('.alert')
  error.remove()
}

ManageModerationReasonsDialog.prototype.makeAlertBox = function (errors) {
  // construct the alert box
  var alert_box = new AlertBox()
  alert_box.setClass('alert-error')
  if (typeof errors === 'string') {
    alert_box.setText(errors)
  } else if (errors.constructor === [].constructor) {
    if (errors.length > 1) {
      alert_box.setContent(
        '<div>' +
        gettext('Looks there are some things to fix:') +
        '</div>'
      )
      var list = this.makeElement('ul')
      $.each(errors, function (idx, item) {
        list.append('<li>' + item + '</li>')
      })
      alert_box.addContent(list)
    } else if (errors.length === 1) {
      alert_box.setContent(errors[0])
    } else if (errors.length === 0) {
      return
    }
  } else if ('html' in errors) {
    alert_box.setContent(errors)
  } else {
    return// don't know what to do
  }
  return alert_box
}

ManageModerationReasonsDialog.prototype.setAdderErrors = function (errors) {
  // clear previous errors
  this.clearErrors()
  var alert_box = this.makeAlertBox(errors)
  this._element
    .find('.add-reason-dialog .modal-body')
    .prepend(alert_box.getElement())
}

ManageModerationReasonsDialog.prototype.setSelectorErrors = function (errors) {
  this.clearErrors()
  var alert_box = this.makeAlertBox(errors)
  this._element
    .find('.select-reason-dialog .modal-body')
    .prepend(alert_box.getElement())
}

ManageModerationReasonsDialog.prototype.getModerationReason = function (reasonId) {
  for (var idx = 0; idx < askbot.data.moderationReasons.length; idx++) {
    var reason = askbot.data.moderationReasons[idx]
    if (reason.id === reasonId) {
      return reason
    }
  }
  return null
}

ManageModerationReasonsDialog.prototype.addSelectableReason = function (data) {
  var id = data.reason_id
  var title = data.title
  var details = data.description
  this._select_box.addItem(id, title, details)

  askbot.data.moderationReasons.push({ id: data.reason_id, title: data.title })
  $.each(this._postModerationControls, function (idx, control) {
    control.addReason(data.reason_id, data.title)
  })
}

ManageModerationReasonsDialog.prototype.startSavingReason = function () {
  var title_input = this._title_input
  var details_input = this._details_input

  var errors = []
  if (title_input.isBlank()) {
    errors.push(gettext('Please provide description.'))
  }
  if (details_input.isBlank()) {
    errors.push(gettext('Please provide details.'))
  }

  if (errors.length > 0) {
    this.setAdderErrors(errors)
    return// just show errors and quit
  }

  var data = {
    title: title_input.getVal(),
    description: details_input.getVal(),
    reason_type: this.reasonType
  }

  var reasonIsNew = true
  if (this._selected_reason_id) {
    data.reason_id = this._selected_reason_id
    reasonIsNew = false
  }

  var me = this

  $.ajax({
    type: 'POST',
    dataType: 'json',
    cache: false,
    url: askbot.urls.saveModerationReason,
    data: data,
    success: function (data) {
      if (data.success) {
        // show current reason data and focus on it
        me.addSelectableReason(data)
        if (reasonIsNew) {
          var menu = me.getMenu()
          if (menu) {
            menu.addReason(data.reason_id, data.title)
          }
        }
        var onSaveHandler = me.getOnReasonSaveHandler()
        if (onSaveHandler) {
          onSaveHandler(data)
        }
        me.setState('select')
      } else {
        me.setAdderErrors(data.message)
      }
    }
  })
}

ManageModerationReasonsDialog.prototype.getReasonData = function (id) {
  var reasons = askbot['data']['moderationReasons']
  for (var idx = 0; idx < reasons.length; idx++) {
    var reason = reasons[idx]
    if (reason.id === id) {
      return reason
    }
  }
  return null
}

ManageModerationReasonsDialog.prototype.isReasonPredefined = function (id) {
  var data = this.getReasonData(id)
  if (data) {
    return data.is_predefined
  }
  throw 'Moderation reason with id ' + id + ' not found'
}

ManageModerationReasonsDialog.prototype.startEditingReason = function () {
  var data = this._select_box.getSelectedItemData()
  if (this.isReasonPredefined(data.id)) {
    this.setSelectorErrors(gettext('This reason is predefined and cannot be modified'))
    return
  } else {
    this.clearErrors()
  }
  var title = $(data.title).text() || data.title // bug in the underlying element!!!
  var description = data.details
  this._title_input.setVal(title)
  this._details_input.setVal(description)
  this._selected_reason_id = data.id
  this.setState('add-new')
}

ManageModerationReasonsDialog.prototype.resetSelectedReasonId = function () {
  this._selected_reason_id = null
}

ManageModerationReasonsDialog.prototype.getSelectedReasonId = function () {
  return this._selected_reason_id
}

ManageModerationReasonsDialog.prototype.startDeletingReason = function () {
  var select_box = this._select_box
  var data = select_box.getSelectedItemData()
  if (this.isReasonPredefined(data.id)) {
    this.setSelectorErrors(gettext('This reason is predefined and cannot be deleted'))
    return
  } else {
    this.clearErrors()
  }
  var reason_id = data.id
  var me = this
  if (data.id) {
    $.ajax({
      type: 'POST',
      dataType: 'json',
      cache: false,
      url: askbot.urls.deleteModerationReason,
      data: { reason_id: reason_id },
      success: function (data) {
        if (data.success) {
          select_box.removeItem(reason_id)
          me.hideEditButtons()
          var menu = me.getMenu()
          if (menu) {
            menu.removeReason(reason_id)
          }
        } else {
          me.setSelectorErrors(data.message)
        }
      }
    })
  } else {
    me.setSelectorErrors(gettext('A reason must be selected to delete one.'))
  }
}

ManageModerationReasonsDialog.prototype.hideEditButtons = function () {
  this._editButton.hide()
  this._deleteButton.hide()
}

ManageModerationReasonsDialog.prototype.showEditButtons = function () {
  this._editButton.show()
  this._deleteButton.show()
}

ManageModerationReasonsDialog.prototype.getSelectItemHandler = function () {
  var me = this
  return function () {
    var mode = me.getMode()
    if (mode === 'edit') {
      me.showEditButtons()
    } else if (mode === 'moderate') {
      var data = me.getSelectBox().getSelectedItemData()
      var reasonId = data.id
    } else {
      throw 'Unexpected mode ' + mode
    }
  }
}

ManageModerationReasonsDialog.prototype.decorate = function (element) {
  var me = this
  this._element = element
  // set default state according to the # of available reasons
  this._selector = $(element).find('.select-reason-dialog')
  this._adder = $(element).find('.add-reason-dialog')
  if (this._selector.find('li').length > 0) {
    this.setState('select')
    this.resetInputs()
  } else {
    this.setState('add-new')
    this.resetInputs()
  }

  this._menuTitleElement = $(element).find('.js-modal-title')

  this._infoMessage = $(element).find('.info-message')

  this._editButtons = $(element).find('.edit-buttons')
  this._moderateButtons = $(element).find('.moderate-buttons')
  var toEditModeBtn = $(element).find('.to-edit-mode')
  setupButtonEventHandlers(toEditModeBtn, function () { me.setMode('edit') })
  this.setMode(this._mode)

  var toApplyModeBtn = $(element).find('.to-apply-mode')
  setupButtonEventHandlers(toApplyModeBtn, function () { me.setMode('moderate') })

  if (this._isBimodal === false) {
    $(element).find('.to-apply-mode').hide()
  } else {
    this._editButtons.find('.cancel').hide()
  }

  var select_box = new SelectBox()
  if (this._selectBoxItemClass) {
    select_box.setItemClass(this._selectBoxItemClass)
  }
  select_box.decorate($(this._selector.find('.select-box')))
  select_box.setSelectHandler(this.getSelectItemHandler())
  this._select_box = select_box

  // setup tipped-inputs
  var moderation_title_input = $(this._element).find('input')
  var title_input = new TippedInput()
  title_input.decorate($(moderation_title_input))
  this._title_input = title_input

  var moderation_details_input = $(this._element).find('textarea.moderation-reason-details')

  var details_input = new TippedInput()
  details_input.decorate($(moderation_details_input))
  this._details_input = details_input

  var resetMenuHandler = function () {
    me.clearErrors()
    me.resetInputs()
    me.resetSelectedReasonId()
    me.setState('select')
    me.hideEditButtons()
  }
  setupButtonEventHandlers(
    element.find('.select-reason-dialog .cancel, .modal-header .close'),
    function () {
      me.hide()
      resetMenuHandler()
    }
  )

  setupButtonEventHandlers(element.find('.add-reason-dialog .cancel'), resetMenuHandler)

  setupButtonEventHandlers($(this._element).find('.save-reason'), function () { me.startSavingReason() })

  setupButtonEventHandlers(
    element.find('.add-new-reason'),
    function () {
      me.resetSelectedReasonId()
      me.resetInputs()
      me.setState('add-new')
    }
  )

  this._editButton = element.find('.edit-this-reason')
  setupButtonEventHandlers(this._editButton, function () { me.startEditingReason() })

  this._deleteButton = element.find('.delete-this-reason')
  setupButtonEventHandlers(this._deleteButton, function () { me.startDeletingReason() })
}
