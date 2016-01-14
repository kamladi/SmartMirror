Twitter = {
	refreshTweets: function(cb) {
		var self = this;
		$.getJSON('/twitter', function (result) {
			self.username = '@' + result.username;
			self.tweets = result.statuses;
			self.numTweets = result.statuses.length;
			self.currTweetIndex = 0;
			if (cb) {
				cb();
			}
		});
	},
	nextTweet: function() {
		this.currTweetIndex = (this.currTweetIndex+1) % this.numTweets;
	},
	getCurrTweet: function () {
		return this.tweets[this.currTweetIndex];
	},
	getUsername: function () {
		return this.username;
	}
};
