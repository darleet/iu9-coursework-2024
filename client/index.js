const backendURL = 'http://localhost:8000';

let map = L.map('map').setView([55.7558, 37.6173], 13);  // Moscow's coordinates

// Add a tile layer to the map
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

// Initialize drawing control
let drawnItems = new L.FeatureGroup();
map.addLayer(drawnItems);

let drawControl = new L.Control.Draw({
    edit: {
        featureGroup: drawnItems
    },
    draw: {
        polygon: true,
        polyline: true,
        marker: true,
        circle: false,
        rectangle: false
    }
});
map.addControl(drawControl);

// Event listener for when the user draws a route
map.on('draw:created', function(e) {
    let layer = e.propagatedFrom;
    drawnItems.addLayer(layer);
});

// Event listener for submitting the route
document.getElementById('submit-route').onclick = async function() {
    let routeCoordinates = [];
    drawnItems.eachLayer(function(layer) {
        if (layer.getLatLngs) {
            // Loop through the points in the drawn route
            let latlngs = layer.getLatLngs();
            latlngs.forEach(function(latlng) {
                routeCoordinates.push([latlng.lat, latlng.lng]);
            });
        }
    });

    // Send route data to the FastAPI backend
    const response = await fetch(backendURL + '/route', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ coordinates: routeCoordinates })
    });

    const resp = await response.json();
    const data = resp.data;

    routeCoordinates.forEach((latlng, index) => {
        const iceProb = data.ice_probabilities[index].toFixed(2);
        const visibility = data.visibility_scores[index].toFixed(2);

        const popupContent = `
                <b>Coordinate:</b> (${latlng[0].toFixed(5)}, ${latlng[1].toFixed(5)})<br>
                <b>Ice Probability:</b> ${iceProb}%<br>
                <b>Visibility:</b> ${visibility}%
            `;

        // Display ice probabilities with slightly larger markers
        let color = getColor(iceProb);
        let offsetLatLng = [latlng[0] + 0.0001, latlng[1] + 0.0001];
        L.circleMarker(offsetLatLng, {
            radius: 10,
            fillColor: color,
            color: color,
            weight: 1,
            opacity: 1,
            fillOpacity: 0.7
        }).addTo(map).bindPopup(popupContent);

        // Display visibility scores with slightly smaller markers
        color = getColor(100 - visibility);
        offsetLatLng = [latlng[0] - 0.0001, latlng[1] - 0.0001];
        L.circleMarker(offsetLatLng, {
            radius: 6,
            fillColor: color,
            color: color,
            weight: 1,
            opacity: 1,
            fillOpacity: 0.7
        }).addTo(map).bindPopup(popupContent);
    });

    document.getElementById('result').innerHTML = `
                Route submitted with ice probabilities and visibility scores.
            `;
};

function getColor(value) {
    if (value <= 10) return '#00FF00';  // Very low (Green)
    if (value <= 20) return '#7FFF00';  // Low
    if (value <= 40) return '#FFFF00';  // Moderate (Yellow)
    if (value <= 60) return '#FFA500';  // High (Orange)
    if (value <= 80) return '#FF4500';  // Very high (Dark Orange)
    return '#FF0000';  // Extreme (Red)
}

// Adding a legend to the map
let legend = L.control({ position: 'bottomright' });

legend.onAdd = function() {
    let div = L.DomUtil.create('div', 'legend');
    div.innerHTML += "<h4>Legend</h4>";
    div.innerHTML += '<i style="background: #00FF00"></i> Very Low<br>';
    div.innerHTML += '<i style="background: #7FFF00"></i> Low<br>';
    div.innerHTML += '<i style="background: #FFFF00"></i> Moderate<br>';
    div.innerHTML += '<i style="background: #FFA500"></i> High<br>';
    div.innerHTML += '<i style="background: #FF4500"></i> Very High<br>';
    div.innerHTML += '<i style="background: #FF0000"></i> Extreme<br>';
    div.innerHTML += "<h4>Markers</h4>";
    div.innerHTML += '<div class="marker-item"><div style="width: 18px; height: 18px; background: grey; border-radius: 50%;"></div> Ice Formation (Larger)</div>';
    div.innerHTML += '<div class="marker-item"><div style="width: 10px; height: 10px; background: grey; border-radius: 50%;"></div> Visibility (Smaller)</div>';
    return div;
};

legend.addTo(map);
