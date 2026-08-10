// 1. ENVIRONMENT & BACKEND ROUTING SETUP ===============================================================================================

// Automatically selects the backend URL depending on whether the frontend is running locally or live in production
const BACKEND_URL = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
    ? 'http://127.0.0.1:8000'
    : 'https://autoval-8cs7.onrender.com'


// 2. THEME / COLOR TOGGLING LOGIC ======================================================================================================

// Define available visual themes for the application interface
const themes = ['dark', 'dark-soft', 'light', 'midnight']

let currentThemeIndex = themes.indexOf(document.documentElement.getAttribute('data-theme'))
if (currentThemeIndex === -1) currentThemeIndex = 0

const colorToggle = document.getElementById('color-toggle')
colorToggle?.addEventListener('click', () => {
    currentThemeIndex = (currentThemeIndex + 1) % themes.length
    const nextTheme = themes[currentThemeIndex]
    
    // Changing data-theme on <html> triggers the MutationObserver below
    document.documentElement.setAttribute('data-theme', nextTheme)
    localStorage.setItem('user-theme', nextTheme)
})

// 3. CHART INITIALIZATION & MANAGEMENT =================================================================================================

let myChart = null
let neonChart = null

// Helper function to extract current CSS variable theme colors for charts
function getThemeColors() {
    // Read from document.documentElement (html root) where data-theme is set
    const style = getComputedStyle(document.documentElement)
    return {
        fgMuted: style.getPropertyValue('--fg-muted').trim() || '#94a3b8',
        border: style.getPropertyValue('--border').trim() || '#334155',
        chart1: style.getPropertyValue('--chart-1').trim() || '#3b82f6',
        chart2: style.getPropertyValue('--chart-2').trim() || '#10b981'
    }
}

// Function to instantiate canvas charts with default structures
function initCharts() {
    const colors = getThemeColors()

    // 1. Depreciation Line Chart Initialization
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
                        title: { display: true, text: 'Estimated Value (PHP)', color: colors.fgMuted },
                        ticks: { 
                            color: colors.fgMuted,
                            callback: value => '₱' + value.toLocaleString()
                        },
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

    // 2. Neon DB Historical Bar Chart Initialization
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
                    hoverBackgroundColor: `${colors.chart2}66`,
                    hoverBorderColor: colors.chart2,
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

// Helper function to dynamically synchronize all existing chart colors with active CSS variables
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
                
            chart.data.datasets[0].hoverBorderColor = accentColor
            chart.data.datasets[0].hoverBackgroundColor = chart.config.type === 'line'
                ? `${accentColor}40`
                : `${accentColor}66`
        }
        chart.update('active')
    }

    refreshChart(myChart, colors.chart1)
    refreshChart(neonChart, colors.chart2)
}

// Observe attribute changes on <html> to re-render all chart themes immediately
const themeObserver = new MutationObserver(mutations => {
    mutations.forEach(m => {
        if (m.attributeName === 'data-theme') {
            updateChartColors()
        }
    })
})
themeObserver.observe(document.documentElement, { attributes: true })

// Call chart instantiation when script loads
initCharts()


// 4. DYNAMIC CAR MODEL SELECTION MAPPING ===============================================================================================

