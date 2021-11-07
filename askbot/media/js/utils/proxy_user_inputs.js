/* global AutoCompleter, askbot */
$(document).ready(function () {
  var proxyUserNameInput = $('#id_post_author_username');
  var proxyUserEmailInput = $('#id_post_author_email');
  if (proxyUserNameInput.length === 1) {
    var userSelectHandler = function (data) {
      proxyUserEmailInput.val(data.data[0]);
    };
    var fakeUserAc = new AutoCompleter({
      url: askbot.urls.get_users_info,
      minChars: 1,
      useCache: true,
      matchInside: true,
      maxCacheLength: 100,
      delay: 10,
      onItemSelect: userSelectHandler
    });
    fakeUserAc.decorate(proxyUserNameInput);
  }
});
