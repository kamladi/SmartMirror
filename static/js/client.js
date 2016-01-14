$(document).ready(function(){
    // Create Reminders object
    REMINDERS = new ReminderList();
    refreshReminders();
    getWeather();
    setInterval(function () {
        getWeather();
    }, 5*60*1000);
    Twitter.refreshTweets(function () {
        renderTweet();
        setInterval(function () {
            Twitter.nextTweet();
            renderTweet();
        },5000);
    });
    // todo: refresh twitter list occasionally
    Calendar.refreshEvents(function () {
        renderCalendar();
    });


    // update widgets when buttons are clicked
    $('form#weather').submit(function (event) {
        getWeather();
        return false;
    });

    $('form#twitter').submit(function (event) {
        getTwitterNews();
        return false;
    });


    if (annyang) {
      // voice command handlers
      var commands = {
        'what is the weather today': function() {
          getWeather(true);
        },
        'show me the news': function() {
          getTwitterNews();
        },
        'remind me to *reminder': function(reminder) {
            REMINDERS.addReminder(reminder);
            refreshReminders();
        },
        'remind me *reminder': function(reminder) {
            REMINDERS.addReminder(reminder);
            refreshReminders();
        },
        'good morning bruh': function() {
            speak('how you doing brah');
        },
        'hello': function () {
            alert('hello');
        }
      };

      annyang.addCommands(commands);

      annyang.addCallback('resultNoMatch', function (result) {
          console.log("unkown speech recognized:");
          console.log(result);
      });

      annyang.start();
    }
});

/**
 * helper functions for widgets
 */

function getWeather(speak) {
    $.getJSON('/weather', function (result) {
        if (speak) {
            speakWeather(result);
            return;
        }

        $('#weather-result').fadeOut('fast', function () {
            var $this = $(this);
            $this.find('.weather-temp').html(result.temperature + '&deg;');
            $this.find('.weather-icon').html(Weather.getIconCode(result.icon_url));
            $this.find('.weather-desc').html(result.weather_desc);
            $this.fadeIn();
        });
    });
}

function speakWeather(weather) {
    var msg = 'The weather in ' + weather.location + " is " + weather.temperature + ' degrees. Conditions are ' + weather.weather_desc;
    speak(msg);
}

function renderTweet() {
    var curTweet = Twitter.getCurrTweet();
    curTweet = curTweet.replace('.@','@');
    // remove links from tweets
    curTweet = curTweet.replace(/(?:https?|ftp):\/\/[\n\S]+/g,'');
    $('#twitter-username').text(Twitter.getUsername());
    $('#tweet').fadeOut('fast', function () {
        $(this).html(curTweet).fadeIn();
    });
}

function refreshReminders() {
    var reminderStrings = REMINDERS.getReminders().map(function (reminder) {
        return '<li>' + reminder + '</li>';
    });
    $('#reminders').html(reminderStrings.join(''));
}

function renderCalendar() {
    var calendarString = '';
    Calendar.getEvents().forEach(function (event) {
        var date = new Date(event.start);
        var timeString = date.toString('hh:mm tt');
        calendarString += '<li>';
        calendarString += '<div class="event-start">'+timeString+'</div>';
        calendarString += '<div class="event-title">'+event.title+'</div>';
        calendarString += '</li>';
    });
    $('.events').html(calendarString);
}

function speak(message) {
    var u = new SpeechSynthesisUtterance();
    u.text = message;
    u.lang = 'en-US';
    speechSynthesis.speak(u);
}
