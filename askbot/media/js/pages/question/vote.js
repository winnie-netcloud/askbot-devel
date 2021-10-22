/**
 * legacy Vote class
 * handles all sorts of vote-like operations
 */
var Vote = (function () {
    // All actions are related to a question
    var questionId;
    //question slug to build redirect urls
    var questionSlug;
    // The object we operate on actually. It can be a question or an answer.
    var postId;
    var questionAuthorId;
    var currentUserId;
    var answerContainerIdPrefix = 'post-id-';
    var voteContainerId = 'js-vote-buttons';
    var imgIdPrefixAccept = 'answer-img-accept-';
    var imgIdPrefixQuestionVotedown = 'question-img-downvote-';
    var imgIdPrefixAnswerVoteup = 'answer-img-upvote-';
    var imgIdPrefixAnswerVotedown = 'answer-img-downvote-';
    var voteNumberClass = 'vote-number';
    var offensiveIdPrefixQuestionFlag = 'question-offensive-flag-';
    var removeOffensiveIdPrefixQuestionFlag = 'question-offensive-remove-flag-';
    var removeAllOffensiveIdPrefixQuestionFlag = 'question-offensive-remove-all-flag-';
    var offensiveIdPrefixAnswerFlag = 'answer-offensive-flag-';
    var removeOffensiveIdPrefixAnswerFlag = 'answer-offensive-remove-flag-';
    var removeAllOffensiveIdPrefixAnswerFlag = 'answer-offensive-remove-all-flag-';
    var offensiveClassFlag = 'offensive-flag';
    var questionControlsId = 'question-controls';
    var removeAnswerLinkIdPrefix = 'answer-delete-link-';
    var questionSubscribeUpdates = 'question-subscribe-updates';
    var questionSubscribeSidebar = 'question-subscribe-sidebar';

    var acceptAnonymousMessage = gettext('insufficient privilege');

    var pleaseLogin = ' <a href="' + askbot.urls.user_signin + '">' + gettext('please login') + '</a>';

    //todo: this below is probably not used
    var subscribeAnonymousMessage = gettext('anonymous users cannot subscribe to questions') + pleaseLogin;
    var voteAnonymousMessage = gettext('anonymous users cannot vote') + pleaseLogin;
    //there were a couple of more messages...
    var offensiveAnonymousMessage = gettext('anonymous users cannot flag offensive posts') + pleaseLogin;
    var removeConfirmation = gettext('confirm delete');
    var removeAnonymousMessage = gettext('anonymous users cannot delete/undelete') + pleaseLogin;
    var recoveredMessage = gettext('post recovered');
    var deletedMessage = gettext('post deleted');

    var VoteType = {
        questionUpVote: 1,
        questionDownVote: 2,
        answerUpVote: 5,
        answerDownVote:6,

        acceptAnswer: 0,
        offensiveQuestion: 7,
        removeOffensiveQuestion: 7.5,
        removeAllOffensiveQuestion: 7.6,
        offensiveAnswer: 8,
        removeOffensiveAnswer: 8.5,
        removeAllOffensiveAnswer: 8.6,
        removeQuestion: 9,//deprecate
        removeAnswer: 10,//deprecate
        questionSubscribeUpdates: 11,
        questionUnsubscribeUpdates: 12
    };

    var getQuestionVoteUpButton = function () {
        return $('#js-post-upvote-btn-' + questionId);
    };
    var getQuestionVoteDownButton = function () {
        return $('#js-post-downvote-btn-' + questionId);
    };
    var getAnswerVoteUpButtons = function () {
        var answerVoteUpButton = 'div.' + voteContainerId + ' div[id^="js-post-upvote-btn-"]';
        return $(answerVoteUpButton);
    };
    var getAnswerVoteDownButtons = function () {
        var answerVoteDownButton = 'div.' + voteContainerId + ' div[id^="' + imgIdPrefixAnswerVotedown + '"]';
        return $(answerVoteDownButton);
    };
    var getAnswerVoteUpButton = function (id) {
        return $('#js-post-upvote-btn-' + id);
    };
    var getAnswerVoteDownButton = function (id) {
        var answerVoteDownButton = 'div.' + voteContainerId + ' div[id="' + imgIdPrefixAnswerVotedown + id + '"]';
        return $(answerVoteDownButton);
    };

    var setVoteImage = function (voteType, undo, object) {
      var flag = undo ? false : true;
      if (object.hasClass('js-active')) {
        object.removeClass('js-active');
      } else {
        object.addClass('js-active');
      }

      if (undo) {
        if (voteType === VoteType.questionUpVote || voteType === VoteType.questionDownVote) {
          $(getQuestionVoteUpButton()).removeClass('js-active');
          $(getQuestionVoteDownButton()).removeClass('js-active');
        } else {
          $(getAnswerVoteUpButton(postId)).removeClass('js-active');
          $(getAnswerVoteDownButton(postId)).removeClass('js-active');
        }
      }
    };

    var setVoteNumber = function (object, number) {
        var voteNumber = object.parent('div.' + voteContainerId).find('div.' + voteNumberClass);
        $(voteNumber).text(number);
    };

    var callback_vote = function (object, voteType, data) {
        /*jshint eqeqeq:false */
        if (data.success == '0') {
            showMessage(object, data.message);
            return;
        } else {
            if (data.status == '1') {
                setVoteImage(voteType, true, object);
                object.trigger('askbot.voteDown', [object, data]);
            } else {
                setVoteImage(voteType, false, object);
                object.trigger('askbot.voteUp', [object, data]);
            }
            setVoteNumber(object, data.count);
            if (data.message && data.message.length > 0) {
                showMessage(object, data.message);
            }
            return;
        }
        /*jshint eqeqeq:true */
    };


    var getOffensiveQuestionFlag = function () {
        var offensiveQuestionFlag = 'span[id^="' + offensiveIdPrefixQuestionFlag + '"]';
        return $(offensiveQuestionFlag);
    };

    var getRemoveOffensiveQuestionFlag = function () {
        var removeOffensiveQuestionFlag = 'span[id^="' + removeOffensiveIdPrefixQuestionFlag + '"]';
        return $(removeOffensiveQuestionFlag);
    };

    var getRemoveAllOffensiveQuestionFlag = function () {
        var removeAllOffensiveQuestionFlag = 'span[id^="' + removeAllOffensiveIdPrefixQuestionFlag + '"]';
        return $(removeAllOffensiveQuestionFlag);
    };

    var getOffensiveAnswerFlags = function () {
        var offensiveQuestionFlag = 'span[id^="' + offensiveIdPrefixAnswerFlag + '"]';
        return $(offensiveQuestionFlag);
    };

    var getRemoveOffensiveAnswerFlag = function () {
        var removeOffensiveAnswerFlag = 'span[id^="' + removeOffensiveIdPrefixAnswerFlag + '"]';
        return $(removeOffensiveAnswerFlag);
    };

    var getRemoveAllOffensiveAnswerFlag = function () {
        var removeAllOffensiveAnswerFlag = 'span[id^="' + removeAllOffensiveIdPrefixAnswerFlag + '"]';
        return $(removeAllOffensiveAnswerFlag);
    };

    var getquestionSubscribeUpdatesCheckbox = function () {
        return $('#' + questionSubscribeUpdates);
    };

    var getquestionSubscribeSidebarCheckbox = function () {
        return $('#' + questionSubscribeSidebar);
    };

    var getremoveAnswersLinks = function () {
        var removeAnswerLinks = 'a[id^="' + removeAnswerLinkIdPrefix + '"]';
        return $(removeAnswerLinks);
    };

    var bindEvents = function () {
        // accept answers
        var acceptedButtons = 'div.' + voteContainerId + ' div[id^="' + imgIdPrefixAccept + '"]';
        $(acceptedButtons).unbind('click').click(function (event) {
            Vote.accept($(event.target));
        });

        // question vote up
        var questionVoteUpButton = getQuestionVoteUpButton();
        questionVoteUpButton.unbind('click').click(function (event) {
            Vote.vote($(event.target), VoteType.questionUpVote);
        });

        var questionVoteDownButton = getQuestionVoteDownButton();
        questionVoteDownButton.unbind('click').click(function (event) {
            Vote.vote($(event.target), VoteType.questionDownVote);
        });

        var answerVoteUpButton = getAnswerVoteUpButtons();
        answerVoteUpButton.unbind('click').click(function (event) {
            Vote.vote($(event.target), VoteType.answerUpVote);
        });

        var answerVoteDownButton = getAnswerVoteDownButtons();
        answerVoteDownButton.unbind('click').click(function (event) {
            Vote.vote($(event.target), VoteType.answerDownVote);
        });

        getOffensiveQuestionFlag().unbind('click').click(function (event) {
            Vote.offensive(this, VoteType.offensiveQuestion);
        });

        getRemoveOffensiveQuestionFlag().unbind('click').click(function (event) {
            Vote.remove_offensive(this, VoteType.removeOffensiveQuestion);
        });

        getRemoveAllOffensiveQuestionFlag().unbind('click').click(function (event) {
            Vote.remove_all_offensive(this, VoteType.removeAllOffensiveQuestion);
        });

        getOffensiveAnswerFlags().unbind('click').click(function (event) {
            Vote.offensive(this, VoteType.offensiveAnswer);
        });

        getRemoveOffensiveAnswerFlag().unbind('click').click(function (event) {
            Vote.remove_offensive(this, VoteType.removeOffensiveAnswer);
        });

        getRemoveAllOffensiveAnswerFlag().unbind('click').click(function (event) {
            Vote.remove_all_offensive(this, VoteType.removeAllOffensiveAnswer);
        });

        getquestionSubscribeUpdatesCheckbox().unbind('click').click(function (event) {
            //despeluchar esto
            if (this.checked) {
                getquestionSubscribeSidebarCheckbox().attr({'checked': true});
                Vote.vote($(event.target), VoteType.questionSubscribeUpdates);
            } else {
                getquestionSubscribeSidebarCheckbox().attr({'checked': false});
                Vote.vote($(event.target), VoteType.questionUnsubscribeUpdates);
            }
        });

        getquestionSubscribeSidebarCheckbox().unbind('click').click(function (event) {
            if (this.checked) {
                getquestionSubscribeUpdatesCheckbox().attr({'checked': true});
                Vote.vote($(event.target), VoteType.questionSubscribeUpdates);
            } else {
                getquestionSubscribeUpdatesCheckbox().attr({'checked': false});
                Vote.vote($(event.target), VoteType.questionUnsubscribeUpdates);
            }
        });

        getremoveAnswersLinks().unbind('click').click(function (event) {
            Vote.remove(this, VoteType.removeAnswer);
        });
    };

    var submit = function (object, voteType, callback) {
        //this function submits votes
        $.ajax({
            type: 'POST',
            cache: false,
            dataType: 'json',
            url: askbot.urls.vote_url,
            data: { type: voteType, postId: postId },
            error: handleFail,
            success: function (data) {
                callback(object, voteType, data);
            }
        });
    };

    var handleFail = function (xhr, msg) {
        alert('Callback invoke error: ' + msg);
    };

    // callback function for Accept Answer action
    var callback_accept = function (object, voteType, data) {
        /*jshint eqeqeq:false */
        if (data.allowed == '0' && data.success == '0') {
            showMessage(object, acceptAnonymousMessage);
        } else if (data.allowed == '-1') {
            var message = interpolate(
                gettext('sorry, you cannot %(accept_own_answer)s'),
                {'accept_own_answer': askbot.messages.acceptOwnAnswer},
                true
            );
            showMessage(object, message);
        } else if (data.status == '1') {
            $('#' + answerContainerIdPrefix + postId).removeClass('accepted-answer');
            object.trigger('askbot.unacceptAnswer', [object, data]);
        } else if (data.success == '1') {
            var answers = ('div[id^="' + answerContainerIdPrefix + '"]');
            $(answers).removeClass('accepted-answer');
            $('#' + answerContainerIdPrefix + postId).addClass('accepted-answer');
            object.trigger('askbot.acceptAnswer', [object, data]);
        } else {
            showMessage(object, data.message);
        }
        /*jshint eqeqeq:true */
    };

    var callback_offensive = function (object, voteType, data) {
        /*jshint eqeqeq:false */
        //todo: transfer proper translations of these from i18n.js
        //to django.po files
        //_('anonymous users cannot flag offensive posts') + pleaseLogin;
        if (data.success == '1') {
            if (data.count > 0) {
                $(object).children('span[class="darkred"]').text('(' + data.count + ')');
            } else {
                $(object).children('span[class="darkred"]').text('');
            }

            // Change the link text and rebind events
            $(object).find('.question-flag').html(gettext('remove flag'));
            var obj_id = $(object).attr('id');
            $(object).attr('id', obj_id.replace('flag-', 'remove-flag-'));

            getRemoveOffensiveQuestionFlag().unbind('click').click(function (event) {
                Vote.remove_offensive(this, VoteType.removeOffensiveQuestion);
            });

            getRemoveOffensiveAnswerFlag().unbind('click').click(function (event) {
                Vote.remove_offensive(this, VoteType.removeOffensiveAnswer);
            });
        } else {
            object = $(object);
            showMessage(object, data.message);
        }
        /*jshint eqeqeq:true */
    };

    var callback_remove_offensive = function (object, voteType, data) {
        /*jshint eqeqeq:false */
        //todo: transfer proper translations of these from i18n.js
        //to django.po files
        //_('anonymous users cannot flag offensive posts') + pleaseLogin;
        if (data.success == '1') {
            if (data.count > 0) {
                $(object).children('span[class="darkred"]').text('(' + data.count + ')');
            } else {
                $(object).children('span[class="darkred"]').text('');
                // Remove "remove all flags link" since there are no more flags to remove
                var remove_all = $(object).siblings('span.offensive-flag[id*="-offensive-remove-all-flag-"]');
                $(remove_all).next('span.sep').remove();
                $(remove_all).remove();
            }
            // Change the link text and rebind events
            $(object).find('.question-flag').html(gettext('flag offensive'));
            var obj_id = $(object).attr('id');
            $(object).attr('id', obj_id.replace('remove-flag-', 'flag-'));

            getOffensiveQuestionFlag().unbind('click').click(function (event) {
                Vote.offensive(this, VoteType.offensiveQuestion);
            });

            getOffensiveAnswerFlags().unbind('click').click(function (event) {
                Vote.offensive(this, VoteType.offensiveAnswer);
            });
        } else {
            object = $(object);
            showMessage(object, data.message);
        }
        /*jshint eqeqeq:true */
    };

    var callback_remove_all_offensive = function (object, voteType, data) {
        /*jshint eqeqeq:false */
        //todo: transfer proper translations of these from i18n.js
        //to django.po files
        //_('anonymous users cannot flag offensive posts') + pleaseLogin;
        if (data.success == '1') {
            if (data.count > 0) {
                $(object).children('span[class="darkred"]').text('(' + data.count + ')');
            } else {
                $(object).children('span[class="darkred"]').text('');
            }
            // remove the link. All flags are gone
            var remove_own = $(object).siblings('span.offensive-flag[id*="-offensive-remove-flag-"]');
            $(remove_own).find('.question-flag').html(gettext('flag offensive'));
            $(remove_own).attr('id', $(remove_own).attr('id').replace('remove-flag-', 'flag-'));

            $(object).next('span.sep').remove();
            $(object).remove();

            getOffensiveQuestionFlag().unbind('click').click(function (event) {
                Vote.offensive(this, VoteType.offensiveQuestion);
            });

            getOffensiveAnswerFlags().unbind('click').click(function (event) {
                Vote.offensive(this, VoteType.offensiveAnswer);
            });
        } else {
            object = $(object);
            showMessage(object, data.message);
        }
        /*jshint eqeqeq:true */
    };

    var callback_remove = function (object, voteType, data) {
        /*jshint eqeqeq:false */
        if (data.success == '1') {
            if (removeActionType == 'delete') {
                postNode.addClass('deleted');
                postRemoveLink.innerHTML = gettext('undelete');
                showMessage(object, deletedMessage);
            } else if (removeActionType == 'undelete') {
                postNode.removeClass('deleted');
                postRemoveLink.innerHTML = gettext('delete');
                showMessage(object, recoveredMessage);
            }
        } else {
            showMessage(object, data.message);
        }
        /*jshint eqeqeq:true */
    };

    return {
        init: function (qId, qSlug, questionAuthor, userId) {
            questionId = qId;
            questionSlug = qSlug;
            questionAuthorId = questionAuthor;
            currentUserId = '' + userId;//convert to string
            bindEvents();
        },

        //accept answer
        accept: function (object) {
            object = object.closest('.answer-img-accept');
            postId = object.attr('id').substring(imgIdPrefixAccept.length);
            submit(object, VoteType.acceptAnswer, callback_accept);
        },

        vote: function (object, voteType) {
            object = object.closest('.js-post-vote');
            if (!currentUserId || currentUserId.toUpperCase() === 'NONE') {
                if (voteType === VoteType.questionSubscribeUpdates || voteType === VoteType.questionUnsubscribeUpdates) {
                    getquestionSubscribeSidebarCheckbox().removeAttr('checked');
                    getquestionSubscribeUpdatesCheckbox().removeAttr('checked');
                    showMessage(object, subscribeAnonymousMessage);
                } else {
                    showMessage(
                        $(object),
                        voteAnonymousMessage.replace(
                                '{{QuestionID}}',
                                questionId
                            ).replace(
                                '{{questionSlug}}',
                                questionSlug
                            )
                    );
                }
                return false;
            }
            // up and downvote processor
            if (voteType === VoteType.answerUpVote) {
                postId = object.attr('id').substring(imgIdPrefixAnswerVoteup.length);
            } else if (voteType === VoteType.answerDownVote) {
                postId = object.attr('id').substring(imgIdPrefixAnswerVotedown.length);
            } else {
                postId = questionId;
            }

            submit(object, voteType, callback_vote);
        },
        //flag offensive
        offensive: function (object, voteType) {
            if (!currentUserId || currentUserId.toUpperCase() === 'NONE') {
                showMessage(
                    $(object),
                    offensiveAnonymousMessage.replace(
                            '{{QuestionID}}',
                            questionId
                        ).replace(
                            '{{questionSlug}}',
                            questionSlug
                        )
                );
                return false;
            }
            postId = object.id.substr(object.id.lastIndexOf('-') + 1);
            submit(object, voteType, callback_offensive);
        },
        //remove flag offensive
        remove_offensive: function (object, voteType) {
            if (!currentUserId || currentUserId.toUpperCase() === 'NONE') {
                showMessage(
                    $(object),
                    offensiveAnonymousMessage.replace(
                            '{{QuestionID}}',
                            questionId
                        ).replace(
                            '{{questionSlug}}',
                            questionSlug
                        )
                );
                return false;
            }
            postId = object.id.substr(object.id.lastIndexOf('-') + 1);
            submit(object, voteType, callback_remove_offensive);
        },
        remove_all_offensive: function (object, voteType) {
            if (!currentUserId || currentUserId.toUpperCase() === 'NONE') {
                showMessage(
                    $(object),
                    offensiveAnonymousMessage.replace(
                            '{{QuestionID}}',
                            questionId
                        ).replace(
                            '{{questionSlug}}',
                            questionSlug
                        )
                );
                return false;
            }
            postId = object.id.substr(object.id.lastIndexOf('-') + 1);
            submit(object, voteType, callback_remove_all_offensive);
        },
        //delete question or answer (comments are deleted separately)
        remove: function (object, voteType) {
            if (!currentUserId || currentUserId.toUpperCase() === 'NONE') {
                showMessage(
                    $(object),
                    removeAnonymousMessage.replace(
                            '{{QuestionID}}',
                            questionId
                        ).replace(
                            '{{questionSlug}}',
                            questionSlug
                        )
                    );
                return false;
            }
            bits = object.id.split('-');
            postId = bits.pop();/* this seems to be used within submit! */
            postType = bits.shift();

            var do_proceed = false;
            postNode = $('#post-id-' + postId);
            postRemoveLink = object;
            if (postNode.hasClass('deleted')) {
                removeActionType = 'undelete';
                do_proceed = true;
            } else {
                removeActionType = 'delete';
                do_proceed = confirm(removeConfirmation);
            }
            if (do_proceed) {
                submit($(object), voteType, callback_remove);
            }
        }
    };
})();
