$(document).ready(function(){
    // Create Reminders object
    REMINDERS = new ReminderList();
    refreshReminders();
    getWeather();
    setInterval(function () {
        getWeather();
    }, 5*60*1000);


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
            $this.fadeIn();
        });
    });
}

function speakWeather(weather) {
    var msg = 'The weather in ' + weather.location + " is " + weather.temperature + ' degrees. Conditions are ' + weather.weather_desc;
    speak(msg);
}

function getTwitterNews() {
    $.getJSON('/twitter', function (result) {
        var statuses = result.statuses.map(function (status) {
            return '<li>' + status + '</li>';
        });
        $('#twitter-result').fadeOut('fast', function () {
            $(this).html('<ul>'+statuses.join('')+'</ul>').fadeIn();
        });
    });
}

function refreshReminders() {
    var reminderStrings = REMINDERS.getReminders().map(function (reminder) {
        return '<li>' + reminder + '</li>';
    });
    $('#reminders').html(reminderStrings.join(''));
}

function speak(message) {
    var u = new SpeechSynthesisUtterance();
    u.text = message;
    u.lang = 'en-US';
    speechSynthesis.speak(u);
}
