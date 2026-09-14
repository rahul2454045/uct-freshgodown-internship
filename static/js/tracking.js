// Live Order Tracking & Geolocation Simulation JS

let map = null;
let godownMarker = null;
let customerMarker = null;
let driverMarker = null;
let routePolyline = null;
let pollInterval = null;

document.addEventListener("DOMContentLoaded", () => {
    initTracking();
});

async function initTracking() {
    const orderNumEl = document.getElementById("orderNumberVal");
    if (!orderNumEl) return;
    const orderNumber = orderNumEl.innerText.trim();

    await fetchTrackingData(orderNumber, true);

    // Poll every 5 seconds for simulated live driver movement
    pollInterval = setInterval(() => {
        fetchTrackingData(orderNumber, false);
    }, 5000);
}

async function fetchTrackingData(orderNumber, isFirstLoad = false) {
    try {
        const res = await fetch(`/api/orders/${orderNumber}/tracking`);
        if (!res.ok) throw new Error("Order tracking details not found");
        const data = await res.json();
        
        updateTrackingUI(data);

        if (isFirstLoad) {
            setupLeafletMap(data);
        } else {
            updateDriverPositionOnMap(data);
        }

        if (data.status === "DELIVERED") {
            clearInterval(pollInterval);
        }
    } catch (err) {
        console.error("Tracking error:", err);
    }
}

function updateTrackingUI(data) {
    // Status Badge
    const statusBadge = document.getElementById("orderStatusBadge");
    if (statusBadge) {
        statusBadge.innerText = data.status.replace(/_/g, " ");
        if (data.status === "DELIVERED") {
            statusBadge.className = "px-3 py-1 bg-emerald-100 text-emerald-800 font-bold rounded-full text-xs uppercase tracking-wider";
        } else if (data.status === "OUT_FOR_DELIVERY") {
            statusBadge.className = "px-3 py-1 bg-amber-100 text-amber-800 font-bold rounded-full text-xs uppercase tracking-wider animate-pulse";
        } else {
            statusBadge.className = "px-3 py-1 bg-blue-100 text-blue-800 font-bold rounded-full text-xs uppercase tracking-wider";
        }
    }

    // Dynamic ETA
    const etaVal = document.getElementById("etaMinutesVal");
    if (etaVal) {
        etaVal.innerText = data.status === "DELIVERED" ? "Delivered!" : `${data.eta_minutes} mins`;
    }

    // Progress Bar
    const progressEl = document.getElementById("progressPercentage");
    if (progressEl) {
        progressEl.style.width = `${data.progress_percent}%`;
    }

    // Driver info
    const driverName = document.getElementById("driverName");
    const driverPhone = document.getElementById("driverPhone");
    const driverVehicle = document.getElementById("driverVehicle");
    if (driverName) driverName.innerText = data.driver.name;
    if (driverPhone) driverPhone.innerText = data.driver.phone;
    if (driverVehicle) driverVehicle.innerText = data.driver.vehicle;

    // Delivery Slot & Address
    const slotInfo = document.getElementById("trackSlotInfo");
    const addressInfo = document.getElementById("trackAddress");
    if (slotInfo) slotInfo.innerText = `${data.slot_date} (${data.slot_window})`;
    if (addressInfo) addressInfo.innerText = `${data.customer.address}, ${data.customer.city}`;

    // Milestones Stepper
    renderMilestones(data.milestones);
}

function renderMilestones(milestones) {
    const list = document.getElementById("milestonesList");
    if (!list) return;

    let html = "";
    milestones.forEach((m, idx) => {
        const isDone = m.completed;
        const isActive = m.active;
        const isLast = idx === milestones.length - 1;

        html += `
            <div class="flex items-start gap-4 relative">
                ${!isLast ? `
                    <div class="absolute left-4 top-8 w-0.5 h-12 ${isDone ? 'bg-emerald-500' : 'bg-slate-200'}"></div>
                ` : ''}

                <div class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold shrink-0 z-10 ${
                    isDone ? 'bg-emerald-600 text-white ring-4 ring-emerald-100' :
                    isActive ? 'bg-amber-500 text-white ring-4 ring-amber-100 animate-pulse' :
                    'bg-slate-200 text-slate-500'
                }">
                    ${isDone ? '✓' : (idx + 1)}
                </div>

                <div class="pb-6">
                    <h4 class="font-bold text-sm ${isActive ? 'text-amber-700' : isDone ? 'text-slate-900' : 'text-slate-400'}">
                        ${m.title}
                    </h4>
                    <p class="text-xs text-slate-500 mt-0.5">${m.description}</p>
                </div>
            </div>
        `;
    });

    list.innerHTML = html;
}

function setupLeafletMap(data) {
    const mapContainer = document.getElementById("trackingMap");
    if (!mapContainer || typeof L === "undefined") return;

    const godownCoord = [data.godown.lat, data.godown.lng];
    const custCoord = [data.customer.lat, data.customer.lng];
    const driverCoord = [data.driver.lat, data.driver.lng];

    // Initialize map
    map = L.map('trackingMap').setView(driverCoord, 13);

    // OpenStreetMap tile layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    // Custom Icon Creators
    const createCustomIcon = (emoji, bgColor) => L.divIcon({
        className: 'custom-map-icon',
        html: `<div style="background-color: ${bgColor}; width: 36px; height: 36px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 18px; box-shadow: 0 4px 10px rgba(0,0,0,0.25); border: 2px solid white;">${emoji}</div>`,
        iconSize: [36, 36],
        iconAnchor: [18, 18]
    });

    // 1. Godown Marker
    godownMarker = L.marker(godownCoord, {
        icon: createCustomIcon('🏬', '#1e293b')
    }).addTo(map).bindPopup(`<b>${data.godown.name}</b><br>Central Storage Hub`);

    // 2. Customer Destination Marker
    customerMarker = L.marker(custCoord, {
        icon: createCustomIcon('🏠', '#10b981')
    }).addTo(map).bindPopup(`<b>Delivery Destination</b><br>${data.customer.address}`);

    // 3. Driver Marker
    driverMarker = L.marker(driverCoord, {
        icon: createCustomIcon('🚚', '#f59e0b')
    }).addTo(map).bindPopup(`<b>${data.driver.name}</b><br>${data.driver.vehicle}`);

    // Polyline Route from Godown to Customer
    routePolyline = L.polyline([godownCoord, driverCoord, custCoord], {
        color: '#10b981',
        weight: 4,
        dashArray: '8, 8',
        opacity: 0.75
    }).addTo(map);

    // Fit bounds to fit both endpoints comfortably
    const group = new L.featureGroup([godownMarker, customerMarker, driverMarker]);
    map.fitBounds(group.getBounds().pad(0.2));
}

function updateDriverPositionOnMap(data) {
    if (!driverMarker || !map) return;
    const newPos = [data.driver.lat, data.driver.lng];
    driverMarker.setLatLng(newPos);

    // Update polyline route
    if (routePolyline) {
        const godownCoord = [data.godown.lat, data.godown.lng];
        const custCoord = [data.customer.lat, data.customer.lng];
        routePolyline.setLatLngs([godownCoord, newPos, custCoord]);
    }
}
