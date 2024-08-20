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
            <td>${reading.Tilt}</td>
            <td>${reading.Date}</td>
            <td>${reading.Hour}</td>
        `;
        tableBody.appendChild(row);
    });
}
//start the visualization


let temperatureChart, vibrationChart;

document.addEventListener('DOMContentLoaded', function () {
    console.log('RefreshData.js version:', Chart.version);

    // Initialize charts
    function initializeCharts(data) {
        const ctxTemperature = document.getElementById('temperatureChart').getContext('2d');
        const ctxVibration = document.getElementById('vibrationChart').getContext('2d');
        const ctxTilt = document.getElementById('tiltChart').getContext('2d');
        temperatureChart = new Chart(ctxTemperature, {
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

        vibrationChart = new Chart(ctxVibration, {
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
        tiltChart = new Chart(ctxTilt, {
            type: 'line',
            data: {
                labels: data.map(item => item.sample_time_utc),
                datasets: [{
                    label: 'Tilt Measurement',
                    data: data.map(item => item['Tilt']),
                    borderColor: 'rgba(128, 0, 128, 1)',
                    backgroundColor: 'rgba(128, 0, 128, 0.2)',
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
    }
    
function fetchData() {
    const selectedMonth = document.getElementById('monthPicker').value;
    const selectedDate = document.getElementById('datePicker').value;
    let fetchUrl;

    if (selectedDate) {
        const formattedDate = new Date(selectedDate).toISOString().split('T')[0];
        fetchUrl = `/users/data?date=${formattedDate}`;
    } else if (selectedMonth) {
        fetchUrl = `/users/data?month=${selectedMonth}`;
    } else {
        console.error('No date or month selected');
        return;
    }

    console.log(`Fetching data from: ${fetchUrl}`);
    fetch(fetchUrl)
        .then(response => response.json())
        .then(data => {
            console.log(data);
            if (temperatureChart && vibrationChart&& tiltChart) {
                updateCharts(data);
            } else {
                initializeCharts(data);
            }
        })
        .catch(error => {
            console.error('Error fetching data:', error);
        });
}

function updateCharts(data) {
    temperatureChart.data.labels = [];
    temperatureChart.data.datasets[0].data = [];
    vibrationChart.data.labels = [];
    vibrationChart.data.datasets[0].data = [];
    tiltChart.data.labels = [];
    tiltChart.data.datasets[0].data = [];

    if (data.length === 0) {
        console.log("No data available for the selected date or month.");
        document.getElementById('noDataMessage').style.display = 'block';
    } else {
        document.getElementById('noDataMessage').style.display = 'none';

        temperatureChart.data.labels = data.map(item => item.sample_time_utc);
        temperatureChart.data.datasets[0].data = data.map(item => item.Temperature);
        temperatureChart.update();

        vibrationChart.data.labels = data.map(item => item.sample_time_utc);
        vibrationChart.data.datasets[0].data = data.map(item => item['Vibration SD']);
        vibrationChart.update();
        tiltChart.data.labels = data.map(item => item.sample_time_utc);
        tiltChart.data.datasets[0].data = data.map(item => item.Tilt);
        tiltChart.update();
    }

        const stats = calculateStatistics(data);
        displayStatistics(stats);
    }


    function fetchCurrentMonthData() {
        const today = new Date();
        const currentMonth = today.toISOString().split('T')[0].slice(0, 7); // YYYY-MM format
        document.getElementById('monthPicker').value = currentMonth; // Set the month picker to the current month
        fetch(`/users/data?month=${currentMonth}`)
            .then(response => response.json())
            .then(data => {
                console.log(data);
                if (temperatureChart && vibrationChart) {
                    updateCharts(data);
                } else {
                    initializeCharts(data);
                }
            })
            .catch(error => {
                console.error('Error fetching data:', error);
            });
    }


    // const filterButton = document.getElementById('filterButton');
    // filterButton.addEventListener('click', function () {
    //     fetchData();
    // });

    const filterButton = document.getElementById('filterButton');
    filterButton.addEventListener('click', function(event) {
        event.preventDefault(); // Always prevent default to manage behavior manually
    
        // Check if the sensor option is not selected or not 'Bazal'
        
        if (selectedOption == "" ) {
            alert("Error: Please select sensor option to apply filter.");
        } else if(selectedOption == "Bazal"){
            fetchData(); // Only fetch data if 'Bazal' is selected
        }else if(selectedOption == "Blank"){
            alert("not implemented yet");
        }else if(selectedOption == null){
            fetchData();
        }
    });

    const refreshAPIButton = document.getElementById('refreshAPIButton');
    refreshAPIButton.addEventListener('click', function (event) {
        event.preventDefault(); // Prevent default link behavior
        refreshData();
    });

    fetchCurrentMonthData();
});


//show statictics
function calculateStatistics(data) {
    if (data.length === 0) {
        return null;
    }

    const temperatureValues = data.map(item => item.Temperature);
    const vibrationValues = data.map(item => item['Vibration SD']);

    const meanTemperature = temperatureValues.reduce((a, b) => a + b, 0) / temperatureValues.length;
    const meanVibration = vibrationValues.reduce((a, b) => a + b, 0) / vibrationValues.length;

    const maxTemperature = Math.max(...temperatureValues);
    const minTemperature = Math.min(...temperatureValues);

    const maxVibration = Math.max(...vibrationValues);
    const minVibration = Math.min(...vibrationValues);

    const temperatureSD = Math.sqrt(temperatureValues.map(x => Math.pow(x - meanTemperature, 2)).reduce((a, b) => a + b, 0) / temperatureValues.length);
    const vibrationSD = Math.sqrt(vibrationValues.map(x => Math.pow(x - meanVibration, 2)).reduce((a, b) => a + b, 0) / vibrationValues.length);

    console.log('Statistics calculated:', {
        meanTemperature,
        meanVibration,
        maxTemperature,
        minTemperature,
        maxVibration,
        minVibration,
        temperatureSD,
        vibrationSD
    });

    return {
        meanTemperature,
        meanVibration,
        maxTemperature,
        minTemperature,
        maxVibration,
        minVibration,
        temperatureSD,
        vibrationSD
    };
}

function displayStatistics(stats) {
    if (!stats) {
        document.getElementById('statistics').innerHTML = "<p>No data available for statistics.</p>";
        return;
    }

    // Update all statistics in the single card
    document.getElementById('meanTemperature').innerText = `${stats.meanTemperature.toFixed(2)} °C`;
    document.getElementById('meanVibration').innerText = `${stats.meanVibration.toFixed(2)}`;
    document.getElementById('maxTemperature').innerText = `${stats.maxTemperature.toFixed(2)} °C`;
    document.getElementById('minTemperature').innerText = `${stats.minTemperature.toFixed(2)} °C`;
    document.getElementById('maxVibration').innerText = `${stats.maxVibration.toFixed(2)}`;
    document.getElementById('minVibration').innerText = `${stats.minVibration.toFixed(2)}`;
    document.getElementById('temperatureSD').innerText = `${stats.temperatureSD.toFixed(2)}`;
    document.getElementById('vibrationSD').innerText = `${stats.vibrationSD.toFixed(2)}`;

    console.log('Statistics displayed:', stats);
}

