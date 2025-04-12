document.addEventListener("DOMContentLoaded", function () {
    const scanBtn = document.getElementById("scan-btn");
    const resultText = document.getElementById("result");
    const closeBtn = document.getElementById("close-btn");
    const chartContainer = document.querySelector(".chart-container");
    const toggleThemeBtn = document.getElementById("toggle-theme"); // dark mode button
    const body = document.body;

    let lineChartInstance = null;
    let pieChartInstance = null;

    // Set theme from localStorage
    if (localStorage.getItem("theme") === "dark") {
        body.classList.add("dark-mode");
    }

    // Toggle theme
    toggleThemeBtn?.addEventListener("click", function () {
        body.classList.toggle("dark-mode");
        localStorage.setItem("theme", body.classList.contains("dark-mode") ? "dark" : "light");

        // Refresh charts with correct text color
        if (lineChartInstance) updateLineChart(lineChartInstance.data);
        if (pieChartInstance) updatePieChart(Object.fromEntries(pieChartInstance.data.labels.map((l, i) => [l, pieChartInstance.data.datasets[0].data[i]])));
    });

    // SCAN Button Click
    scanBtn.addEventListener("click", async function () {
        scanBtn.disabled = true;
        scanBtn.innerHTML = `<span class="spinner-border spinner-border-sm"></span> Scanning...`;
        resultText.textContent = "";
        chartContainer.style.display = "none";
        closeBtn.style.display = "none";

        try {
            const response = await fetch("/scan");
            const data = await response.json();

            if (data.status === "success") {
                body.classList.add("scanned");
                scanBtn.textContent = "Scan Complete!";
                resultText.innerHTML = `Anomalies Detected: <b>${data.anomalies}</b>`;
                chartContainer.style.display = "flex";
                closeBtn.style.display = "inline-block";

                updateLineChart(data.traffic_data);
                updatePieChart(data.anomaly_distribution);
            } else {
                scanBtn.textContent = "Scan Failed!";
                resultText.textContent = `Error: ${data.message}`;
            }
        } catch (error) {
            scanBtn.textContent = "Scan Failed!";
            resultText.textContent = `Error: ${error.message}`;
        } finally {
            scanBtn.disabled = false;
        }
    });

    // CLOSE Button
    closeBtn.addEventListener("click", function () {
        chartContainer.style.display = "none";
        closeBtn.style.display = "none";
        resultText.textContent = "";
        scanBtn.textContent = "Scan Network";
        body.classList.remove("scanned");

        if (lineChartInstance) {
            lineChartInstance.destroy();
            lineChartInstance = null;
        }
        if (pieChartInstance) {
            pieChartInstance.destroy();
            pieChartInstance = null;
        }
    });

    // Line Chart
    function updateLineChart(data) {
        const ctx = document.getElementById("lineChart").getContext("2d");
        const labels = data.map(item => item.time);
        const values = data.map(item => item.count);

        if (lineChartInstance) lineChartInstance.destroy();

        lineChartInstance = new Chart(ctx, {
            type: "line",
            data: {
                labels: labels,
                datasets: [{
                    label: "Packets Over Time",
                    data: values,
                    borderColor: "blue",
                    backgroundColor: "rgba(0, 0, 255, 0.1)",
                    fill: true,
                    tension: 0.3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: {
                            color: getTextColor()
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: { color: getTextColor() }
                    },
                    y: {
                        ticks: { color: getTextColor() }
                    }
                }
            }
        });
    }

    // Pie Chart
    function updatePieChart(distribution) {
        const canvas = document.getElementById("anomalyPieChart");
        if (!canvas) {
            console.warn("Pie chart canvas not found!");
            return;
        }
    
        const ctx = canvas.getContext("2d");
        const labels = Object.keys(distribution);
        const values = Object.values(distribution);
    
        const allZero = values.every(v => v === 0);
    
        if (pieChartInstance) pieChartInstance.destroy();
    
        if (allZero) {
            // Render a pie chart with a single green slice saying "No Anomalies"
            pieChartInstance = new Chart(ctx, {
                type: "pie",
                data: {
                    labels: ["No Anomalies"],
                    datasets: [{
                        data: [1],
                        backgroundColor: ["#28a745"] // green
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: {
                                color: getTextColor()
                            }
                        }
                    }
                }
            });
        } else {
            // Render normal pie chart with actual data
            pieChartInstance = new Chart(ctx, {
                type: "pie",
                data: {
                    labels,
                    datasets: [{
                        data: values,
                        backgroundColor: ["#ff6384", "#36a2eb", "#cc65fe", "#ffce56"]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: {
                                color: getTextColor()
                            }
                        }
                    }
                }
            });
        }
    }    
    function getTextColor() {
        return document.body.classList.contains("dark-mode") ? "#fff" : "#000";
    }
});
