function refreshData() {
    fetch('/users/refresh_API_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data) {
            displayData(data);
        } else {
            alert('Error: ' + data.error);
        }
    })
    .catch(error => {
        alert('Error: ' + error);
    });
}

function displayData(data) {
    const tableBody = document.getElementById('dataTableBody');
    tableBody.innerHTML = ''; // Clear existing data

    data.forEach(reading => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${reading.Temperature}</td>
            <td>${reading.Vibration}</td>
            <td>${reading.Impact}</td>
            <td>${reading.Date}</td>
            <td>${reading.Hour}</td>
        `;
        tableBody.appendChild(row);
    });
}

document.addEventListener("DOMContentLoaded", function() {
    document.getElementById('refreshAPIButton').addEventListener('click', function(event) {
        event.preventDefault(); // Prevent the default link behavior
        refreshData();
    });
});
