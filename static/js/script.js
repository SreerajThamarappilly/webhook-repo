// static/js/script.js
async function fetchEvents() {
    const response = await fetch('/events');
    const events = await response.json();
    const eventContainer = document.getElementById('events');
    eventContainer.innerHTML = '';

    events.forEach(event => {
        let message = `${event.author} ${event.action.toLowerCase()} from ${event.from_branch || '-'} to ${event.to_branch} on ${event.timestamp}`;
        const eventElement = document.createElement('p');
        eventElement.textContent = message;
        eventContainer.appendChild(eventElement);
    });
}

setInterval(fetchEvents, 15000);  // Poll every 15 seconds
