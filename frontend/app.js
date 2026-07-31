const BACKEND_URL = 'https://autoval-test.onrender.com/predict' // Temporary js backend ko, papalitan to. Galing sya dito: https://github.com/Naourr/autoval-test/blob/main/server.js

const carForm = document.getElementById('carForm')
const result = document.getElementById('result')

let myChart = null
function initCharts() {
    const lineCtx = document.getElementById('depreciationChart').getContext('2d')

    myChart = new Chart(lineCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Market Price vs. Mileage Depreciation Curve',
                data: [],
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                borderWidth: 3,
                tension: 0.3,
                fill: true
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: { beginAtZero: false, title: { display: true, text: 'Estimated Value ($)' } },
                x: { title: { display: true, text: 'Odometer Mileage Status' } }
            }
        }
    })
}
initCharts()

carForm.addEventListener('submit', async (e) => {
    e.preventDefault()
    const brand = document.getElementById('brand').value
    const year = document.getElementById('year').value
    const mileage = document.getElementById('mileage').value
    const transmission = document.getElementById('transmission').value
    const condition = document.getElementById('condition').value

    result.innerHTML = '<em>Connecting to server..</em>'

    try {
        const response = await fetch(BACKEND_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({brand, year, mileage, transmission, condition})
        })

        if (!response.ok) throw new Error('Network response failed server-side')

		const data = await response.json()
		const { brand: serverBrand, estimatedValue, dealMetrics, marketInsights } = data

		const mileagePenalty = marketInsights?.mileageImpact || "calculating..."

		result.innerHTML = `
            <h4> The average marketplace value for a ${year} ${serverBrand} is <strong> ${marketInsights.averagePriceForYear}</strong>, 
            but your specific unit is valued at <strong> ${estimatedValue} </strong> 
            due to an accumulated mileage penalty of ${marketInsights.mileageImpact}. And its depreciation rate is ${marketInsights.depreciationRate}.</h4>
            <h3> Overall: <span class='${dealMetrics.status}'>${dealMetrics.label}</span> </h3>
		`
		loadMarketChart(brand, year, mileage, transmission, condition)
    } catch (error) {
        console.error('Fetch operation error:', error)
        result.innerHTML = `<span style="color: red"><strong>Error:</strong> Could not reach backend server. Did you start server.js in your terminal?</span>`
    }
})

async function loadMarketChart(brand, condition, year, mileage, transmission) {
    const TRENDS_URL = 'https://autoval-test.onrender.com/market-trends'; // Temporary js backend ko ulit, papalitan to.

    try {
        const response = await fetch(TRENDS_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ brand, year, mileage, transmission, condition })
        });
        
        const data = await response.json();
        
        if (myChart) {
            myChart.data.labels = data.mileageLabels;
            myChart.data.datasets[0].data = data.depreciationPrices;
            myChart.update();
        }

    } catch (error) {
        console.error('Failed to load chart metrics:', error);
    }
}