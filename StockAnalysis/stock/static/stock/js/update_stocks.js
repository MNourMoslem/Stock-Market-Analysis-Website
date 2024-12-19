function update_stocks() {
    const token = 'GyGA3akK8hGmxlmgali2aX21nl5KD5axm'; // Replace with your actual secret token

    fetch('/api/update_stocks', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}` // Send the token in the Authorization header
        },
        body: JSON.stringify({}) // You can send any necessary data here
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Stocks updated successfully:', data);
    })
    .catch(error => {
        console.error('Error updating stocks:', error);
    });
}

function checkTimeAndUpdate() {
    const now = new Date();
    const utcOffset = -5; // Eastern Standard Time (EST) without Daylight Saving Time
    const estTime = new Date(now.getTime() + (utcOffset * 60 * 60 * 1000));

    if (estTime.getHours() === 16 && estTime.getMinutes() === 0) {
        update_stocks();
    }
}

// Check every minute
setInterval(checkTimeAndUpdate, 60000); 