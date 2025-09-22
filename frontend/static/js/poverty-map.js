// Poverty Map JavaScript

let map = null;
let povertyLayer = null;

// Initialize map
function initializeMap() {
    // Initialize Leaflet map
    map = L.map('map').setView([40.7128, -74.0060], 10); // Default to NYC area

    // Add OpenStreetMap tiles
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // Load poverty data
    loadPovertyData();
}

// Load poverty data
async function loadPovertyData() {
    try {
        const data = await povertyMapAPI.getData();
        displayPovertyData(data);

    } catch (error) {
        showToast('Failed to load poverty data', 'error');
        console.error('Poverty data error:', error);
    }
}

// Display poverty data on map
function displayPovertyData(data) {
    if (povertyLayer) {
        map.removeLayer(povertyLayer);
    }

    const markers = [];
    const heatData = [];

    data.forEach(area => {
        // Create marker
        const marker = L.circleMarker([area.latitude, area.longitude], {
            radius: Math.max(5, Math.min(15, area.poverty_rate * 2)),
            fillColor: getPovertyColor(area.poverty_rate),
            color: '#fff',
            weight: 1,
            opacity: 1,
            fillOpacity: 0.7
        });

        // Add popup with area information
        marker.bindPopup(`
            <div class="p-2">
                <h6>${area.region}</h6>
                <p><strong>Poverty Rate:</strong> ${area.poverty_rate}%</p>
                <p><strong>Population:</strong> ${area.population.toLocaleString()}</p>
                <p><strong>Average Income:</strong> ${formatCurrency(area.average_income)}</p>
                <p><strong>Unemployment Rate:</strong> ${area.unemployment_rate}%</p>
                <button class="btn btn-sm btn-outline-primary" onclick="viewRegionDetails('${area.region}')">
                    View Details
                </button>
            </div>
        `);

        markers.push(marker);

        // Add to heat map data
        heatData.push([
            area.latitude,
            area.longitude,
            area.poverty_rate / 100 // Normalize for heat map
        ]);
    });

    // Create layer group
    povertyLayer = L.layerGroup(markers);
    povertyLayer.addTo(map);

    // Add heat map layer
    const heatLayer = L.heatLayer(heatData, {
        radius: 25,
        blur: 15,
        maxZoom: 17,
    });

    // Add layer control
    const overlays = {
        "Poverty Areas": povertyLayer,
        "Heat Map": heatLayer
    };

    L.control.layers(null, overlays).addTo(map);

    // Fit map to show all markers
    if (markers.length > 0) {
        const group = new L.featureGroup(markers);
        map.fitBounds(group.getBounds().pad(0.1));
    }
}

// Get color based on poverty rate
function getPovertyColor(rate) {
    if (rate >= 25) return '#d73027'; // High poverty - Red
    if (rate >= 15) return '#fdae61'; // Medium-high - Orange
    if (rate >= 10) return '#fee08b'; // Medium - Yellow
    if (rate >= 5) return '#d9ef8b';  // Low-medium - Light green
    return '#66bd63'; // Low poverty - Green
}

