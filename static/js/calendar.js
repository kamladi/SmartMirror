Calendar = {
	refreshEvents: function(cb) {
		var self = this;
		$.getJSON('/calendar', function (result) {
			self.events = result.events;
			if (cb) {
				cb();
			}
		});
	},
	getEvents: function () {
		return this.events;
	}
};
