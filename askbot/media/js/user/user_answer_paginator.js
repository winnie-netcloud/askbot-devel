/* global Paginator */
var UserAnswersPaginator = function () {
  Paginator.call(this);
};
inherits(UserAnswersPaginator, Paginator);

UserAnswersPaginator.prototype.renderPage = function (data) {
  $('.js-user-answers').html(data.html);
};

UserAnswersPaginator.prototype.getPageDataUrl = function () {
  return askbot.urls.getTopAnswers;
};

UserAnswersPaginator.prototype.getPageDataUrlParams = function (pageNo) {
  return {
    user_id: askbot.data.viewUserId,
    page_number: pageNo
  };
};
