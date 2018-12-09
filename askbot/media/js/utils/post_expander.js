/**
 * @constructor
 */
var PostExpander = function () {
    SimpleControl.call(this);
    this._handler = this.getExpandHandler();
};
inherits(PostExpander, SimpleControl);

PostExpander.prototype.setRevisionId = function (revId) {
    this._revId = revId;
};

PostExpander.prototype.getRevisionId = function () {
    return this._revId;
};

PostExpander.prototype.showWaitIcon = function () {
    var icon = new WaitIcon();
    this._element.html(icon.getElement());
    icon.show();
};

PostExpander.prototype.updateTheDots = function () {
    var numDots = this._cNumDots + 1;
    if (numDots > this._maxNumDots) {
        numDots = 1;
    }
    this._cNumDots = numDots;
    var dots = '';
    for (var i = 0; i < numDots; i++) {
        dots += '&bull;';
    }
    for (; i < this._maxNumDots; i++) {
        dots += '&nbsp;';
    }
    this._element.html(dots);
};

PostExpander.prototype.stopTheDots = function () {
    clearInterval(this._dotsInterval);
};

PostExpander.prototype.startTheDots = function () {
    var numDots = this._element.find('a').html().length + 2;
    this._maxNumDots = numDots;
    this._cNumDots = 0;
    var dots = '';
    for (var i = 0; i < numDots; i++) {
        dots += '&nbsp;';
    }
    this._element.html(dots);
    var me = this;
    var handler = function () {
        me.updateTheDots();
    };
    this._dotsInterval = setInterval(handler, 150);
};

PostExpander.prototype.getExpandHandler = function () {
    var me = this;
    return function () {
        var element = me.getElement();
        var snippet = $(element.parents('.snippet')[0]);
        $.ajax({
            type: 'GET',
            dataType: 'json',
            data: {'revision_id': me.getRevisionId()},
            url: askbot.urls.getPostRevisionHtml,
            success: function (data) {
                if (data.revision_html) {
                    snippet.hide();
                    snippet.html(data.revision_html);
                    snippet.fadeIn();
                    if (askbot.settings.mathjaxEnabled === true) {
                        runMathJax();
                    }
                }
            }
        });
        me.showWaitIcon();
    };
};
