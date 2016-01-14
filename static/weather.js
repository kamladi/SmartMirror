Weather = {
	getIconCode: function(icon_url) {
    var matcher = /\/(\w+).gif$/;
    var code = matcher.exec(icon_url);
    if (code) {
      code = code[1];
    } else {
      // We can't find the code
      code = null;
    }
    switch(code) {
      case "chanceflurries":
      case "chancesnow":
        return "p";
      case "/ig/images/weather/flurries.gif":
        return "]";
      case "chancesleet":
        return "4";
      case "chancerain":
        return "7";
      case "chancetstorms":
        return "x";
      case "tstorms":
      case "nt_tstorms":
        return "z";
      case "clear":
      case "sunny":
        return "v";
      case "cloudy":
        return "`";
      case "flurries":
      case "nt_flurries":
        return "]";
      case "fog":
      case "hazy":
      case "nt_fog":
      case "nt_hazy":
        return "g";
      case "mostlycloudy":
      case "partlysunny":
      case "partlycloudy":
      case "mostlysunny":
        return "1";
      case "sleet":
      case "nt_sleet":
        return "3";
      case "rain":
      case "nt_rain":
        return "6";
      case "snow":
      case "nt_snow":
        return "o";
      // Night Specific
      case "nt_chanceflurries":
        return "a";
      case "nt_chancerain":
        return "8";
      case "nt_chancesleet":
        return "5";
      case "nt_chancesnow":
        return "[";
      case "nt_chancetstorms":
        return "c";
      case "nt_clear":
      case "nt_sunny":
        return "/";
      case "nt_cloudy":
        return "2";
      case "nt_mostlycloudy":
      case "nt_partlysunny":
      case "nt_partlycloudy":
      case "nt_mostlysunny":
        return "2";

      default:
        console.log("MISSING", code);
        return "T";
    }
  }
};
