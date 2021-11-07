/* global askbot, SimpleControl, inherits, showMessage */
/**
 * @constructor
 * @extends {SimpleControl}
 * @param {Comment} comment to upvote
 */
var CommentVoteButton = function (comment) {
    SimpleControl.call(this);
    /**
     * @param {Comment}
     */
    this._comment = comment;
    /**
     * @type {boolean}
     */
    this._voted = false;
    /**
     * @type {number}
     */
    this._score = 0;
};
inherits(CommentVoteButton, SimpleControl);
/**
 * @param {number} score
 */
CommentVoteButton.prototype.setScore = function (score) {
    this._score = score;
    if (this._element) {
        this._element.html(score || '');
    }
    this._element.trigger('askbot.afterSetScore', [this, score]);
};
/**
 * @param {boolean} voted
 */
CommentVoteButton.prototype.setVoted = function (voted) {
    this._voted = voted;
    if (this._element && voted) {
        this._element.addClass('upvoted');
    } else if (this._element) {
        this._element.removeClass('upvoted');
    }
};

CommentVoteButton.prototype.getVoteHandler = function () {
    var me = this;
    var comment = this._comment;
    return function () {
        var cancelVote =  me._voted ? true: false;
        var post_id = me._comment.getId();
        var data = {
            cancel_vote: cancelVote,
            post_id: post_id
        };
        $.ajax({
            type: 'POST',
            data: data,
            dataType: 'json',
            url: askbot.urls.upvote_comment,
            cache: false,
            success: function (data) {
                if (data.success) {
                    me.setScore(data.score);
                    me.setVoted(!cancelVote);
                } else {
                    showMessage(comment.getElement(), data.message, 'after');
                }
            }
        });
    };
};

CommentVoteButton.prototype.decorate = function (element) {
    this._element = element;
    this.setHandler(this.getVoteHandler());

    element = this._element;
    var comment = this._comment;
    /* can't call comment.getElement() here due
     * an issue in the getElement() of comment
     * so use an "illegal" access to comment._element here
     */
    comment._element.mouseenter(function () {
        //outside height may not be known
        //var height = comment.getElement().height();
        //element.height(height);
        element.addClass('hover');
    });
    comment._element.mouseleave(function () {
        element.removeClass('hover');
    });

};

CommentVoteButton.prototype.createDom = function () {
    this._element = this.makeElement('div');
    if (this._score > 0) {
        this._element.html(this._score);
    }
    this._element.addClass('upvote');
    if (this._voted) {
        this._element.addClass('upvoted');
    }
    this.decorate(this._element);
};

