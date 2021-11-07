/* global askbot, addExtraCssClasses, AutoCompleter, gettext, Tag, getUniqueWords, notify, showMessage */
(function () {
  var oldTagsHtml = '';
  var tagInput = null;
  var tagsList = null;
  var retagLink = null;

  function restoreEventHandlers() {
    $(document).unbind('click', cancelRetag);
  }

  function cancelRetag() {
    tagsList.html(oldTagsHtml);
    tagsList.removeClass('post-retag');
    tagsList.addClass('post-tags');
    restoreEventHandlers();
    initRetagger();
  }

  function drawNewTags (new_tags) {
    tagsList.empty();
    if (new_tags === '') {
      return;
    }
    new_tags = new_tags.split(/\s+/);
    $.each(new_tags, function (index, name) {
      var tag = new Tag();
      tag.setName(name);
      var li = $('<li></li>');
      tagsList.append(li);
      li.append(tag.getElement());
    });
  }

  function doRetag() {
    $.ajax({
      type: 'POST',
      url: askbot.urls.retag,
      dataType: 'json',
      data: { tags: getUniqueWords(tagInput.val()).join(' ') },
      success: function (json) {
        if (json.success) {
          var new_tags = getUniqueWords(json.new_tags);
          oldTagsHtml = '';
          cancelRetag();
          drawNewTags(new_tags.join(' '));
          if (json.message) {
            notify.show(json.message);
          }
        } else {
          cancelRetag();
          showMessage(tagsList, json.message);
        }
      },
      error: function () {
        showMessage(tagsList, gettext('sorry, something is not right here'));
        cancelRetag();
      }
    });
    return false;
  }

  function setupInputEventHandlers(input) {
    input.keydown(function (e) {
      if ((e.which && e.which === 27) || (e.keyCode && e.keyCode === 27)) {
        cancelRetag();
      }
    });
    $(document).unbind('click', cancelRetag).click(cancelRetag);
    input.closest('form').click(function (e) {
      e.stopPropagation();
    });
  }

  function createRetagForm(old_tags_string) {
    var div = $('<form method="post"></form>');
    tagInput = $('<input id="retag_tags" type="text" autocomplete="off" name="tags" size="30"/>');
    addExtraCssClasses(tagInput, 'textInputClasses');
    //var tagLabel = $('<label for="retag_tags" class="error"></label>');
    //populate input
    var tagAc = new AutoCompleter({
      url: askbot.urls.get_tag_list,
      minChars: 1,
      useCache: true,
      matchInside: true,
      maxCacheLength: 100,
      delay: 10
    });
    tagAc.decorate(tagInput);
    tagAc._results.on('click', function (e) {
      //click on results should not trigger cancelRetag
      e.stopPropagation();
    });
    tagInput.val(old_tags_string);
    div.append(tagInput);
    //div.append(tagLabel);
    setupInputEventHandlers(tagInput);

    //button = $('<input type="submit" />');
    //button.val(gettext('save tags'));
    //div.append(button);
    //setupButtonEventHandlers(button);
    $(document).trigger('askbot.afterCreateRetagForm', [div]);

    div.validate({//copy-paste from utils.js
      rules: {
        tags: {
          required: askbot.settings.tagsAreRequired,
          maxlength: askbot.settings.maxTagsPerPost * askbot.settings.maxTagLength,
          limit_tag_count: true,
          limit_tag_length: true
        }
      },
      messages: {
        tags: {
          required: gettext('tags cannot be empty'),
          maxlength: askbot.messages.tagLimits,
          limit_tag_count: askbot.messages.maxTagsPerPost,
          limit_tag_length: askbot.messages.maxTagLength
        }
      },
      submitHandler: doRetag,
      errorClass: 'retag-error'
    });

    $(document).trigger('askbot.afterSetupValidationRetagForm', [div]);
    return div;
  }

  function getTagsAsString(tags_div) {
    var links = tags_div.find('.js-tag-name');
    var tags_str = '';
    links.each(function (index, element) {
      if (index === 0) {
        //this is pretty bad - we should use Tag.getName()
        tags_str = $(element).data('tagName');
      } else {
        tags_str += ' ' + $(element).data('tagName');
      }
    });
    return tags_str;
  }

  function noopHandler () {
    tagInput.focus();
    tagInput.focus();
    return false;
  }

  function deactivateRetagLink () {
    retagLink.unbind('click').click(noopHandler);
    retagLink.unbind('keypress').keypress(noopHandler);
  }

  function startRetag () {
    tagsList = $('#question-tags');
    oldTagsHtml = tagsList.html();//save to restore on cancel
    var old_tags_string = getTagsAsString(tagsList);
    var retag_form = createRetagForm(old_tags_string);
    tagsList.html('');
    tagsList.append(retag_form);
    tagsList.removeClass('post-tags');
    tagsList.addClass('post-retag');
    tagInput.focus();
    deactivateRetagLink();
    return false;
  }

  function setupClickAndEnterHandler (element, callback) {
    element.unbind('click').click(callback);
    element.unbind('keypress').keypress(function (e) {
      if ((e.which && e.which === 13) || (e.keyCode && e.keyCode === 13)) {
        callback();
      }
    });
  }

  function initRetagger() {
    retagLink = $('#retag');
    setupClickAndEnterHandler(retagLink, startRetag);
  }

  if (askbot.settings.tagSource === 'user-input') {
    initRetagger()
  }
})();


