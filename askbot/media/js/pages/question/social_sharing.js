( 
  function SocialSharing () {
    var SERVICE_DATA = {
      //url - template for the sharing service url, params are for the popup
      identica: {
        url: 'http://identi.ca/notice/new?status_textarea={TEXT}%20{URL}',
        params: 'width=820, height=526,toolbar=1,status=1,resizable=1,scrollbars=1'
      },
      twitter: {
        url: 'http://twitter.com/share?url={URL}&ref=twitbtn&text={TEXT}',
        params: 'width=820,height=526,toolbar=1,status=1,resizable=1,scrollbars=1'
      },
      facebook: {
        url: 'http://www.facebook.com/sharer.php?u={URL}&ref=fbshare&t={TEXT}',
        params: 'width=630,height=436,toolbar=1,status=1,resizable=1,scrollbars=1'
      },
      linkedin: {
        url: 'http://www.linkedin.com/shareArticle?mini=true&url={URL}&title={TEXT}',
        params: 'width=630,height=436,toolbar=1,status=1,resizable=1,scrollbars=1'
      }
    };
    var URL = '';
    var TEXT = '';

    function sharePage(service_name) {
      if (SERVICE_DATA[service_name]) {
        var url = SERVICE_DATA[service_name].url;
        url = url.replace('{TEXT}', TEXT);
        url = url.replace('{URL}', URL);
        var params = SERVICE_DATA[service_name].params;
        if (!window.open(url, 'sharing', params)) {
          window.location.href = url;
        }
        return false;
      }
    };

    return {
      init: function () {
        URL = window.location.href;
        var urlBits = URL.split('/');
        URL = urlBits.slice(0, -2).join('/') + '/';
        TEXT = encodeURIComponent($('h1 > a').text());
        var hashtag = encodeURIComponent(askbot.settings.sharingSuffixText);
        TEXT = TEXT.substr(0, 134 - URL.length - hashtag.length);
        TEXT = TEXT + '... ' + hashtag;
        var fb = $('.js-facebook-share');
        var tw = $('.js-twitter-share');
        var ln = $('.js-linkedin-share');
        var ica = $('.js-identica-share');
        copyAltToTitle(fb);
        copyAltToTitle(tw);
        copyAltToTitle(ln);
        copyAltToTitle(ica);
        setupButtonEventHandlers(fb, function () { share_page('facebook'); });
        setupButtonEventHandlers(tw, function () { share_page('twitter'); });
        setupButtonEventHandlers(ln, function () { share_page('linkedin'); });
        setupButtonEventHandlers(ica, function () { share_page('identica'); });
      }
    };
  }
  SocialSharing.init();
)();
