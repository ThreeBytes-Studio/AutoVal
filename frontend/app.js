// Auto select backend url whether running locally or live.
const BACKEND_URL = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    ? 'http://127.0.0.1:8000'
    : 'https://autoval-8cs7.onrender.com'

// Color toggling
const themes = ['dark', 'dark-soft', 'light', 'midnight']
const savedTheme = localStorage.getItem('user-theme')
let currentThemeIndex = themes.includes(savedTheme) 
    ? themes.indexOf(savedTheme) 
    : (themes.indexOf(document.body.dataset.theme) === -1 ? 0 : themes.indexOf(document.body.dataset.theme))

document.body.dataset.theme = themes[currentThemeIndex]

const colorToggle = document.getElementById('color-toggle')
colorToggle.addEventListener('click', () => {
    currentThemeIndex = (currentThemeIndex + 1) % themes.length
    const nextTheme = themes[currentThemeIndex]
    
    document.body.dataset.theme = nextTheme

    localStorage.setItem('user-theme', nextTheme)
    
    const freshFgMuted = getComputedStyle(document.body).getPropertyValue('--fg-muted').trim()
    const freshBorder = getComputedStyle(document.body).getPropertyValue('--border').trim()
    const freshAccent = getComputedStyle(document.body).getPropertyValue('--chart-1').trim()

    if (myChart) {
        myChart.options.plugins.legend.labels.color = freshFgMuted
        
        myChart.options.scales.x.ticks.color = freshFgMuted
        myChart.options.scales.x.grid.color = freshBorder
        
        myChart.options.scales.y.ticks.color = freshFgMuted
        myChart.options.scales.y.grid.color = freshBorder

        myChart.data.datasets[0].borderColor = freshAccent
        myChart.data.datasets[0].backgroundColor = `${freshAccent}1A`
        
        myChart.update()
    }
})

// Initialize blank chart/s
let myChart = null
function initCharts() {
    const lineCtx = document.getElementById('depreciationChart').getContext('2d')
    
    const fgMuted = getComputedStyle(document.body).getPropertyValue('--fg-muted').trim()
    const border = getComputedStyle(document.body).getPropertyValue('--border').trim()
    const accent = getComputedStyle(document.body).getPropertyValue('--chart-1').trim()

    myChart = new Chart(lineCtx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Market Price vs. Mileage Depreciation Curve',
                data: [],
                borderColor: accent,
                backgroundColor: `${accent}1A`,
                borderWidth: 3,
                tension: 0.3,
                fill: true
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    labels: { color: fgMuted }
                }
            },
            scales: {
                y: { 
                    beginAtZero: false, 
                    title: { display: true, text: 'Estimated Value ($)', color: '#94a3b8' },
                    ticks: { color: fgMuted },
                    grid: { color: border }
                },
                x: { 
                    title: { display: true, text: 'Odometer Mileage Status', color: '#94a3b8' },
                    ticks: { color: fgMuted },
                    grid: { color: border }
                }
            }
        }
    })
}
initCharts()

// On submit button click
const carForm = document.getElementById('carForm')
const result = document.getElementById('result')
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

// Helper function on submit button click to load chart/s data.
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