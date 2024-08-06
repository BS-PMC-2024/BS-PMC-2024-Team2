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

//yuval added
document.addEventListener('DOMContentLoaded', function () {
    console.log('RefreshData.js version:', Chart.version);
    fetch('/users/data')
        .then(response => response.json())
        .then(data => {
            console.log(data);
            const ctxTemperature = document.getElementById('temperatureChart').getContext('2d');
            const ctxVibration = document.getElementById('vibrationChart').getContext('2d');

            // Line Chart for Temperature
            const temperatureChart = new Chart(ctxTemperature, {
                type: 'line',
                data: {
                    labels: data.map(item => item.sample_time_utc),
                    datasets: [{
                        label: 'Temperature (°C)',
                        data: data.map(item => item.Temperature),
                        borderColor: 'rgba(255, 99, 132, 1)',
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
        maintainAspectRatio: false,
                    scales: {
                        x: {
                            type: 'time',
                            time: {
                                unit: 'day'
                            }
                        },
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });

            // Line Chart for Vibration SD
            const vibrationChart = new Chart(ctxVibration, {
                type: 'line',
                data: {
                    labels: data.map(item => item.sample_time_utc),
                    datasets: [{
                        label: 'Vibration SD',
                        data: data.map(item => item['Vibration SD']),
                        borderColor: 'rgba(54, 162, 235, 1)',
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        fill: true
                    }]
                },
                options: {
                    responsive: true,
        maintainAspectRatio: false,
                    scales: {
                        x: {
                            type: 'time',
                            time: {
                                unit: 'day'
                            }
                        },
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        });

});
