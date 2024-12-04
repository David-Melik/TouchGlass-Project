// Wait until the DOM is fully loaded before running the script
document.addEventListener('DOMContentLoaded', function () {
    // Select the HTML element where the calendar will be rendered
    var calendarEl = document.getElementById('calendar');

    // Create a new FullCalendar instance
    var calendar = new FullCalendar.Calendar(calendarEl, {
        // Set the initial view of the calendar to the month view
        initialView: 'dayGridMonth',
        
        // URL to fetch events from the Flask backend
        events: '/events',

        // Function to handle date clicks (when a date on the calendar is clicked)
        dateClick: function (info) {
            // Prompt the user for their name and age
            let name = prompt("Enter name:");
            let age = prompt("Enter age:");
            let eventDate = info.dateStr;  // Get the clicked date as a string
            
            // Check if both name and age are provided
            if (name && age) {
                // Send an AJAX request to the backend to add an event
                $.ajax({
                    url: '/add_event',  // URL to send the data to
                    method: 'POST',  // HTTP method
                    contentType: 'application/json',  // Specify content type as JSON
                    data: JSON.stringify({ name: name, age: age, date: eventDate }),  // Convert the data to JSON format
                    success: function () {
                        // On success, refetch events to update the calendar display
                        calendar.refetchEvents();
                    }
                });
            }
        },

        // Function to handle event clicks (when an event on the calendar is clicked)
        eventClick: function (info) {
            // Display an alert with event details
            alert("Event: " + info.event.title + "\n" +
                  "Description: " + info.event.extendedProps.description + "\n" +
                  "Location: " + info.event.extendedProps.localisation);
        }
    });

    // Render the calendar in the selected HTML element
    calendar.render();
});
