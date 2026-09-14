// Godown Manager & Admin Portal JS

let adminInventory = [];
let adminOrders = [];

document.addEventListener("DOMContentLoaded", () => {
    initAdmin();
});

async function initAdmin() {
    await loadAdminStats();
    await loadInventory();
    await loadOrders();
    setupAdminSearch();
}

function setupAdminSearch() {
    const searchInput = document.getElementById("invSearchInput");
    if (searchInput) {
        searchInput.addEventListener("input", (e) => {
            const query = e.target.value.toLowerCase().trim();
            renderInventoryTable(query);
        });
    }
}

async function loadAdminStats() {
    try {
        const res = await fetch("/api/admin/stats");
        if (!res.ok) throw new Error("Failed to load admin stats");
        const stats = await res.json();

        document.getElementById("kpiRevenue").innerText = `$${stats.total_revenue.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
        document.getElementById("kpiOrders").innerText = stats.total_orders;
        document.getElementById("kpiPending").innerText = stats.pending_fulfillment;
        document.getElementById("kpiActiveDeliveries").innerText = stats.active_deliveries;
        document.getElementById("kpiLowStock").innerText = stats.low_stock_count;
        document.getElementById("kpiSlotOccupancy").innerText = `${stats.slot_utilization_percent}%`;
    } catch (err) {
        console.error("Admin stats error:", err);
    }
}

async function loadInventory() {
    try {
        const res = await fetch("/api/admin/inventory");
        if (!res.ok) throw new Error("Failed to load inventory");
        adminInventory = await res.json();
        renderInventoryTable();
    } catch (err) {
        console.error("Inventory error:", err);
    }
}

function renderInventoryTable(query = "") {
    const tbody = document.getElementById("inventoryTableBody");
    if (!tbody) return;

    const filtered = adminInventory.filter(p => 
        p.name.toLowerCase().includes(query) || 
        p.category.toLowerCase().includes(query)
    );

    if (filtered.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" class="text-center py-6 text-slate-400">No inventory products matched.</td></tr>`;
        return;
    }

    let html = "";
    filtered.forEach(item => {
        const isLow = item.stock_quantity <= item.low_stock_threshold;
        const isOut = item.stock_quantity <= 0;

        html += `
            <tr class="hover:bg-slate-50 transition-colors border-b border-slate-100">
                <td class="py-3.5 px-4 font-semibold text-slate-900 text-sm">
                    ${item.name}
                    <div class="text-xs text-slate-400 font-normal">Unit: ${item.unit}</div>
                </td>
                <td class="py-3.5 px-4 text-xs font-medium text-slate-600">
                    <span class="bg-slate-100 px-2.5 py-1 rounded-md">${item.category}</span>
                </td>
                <td class="py-3.5 px-4 text-sm font-bold text-slate-900">
                    $${item.price.toFixed(2)}
                    <span class="text-xs text-slate-400 line-through ml-1">$${item.mrp.toFixed(2)}</span>
                </td>
                <td class="py-3.5 px-4">
                    <div class="flex items-center gap-2">
                        <span class="text-sm font-extrabold ${isOut ? 'text-red-600' : isLow ? 'text-amber-600' : 'text-slate-800'}">
                            ${item.stock_quantity}
                        </span>
                        ${isOut ? `
                            <span class="bg-red-100 text-red-700 text-[10px] font-bold px-2 py-0.5 rounded">OUT OF STOCK</span>
                        ` : isLow ? `
                            <span class="bg-amber-100 text-amber-800 text-[10px] font-bold px-2 py-0.5 rounded">LOW STOCK</span>
                        ` : `
                            <span class="bg-emerald-100 text-emerald-800 text-[10px] font-semibold px-2 py-0.5 rounded">HEALTHY</span>
                        `}
                    </div>
                </td>
                <td class="py-3.5 px-4 text-xs text-slate-500">
                    Threshold: ${item.low_stock_threshold}
                </td>
                <td class="py-3.5 px-4 text-right">
                    <div class="flex items-center justify-end gap-2">
                        <button onclick="quickRestock(${item.id}, 50)" class="px-2.5 py-1 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 text-xs font-bold rounded-lg transition-colors border border-emerald-200">
                            +50 Quick Restock
                        </button>
                        <button onclick="promptCustomRestock(${item.id}, '${item.name.replace(/'/g, "\\'")}')" class="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-medium rounded-lg transition-colors">
                            Custom...
                        </button>
                    </div>
                </td>
            </tr>
        `;
    });

    tbody.innerHTML = html;
}

async function quickRestock(productId, amount) {
    try {
        const res = await fetch(`/api/admin/inventory/${productId}/restock?add_quantity=${amount}`, {
            method: "POST"
        });
        if (!res.ok) throw new Error("Failed to restock");
        const data = await res.json();
        adminToast(data.message, "success");
        await loadInventory();
        await loadAdminStats();
    } catch (err) {
        adminToast(err.message, "error");
    }
}