// Mapping object linking manufacturers to supported car model options
const carModelsByBrand = {
    toyota: ["camry", "corolla", "rav4", "tacoma", "highlander", "prius", "yaris", "4runner", "tundra", "sienna"],
    honda: ["civic", "accord", "cr-v", "pilot", "fit", "odyssey", "hr-v", "ridgeline", "passport"],
    ford: ["f-150", "mustang", "explorer", "escape", "focus", "fusion", "ranger", "bronco", "edge", "expedition"],
    chevrolet: ["silverado", "malibu", "equinox", "tahoe", "cruze", "camaro", "suburban", "colorado", "traverse", "corvette"],
    bmw: ["3 series", "5 series", "7 series", "x1", "x3", "x5", "x7", "m3", "m5", "i4", "iX"],
    nissan: ["altima", "sentra", "rogue", "murano", "pathfinder", "frontier", "maxima", "versa", "armada"],
    hyundai: ["elantra", "sonata", "tucson", "santa fe", "palisade", "kona", "ionic 5", "accent", "venue"],
    kia: ["forte", "optima", "k5", "sportage", "sorento", "telluride", "soul", "ev6", "seltos"],
    volkswagen: ["jetta", "passat", "golf", "tiguan", "atlas", "taos", "id.4", "gti"],
    mercedes: ["c-class", "e-class", "s-class", "glc", "gle", "gls", "a-class", "g-class", "eqs"],
    audi: ["a4", "a6", "q3", "q5", "q7", "q8", "e-tron", "r8", "a3"],
    subaru: ["outback", "forester", "impreza", "crosstrek", "legacy", "ascent", "wrx", "brz"],
    mazda: ["mazda3", "mazda6", "cx-5", "cx-30", "cx-50", "cx-90", "mx-5 miata"],
    lexus: ["rx", "es", "nx", "is", "gx", "lx", "ux", "tx"],
    tesla: ["model 3", "model y", "model s", "model x", "cybertruck"],
    jeep: ["wrangler", "grand cherokee", "cherokee", "compass", "gladiator", "renegade"],
    dodge: ["charger", "challenger", "durango", "hornet"],
    ram: ["1500", "2500", "3500", "promaster"],
    gmc: ["sierra", "acadia", "yukon", "terrain", "canyon"],
    volvo: ["xc60", "xc90", "xc40", "s60", "s90", "v60"],
    porsche: ["911", "cayenne", "macan", "taycan", "panamera", "718 boxster"],
    other: ["other"]
}
const brandSelect = document.getElementById("brand")
const modelSelect = document.getElementById("model")

// Function to populate model options based on current brandSelect value
function updateModelOptions() {
    const selectedBrand = brandSelect.value.toLowerCase()
    
    // If no brand is selected yet, reset to default state
    if (!selectedBrand) {
        modelSelect.innerHTML = '<option value="" disabled selected>Select a model</option>'
        return
    }

    const models = carModelsByBrand[selectedBrand] || ["other"]
    
    // Remember currently selected model (if browser restored it)
    const currentSelectedModel = modelSelect.value

    // Clear existing option elements
    modelSelect.innerHTML = '<option value="" disabled selected>Select a model</option>'
    
    // Append newly populated model options
    models.forEach(model => {
        const option = document.createElement("option")
        option.value = model
        
        // Format model strings with capitalized first letter
        const formattedName = model.charAt(0).toUpperCase() + model.slice(1)
        option.textContent = formattedName

        // If the browser previously selected this model on refresh, keep it selected
        if (model === currentSelectedModel) {
            option.selected = true
        }

        modelSelect.appendChild(option)
    })
}

// 1. Fire on user interaction
brandSelect.addEventListener("change", updateModelOptions)

// 2. Fire immediately on page load to catch browser restored values
document.addEventListener("DOMContentLoaded", updateModelOptions)
// Also run immediately in case DOM is already parsed when script runs
if (brandSelect.value) {
    updateModelOptions()
}

// 5. VALUATION FORM SUBMISSION & API HANDLER ===========================================================================================

const carForm = document.getElementById('carForm')
const result = document.getElementById('result')

// Utility helper to create an artificial delay for UX feel during async operations
const delay = (ms) => new Promise(resolve => setTimeout(resolve, ms))

