/**
* the dropdown menu with selection of reasons
* to reject posts and a button that starts menu to
* manage the list of reasons
*/
var ModerateWithReasonMenu = function (reasonType, handlerFactory) {
  this.reasonType = reasonType;
  this.handlerFactory = handlerFactory;
  WrappedElement.call(this);
};
inherits(ModerateWithReasonMenu, WrappedElement);

ModerateWithReasonMenu.prototype.setupDeclinePostHandler = function (button) {
  var reasonId = button.data('reasonId');
  setupButtonEventHandlers(button, this.handlerFactory(reasonId));
};

ModerateWithReasonMenu.prototype.addReason = function (id, title, isPredefined) {
  var li = this.makeElement('li');
  var button = this.makeElement('a');
  li.append(button);
  if (isPredefined) {
    title += ' *'
  }
  button.html(title);
  button.data('reasonId', id);
  button.attr('data-reason-id', id);
  this._addReasonBtn.before(li);

  this.setupDeclinePostHandler(button);
};

ModerateWithReasonMenu.prototype.removeReason = function (id) {
  var btn = this._element.find('a[data-reason-id="' + id + '"]');
  btn.parent().remove();
};

ModerateWithReasonMenu.prototype.makeManageReasonsBtn = function () {
  var btn = this.makeElement('li');
  var anchor = this.makeElement('a');
  anchor.addClass('apply-reason');
  anchor.html(gettext('add/manage reject reasons'));
  btn.append(anchor);
  return btn;
};

ModerateWithReasonMenu.prototype.decorate = function (element) {
  var reasons;
  this._element = element;
  //activate dropdown menu
  element.dropdown();

  var ul = this.makeElement('ul');
  ul.addClass('dropdown-menu');
  ul.addClass('select-' + this.reasonType + '-reason');
  this._element.append(ul);
  this._reasonList = ul;

  var addReasonBtn = this.makeManageReasonsBtn();
  this._addReasonBtn = addReasonBtn;
  this._reasonList.append(addReasonBtn);
  var manageReasonsDialog = new ManageModerationReasonsDialog(this.reasonType);
  manageReasonsDialog.decorate($('#manage-' + this.reasonType + '-reasons-modal'));
  this._manageReasonsDialog = manageReasonsDialog;
  manageReasonsDialog.setMenu(this);
  setupButtonEventHandlers(addReasonBtn, function () { manageReasonsDialog.show(); });

  for (var idx = 0; idx < askbot.data.moderationReasons.length; idx++) {
    var reason = askbot.data.moderationReasons[idx];
    if (reason.reason_type === this.reasonType) {
      this.addReason(reason.id, reason.title, reason.is_predefined);
    }
  }

};
