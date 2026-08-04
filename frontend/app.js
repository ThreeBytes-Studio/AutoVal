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
let neonChart = null

function getThemeColors() {
    const style = getComputedStyle(document.body)
    return {
        fgMuted: style.getPropertyValue('--fg-muted').trim() || '#94a3b8',
        border: style.getPropertyValue('--border').trim() || '#334155',
        chart1: style.getPropertyValue('--chart-1').trim() || '#3b82f6',
        chart2: style.getPropertyValue('--chart-2').trim() || '#10b981'
    }
}

function initCharts() {
    const colors = getThemeColors()

    // 1. Existing Depreciation Chart
    const lineCtx = document.getElementById('depreciationChart')?.getContext('2d')
    if (lineCtx) {
        myChart = new Chart(lineCtx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Market Price vs. Mileage Depreciation Curve',
                    data: [],
                    borderColor: colors.chart1,
                    backgroundColor: `${colors.chart1}1A`,
                    borderWidth: 3,
                    tension: 0.3,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { labels: { color: colors.fgMuted } }
                },
                scales: {
                    y: { 
                        beginAtZero: false, 
                        title: { display: true, text: 'Estimated Value ($)', color: colors.fgMuted },
                        ticks: { color: colors.fgMuted },
                        grid: { color: colors.border }
                    },
                    x: { 
                        title: { display: true, text: 'Odometer Mileage Status', color: colors.fgMuted },
                        ticks: { color: colors.fgMuted },
                        grid: { color: colors.border }
                    }
                }
            }
        })
    }

    // 2. Neon DB Chart
    const neonCtx = document.getElementById('neonChart')?.getContext('2d')
    if (neonCtx) {
        neonChart = new Chart(neonCtx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Historical Listings Average Price (Neon DB)',
                    data: [],
                    backgroundColor: `${colors.chart2}33`,
                    borderColor: colors.chart2,
                    borderWidth: 2,
                    borderRadius: 6
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                plugins: {
                    legend: { labels: { color: colors.fgMuted } }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: { display: true, text: 'Price (PHP)', color: colors.fgMuted },
                        ticks: {
                            color: colors.fgMuted,
                            callback: value => '₱' + value.toLocaleString()
                        },
                        grid: { color: colors.border }
                    },
                    x: {
                        ticks: { color: colors.fgMuted },
                        grid: { color: colors.border }
                    }
                }
            }
        })
    }
}

// Dynamically refresh chart colors on theme switch
function updateChartColors() {
    const colors = getThemeColors()

    const refreshChart = (chart, accentColor) => {
        if (!chart) return
        chart.options.plugins.legend.labels.color = colors.fgMuted
        
        if (chart.options.scales.y) {
            chart.options.scales.y.ticks.color = colors.fgMuted
            chart.options.scales.y.grid.color = colors.border
            if (chart.options.scales.y.title) chart.options.scales.y.title.color = colors.fgMuted
        }
        if (chart.options.scales.x) {
            chart.options.scales.x.ticks.color = colors.fgMuted
            chart.options.scales.x.grid.color = colors.border
            if (chart.options.scales.x.title) chart.options.scales.x.title.color = colors.fgMuted
        }

        if (chart.data.datasets[0]) {
            chart.data.datasets[0].borderColor = accentColor
            chart.data.datasets[0].backgroundColor = chart.config.type === 'line' 
                ? `${accentColor}1A` 
                : `${accentColor}33`
        }
        chart.update()
    }

    refreshChart(myChart, colors.chart1)
    refreshChart(neonChart, colors.chart2)
}

// Observe attribute changes on <body> to re-render chart themes immediately when theme buttons are clicked
const themeObserver = new MutationObserver(mutations => {
    mutations.forEach(m => {
        if (m.attributeName === 'data-theme') {
            updateChartColors()
        }
    })
})
themeObserver.observe(document.body, { attributes: true })

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

async function loadNeonDatabaseChart() {
    try {
        const response = await fetch(`${BACKEND_URL}/chart-data`)
        const result = await response.json()

        if (!result.success || !result.data || result.data.length === 0) {
            console.warn('No Neon DB data available')
            return
        }

        const rawData = result.data

        // Process Neon data: calculate average price per brand
        const brandPrices = {}
        const brandCounts = {}

        rawData.forEach(car => {
            const brand = car.brand
            const price = car.price

            if (!brandPrices[brand]) {
                brandPrices[brand] = 0
                brandCounts[brand] = 0
            }
            brandPrices[brand] += price
            brandCounts[brand] += 1
        })

        const labels = Object.keys(brandPrices)
        const avgPrices = labels.map(b => Math.round(brandPrices[b] / brandCounts[b]))

        if (neonChart) {
            neonChart.data.labels = labels
            neonChart.data.datasets[0].data = avgPrices
            neonChart.update()
        }

    } catch (error) {
        console.error('Failed to load Neon DB chart:', error)
    }
}

// Automatically load Neon DB data when page mounts
document.addEventListener('DOMContentLoaded', () => {
    loadNeonDatabaseChart()
})