function promptCustomRestock(productId, productName) {
    const qtyStr = prompt(`Enter quantity to add to Godown inventory for:\n"${productName}":`, "100");
    if (!qtyStr) return;
    const qty = parseInt(qtyStr, 10);
    if (isNaN(qty) || qty <= 0) {
        alert("Please enter a valid positive number.");
        return;
    }
    quickRestock(productId, qty);
}

async function loadOrders() {
    try {
        const res = await fetch("/api/admin/orders");
        if (!res.ok) throw new Error("Failed to load orders");
        adminOrders = await res.json();
        renderOrdersTable();
    } catch (err) {
        console.error("Orders load error:", err);
    }
}

function renderOrdersTable() {
    const tbody = document.getElementById("ordersTableBody");
    if (!tbody) return;

    if (adminOrders.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" class="text-center py-6 text-slate-400">No orders placed yet.</td></tr>`;
        return;
    }

    let html = "";
    adminOrders.forEach(ord => {
        const statusColors = {
            PLACED: "bg-blue-50 text-blue-700 border-blue-200",
            PICKED_FROM_GODOWN: "bg-indigo-50 text-indigo-700 border-indigo-200",
            PACKED: "bg-purple-50 text-purple-700 border-purple-200",
            OUT_FOR_DELIVERY: "bg-amber-50 text-amber-800 border-amber-200 animate-pulse",
            DELIVERED: "bg-emerald-50 text-emerald-800 border-emerald-200"
        };

        html += `
            <tr class="hover:bg-slate-50 transition-colors border-b border-slate-100">
                <td class="py-3.5 px-4 font-bold text-slate-900 text-xs">
                    <a href="/track/${ord.order_number}" target="_blank" class="text-emerald-700 hover:underline flex items-center gap-1">
                        ${ord.order_number}
                        <span>↗</span>
                    </a>
                </td>
                <td class="py-3.5 px-4">
                    <div class="font-semibold text-slate-900 text-xs">${ord.customer_name}</div>
                    <div class="text-[11px] text-slate-500">${ord.customer_phone}</div>
                </td>
                <td class="py-3.5 px-4 text-xs text-slate-600">
                    <div class="font-medium">${ord.slot_date}</div>
                    <div class="text-[11px] text-slate-400">${ord.slot_window}</div>
                </td>
                <td class="py-3.5 px-4 text-xs font-bold text-slate-900">
                    $${ord.total_amount.toFixed(2)}
                    <div class="text-[10px] font-normal text-emerald-600">${ord.payment_method} (${ord.payment_status})</div>
                </td>
                <td class="py-3.5 px-4 text-xs text-slate-600">
                    ${ord.items.length} items
                </td>
                <td class="py-3.5 px-4">
                    <span class="px-2.5 py-1 rounded-full text-[11px] font-bold border ${statusColors[ord.order_status] || 'bg-slate-100 text-slate-700'}">
                        ${ord.order_status.replace(/_/g, ' ')}
                    </span>
                </td>
                <td class="py-3.5 px-4 text-right">
                    <select onchange="updateFulfillmentStatus(${ord.id}, this.value)" class="text-xs bg-white border border-slate-300 rounded-lg px-2 py-1 font-medium text-slate-700 focus:ring-1 focus:ring-emerald-500 outline-none">
                        <option value="">Update Status...</option>
                        <option value="PLACED" ${ord.order_status === 'PLACED' ? 'disabled' : ''}>1. PLACED</option>
                        <option value="PICKED_FROM_GODOWN" ${ord.order_status === 'PICKED_FROM_GODOWN' ? 'disabled' : ''}>2. PICKED FROM GODOWN</option>
                        <option value="PACKED" ${ord.order_status === 'PACKED' ? 'disabled' : ''}>3. PACKED</option>
                        <option value="OUT_FOR_DELIVERY" ${ord.order_status === 'OUT_FOR_DELIVERY' ? 'disabled' : ''}>4. OUT FOR DELIVERY</option>
                        <option value="DELIVERED" ${ord.order_status === 'DELIVERED' ? 'disabled' : ''}>5. DELIVERED</option>
                    </select>
                </td>
            </tr>
        `;
    });

    tbody.innerHTML = html;
}

async function updateFulfillmentStatus(orderId, newStatus) {
    if (!newStatus) return;

    try {
        const res = await fetch(`/api/admin/orders/${orderId}/status`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ order_status: newStatus })
        });
        if (!res.ok) throw new Error("Failed to update status");
        const updated = await res.json();
        adminToast(`Order ${updated.order_number} advanced to ${newStatus.replace(/_/g, ' ')}!`, "success");
        await loadOrders();
        await loadAdminStats();
    } catch (err) {
        adminToast(err.message, "error");
    }
}

function adminToast(msg, type = "info") {
    const container = document.getElementById("adminToastContainer");
    if (!container) return;
    const toast = document.createElement("div");
    toast.className = `px-4 py-2.5 rounded-xl shadow-md text-xs font-semibold text-white ${type === 'success' ? 'bg-emerald-800' : 'bg-red-800'}`;
    toast.innerText = msg;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}
