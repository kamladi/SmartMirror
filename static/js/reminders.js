(function() {

var ReminderList = function() {
	this.loadReminders();
};

ReminderList.prototype.loadReminders = function() {
	this.reminders = [];
	if (localStorage.getItem('reminders')) {
		this.reminders = JSON.parse(localStorage.reminders);
	} else {
		localStorage.reminders = '[]';
	}
};

ReminderList.prototype.addReminder = function(msg) {
	if (!msg || msg.length === 0) {
		throw "undefined reminder message";
	}
	this.reminders.unshift(msg);
	localStorage.reminders = JSON.stringify(this.reminders);
};

ReminderList.prototype.getReminders = function() {
	return this.reminders;
};

window.ReminderList = ReminderList;

})();