// View region details
async function viewRegionDetails(regionName) {
    try {
        const data = await povertyMapAPI.getRegion(regionName);

        if (data.error) {
            showToast('Region not found', 'error');
            return;
        }

        // Create detailed modal
        const modalHtml = `
            <div id="regionModal" class="modal" style="display: block;">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">${data.region}</h5>
                            <button type="button" class="btn-close" onclick="closeRegionModal()"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row">
                                <div class="col-md-6">
                                    <h6>Demographics</h6>
                                    <table class="table table-sm">
                                        <tr>
                                            <td><strong>Population:</strong></td>
                                            <td>${data.population.toLocaleString()}</td>
                                        </tr>
                                        <tr>
                                            <td><strong>Poverty Rate:</strong></td>
                                            <td>${data.poverty_rate}%</td>
                                        </tr>
                                        <tr>
                                            <td><strong>Average Income:</strong></td>
                                            <td>${formatCurrency(data.average_income)}</td>
                                        </tr>
                                        <tr>
                                            <td><strong>Unemployment Rate:</strong></td>
                                            <td>${data.unemployment_rate}%</td>
                                        </tr>
                                    </table>
                                </div>
                                <div class="col-md-6">
                                    <h6>Analysis</h6>
                                    <div class="alert alert-${getPovertyAlertClass(data.poverty_rate)}">
                                        <strong>Poverty Level: ${getPovertyLevel(data.poverty_rate)}</strong>
                                    </div>
                                    <p class="text-muted">
                                        This area ${data.poverty_rate >= 15 ? 'requires significant attention' : data.poverty_rate >= 10 ? 'needs support' : 'is relatively stable'} based on current poverty indicators.
                                    </p>
                                    <h6>Recommendations</h6>
                                    <ul class="list-unstyled">
                                        ${generateRecommendations(data).map(rec => `<li><i class="fas fa-check text-success me-2"></i>${rec}</li>`).join('')}
                                    </ul>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.body.insertAdjacentHTML('beforeend', modalHtml);

    } catch (error) {
        showToast('Failed to load region details', 'error');
        console.error('Region details error:', error);
    }
}

// Get poverty alert class
function getPovertyAlertClass(rate) {
    if (rate >= 25) return 'danger';
    if (rate >= 15) return 'warning';
    return 'info';
}

// Get poverty level description
function getPovertyLevel(rate) {
    if (rate >= 25) return 'Very High';
    if (rate >= 15) return 'High';
    if (rate >= 10) return 'Moderate';
    if (rate >= 5) return 'Low';
    return 'Very Low';
}

// Generate recommendations based on poverty data
function generateRecommendations(data) {
    const recommendations = [];

    if (data.poverty_rate >= 20) {
        recommendations.push('Implement immediate poverty alleviation programs');
        recommendations.push('Increase access to affordable housing');
        recommendations.push('Expand job training and employment programs');
    } else if (data.poverty_rate >= 15) {
        recommendations.push('Strengthen social support systems');
        recommendations.push('Improve access to healthcare and education');
        recommendations.push('Support local business development');
    } else if (data.poverty_rate >= 10) {
        recommendations.push('Monitor poverty trends closely');
        recommendations.push('Enhance community development initiatives');
        recommendations.push('Promote financial literacy programs');
    } else {
        recommendations.push('Maintain current support systems');
        recommendations.push('Focus on preventive measures');
        recommendations.push('Support community-led initiatives');
    }

    if (data.unemployment_rate >= 15) {
        recommendations.push('Create targeted employment programs');
    }

    if (data.average_income < 30000) {
        recommendations.push('Develop income enhancement strategies');
    }

    return recommendations.slice(0, 5);
}

// Close region modal
function closeRegionModal() {
    const modal = document.getElementById('regionModal');
    if (modal) {
        modal.remove();
    }
}

// Load poverty summary
async function loadPovertySummary() {
    try {
        const summary = await povertyMapAPI.getSummary();

        const container = document.querySelector('#povertyMapSection .card-body');

        const html = `
            <div class="row mb-4">
                <div class="col-md-3">
                    <div class="card bg-light">
                        <div class="card-body text-center">
                            <h6>Total Regions</h6>
                            <h3 class="text-primary">${summary.total_regions}</h3>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-light">
                        <div class="card-body text-center">
                            <h6>Average Poverty Rate</h6>
                            <h3 class="text-${summary.average_poverty_rate >= 15 ? 'danger' : summary.average_poverty_rate >= 10 ? 'warning' : 'success'}">
                                ${summary.average_poverty_rate.toFixed(1)}%
                            </h3>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-light">
                        <div class="card-body text-center">
                            <h6>Total Population</h6>
                            <h3 class="text-info">${summary.total_population.toLocaleString()}</h3>
                        </div>
                    </div>
                </div>
                <div class="col-md-3">
                    <div class="card bg-light">
                        <div class="card-body text-center">
                            <h6>Highest Poverty Area</h6>
                            <h5 class="text-danger">${summary.highest_poverty_region.region}</h5>
                            <small>${summary.highest_poverty_region.poverty_rate}%</small>
                        </div>
                    </div>
                </div>
            </div>
        `;

        container.insertAdjacentHTML('afterbegin', html);

    } catch (error) {
        console.error('Poverty summary error:', error);
    }
}