// Main form submission listener for predicting vehicle prices
carForm.addEventListener('submit', async (e) => {
    e.preventDefault()
    
    // Collect required values from HTML form inputs
    const brand = document.getElementById('brand').value
    const model = document.getElementById('model').value
    const year = parseInt(document.getElementById('year').value)
    const mileage = parseInt(document.getElementById('mileage').value)
    const transmission = document.getElementById('transmission').value
    const condition = document.getElementById('condition').value

    // Collect optional advanced inputs (or fall back to 'Unknown')
    const fuel = document.getElementById('fuel')?.value || "Unknown"
    const title_status = document.getElementById('title_status')?.value || "Unknown"
    const drive = document.getElementById('drive')?.value || "Unknown"
    const type = document.getElementById('type')?.value || "Unknown"
    const size = document.getElementById('size')?.value || "Unknown"
    const cylinders = document.getElementById('cylinders')?.value || "Unknown"

    // Frontend validation logic for year and odometer input sanity checks
    const currentYear = new Date().getFullYear()
    if (year > currentYear) {
        result.innerHTML = `<em style='color: red;'>Year cannot exceed current year..</em>`
        return
    } else if (year < 1886) {
        result.innerHTML = `<em style='color: red;'>Year cannot be before 1886..</em>`
        return
    }
    if (isNaN(mileage) || mileage < 0) {
        result.innerHTML = `<em style='color: red;'>Please enter a valid mileage.</em>`
        return
    }

    // Construct data payload to match FastAPI backend expected schema
    const payload = {
        manufacturer: brand,
        model: model,
        year: parseInt(year),
        odometer: parseInt(mileage),
        transmission: transmission,
        condition: condition,
        
        // Optional advanced specs (passes selected option or 'Unknown' default)
        cylinders: cylinders,
        drive: drive,
        size: size,
        type: type,
        fuel: fuel,
        title_status: title_status
    }
    
    result.innerHTML = '<em>Connecting to server..</em>'

    await delay(450)

    try {
        // Send POST request to FastAPI backend predict route
        const response = await fetch(`${BACKEND_URL}/predict`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })

        if (!response.ok) throw new Error('Network response failed server-side')

        const data = await response.json()
        if (!data.success) {
            result.innerHTML = `<span style="color: orange"><strong>Engine Warning:</strong> ${data.message}</span>`
            return
        }

        // Extract prediction parameters returned by ML model
        const { brand: serverBrand, year: serverYear, estimatedValue, range, dealMetrics } = data

        // Render valuation results onto the page
        result.innerHTML = `
            <div class="result-header" style="margin-bottom: 12px;">
                <h2 style="font-size: 1.25rem; font-weight: 600; margin: 0; color: var(--fg-default);">
                    Valuation for ${serverYear} ${serverBrand}
                </h2>
            </div>
            <h3>Estimated Market Value: <strong>${estimatedValue}</strong></h3>
            <p style="margin-top: 4px; color: var(--fg-muted);">
                Typical Range: <strong>${range.min}</strong> – <strong>${range.max}</strong>
            </p>
            <h4>Overall: <span class="${dealMetrics.status}">${dealMetrics.label}</span></h4>
        `

        // Trigger loading and rendering of line chart depreciation trends
        loadMarketChart(payload)
    } catch (error) {
        console.error('Fetch operation error:', error)
        result.innerHTML = `<span style="color: red"><strong>Error:</strong> Could not reach backend server. Did you start app.py in your terminal?</span>`
    }
})

// 6. CHART DATA API FETCHING LOGIC =====================================================================================================

// Helper function called after prediction to fetch and plot market trend depreciation data
async function loadMarketChart(payload) {
    try {
        const response = await fetch(`${BACKEND_URL}/market-trends`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        
        const data = await response.json()
        
        // Update line chart datasets with returned array trends
        if (myChart) {
            myChart.data.labels = data.mileageLabels
            myChart.data.datasets[0].data = data.depreciationPrices
            myChart.update()
        }

    } catch (error) {
        console.error('Failed to load chart metrics:', error)
    }
}

// Function to fetch historical database record summary for the Neon DB bar chart
async function loadNeonDatabaseChart() {
    try {
        const response = await fetch(`${BACKEND_URL}/chart-data`)
        const result = await response.json()

        if (!result.success || !result.data || result.data.length === 0) {
            console.warn('No Neon DB data available')
            return
        }

        const rawData = result.data

        // Process Neon data: aggregate and calculate average price grouped by brand
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

        // Inject computed averages into the neon bar chart
        if (neonChart) {
            neonChart.data.labels = labels
            neonChart.data.datasets[0].data = avgPrices
            neonChart.update()
        }

    } catch (error) {
        console.error('Failed to load Neon DB chart:', error)
    }
}

// Automatically load Neon DB data once DOM components complete initial rendering
document.addEventListener('DOMContentLoaded', () => {
    loadNeonDatabaseChart()
})