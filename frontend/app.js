const BACKEND_URL = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    ? 'http://127.0.0.1:8000'
    : 'https://autoval-8cs7.onrender.com'

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
            plugins: {
                legend: {
                    labels: {
                        color: '#e2e8f0'
                    }
                }
            },
            scales: {
                y: { 
                    beginAtZero: false, 
                    title: { 
                        display: true, 
                        text: 'Estimated Value ($)',
                        color: '#94a3b8'
                    },
                    ticks: {
                        color: '#cbd5e1'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                x: { 
                    title: { 
                        display: true, 
                        text: 'Odometer Mileage Status',
                        color: '#94a3b8'
                    },
                    ticks: {
                        color: '#cbd5e1'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            }
        }
    })
}
initCharts()

const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms))
carForm.addEventListener('submit', async (e) => {
    e.preventDefault()
    const brand = document.getElementById('brand').value
    const year = document.getElementById('year').value
    const mileage = document.getElementById('mileage').value
    const transmission = document.getElementById('transmission').value
    const condition = document.getElementById('condition').value

    result.innerHTML = '<em>Connecting to server..</em>'

    await delay(450)

    try {
        const response = await fetch(`${BACKEND_URL}/predict`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({brand, year, mileage, transmission, condition})
        })

        if (!response.ok) throw new Error('Network response failed server-side')

		const data = await response.json()
		const { brand: serverBrand, estimatedValue, dealMetrics, marketInsights } = data

		const mileagePenalty = marketInsights?.mileageImpact || "calculating..."

		result.innerHTML = `
            <p> The average marketplace value for a ${year} ${serverBrand} is <strong> ${marketInsights.averagePriceForYear}</strong>, 
            but your specific unit is valued at <strong> ${estimatedValue} </strong> 
            due to an accumulated mileage penalty of ${marketInsights.mileageImpact}. And its depreciation rate is ${marketInsights.depreciationRate}.</p>
            <h3> Overall: <span class='${dealMetrics.status}'>${dealMetrics.label}</span> </h3>
		`
		loadMarketChart(brand, year, mileage, transmission, condition)
    } catch (error) {
        console.error('Fetch operation error:', error)
        result.innerHTML = `<span style="color: red"><strong>Error:</strong> Could not reach backend server. Did you start app.py in your terminal?</span>`
    }
})

async function loadMarketChart(brand, year, mileage, transmission, condition) {
    try {
        const response = await fetch(`${BACKEND_URL}/market-trends`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ brand, year, mileage, transmission, condition })
        })
        
        const data = await response.json()
        
        if (myChart) {
            myChart.data.labels = data.mileageLabels
            myChart.data.datasets[0].data = data.depreciationPrices
            myChart.update()
        }

    } catch (error) {
        console.error('Failed to load chart metrics:', error)
    }
}