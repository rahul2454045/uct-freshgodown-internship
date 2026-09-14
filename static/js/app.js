// FreshGodown App Core JS

let currentProducts = [];
let currentCategories = [];
let activeCategory = null;
let activeSort = "popular";
let inStockOnly = false;
let searchQuery = "";

// Cart State (stored in localStorage)
let cart = JSON.parse(localStorage.getItem("freshgodown_cart") || "[]");
let appliedCoupon = localStorage.getItem("freshgodown_coupon") || null;
let selectedSlot = null;

const MIN_FREE_DELIVERY = 35.0;
const STANDARD_DELIVERY = 4.5;
const TAX_RATE = 0.05;

// Initialization
document.addEventListener("DOMContentLoaded", () => {
    initApp();
});

async function initApp() {
    updateCartUI();
    await loadCategories();
    await loadProducts();
    setupEventListeners();
}

function setupEventListeners() {
    const searchInput = document.getElementById("searchInput");
    if (searchInput) {
        let debounceTimer;
        searchInput.addEventListener("input", (e) => {
            clearTimeout(debounceTimer);
            debounceTimer = setTimeout(() => {
                searchQuery = e.target.value.trim();
                loadProducts();
            }, 300);
        });
    }

    const sortSelect = document.getElementById("sortSelect");
    if (sortSelect) {
        sortSelect.addEventListener("change", (e) => {
            activeSort = e.target.value;
            loadProducts();
        });
    }

    const inStockToggle = document.getElementById("inStockToggle");
    if (inStockToggle) {
        inStockToggle.addEventListener("change", (e) => {
            inStockOnly = e.target.checked;
            loadProducts();
        });
    }
}

// ================= API FETCHING =================
async function loadCategories() {
    try {
        const res = await fetch("/api/categories");
        if (!res.ok) throw new Error("Failed to load categories");
        currentCategories = await res.json();
        renderCategoryPills();
    } catch (err) {
        console.error("Categories load error:", err);
    }
}

function renderCategoryPills() {
    const container = document.getElementById("categoryPillsContainer");
    if (!container) return;

    let html = `
        <button onclick="selectCategory(null)" 
            class="px-4 py-2 rounded-full text-sm font-medium transition-all ${
                activeCategory === null 
                ? 'bg-emerald-600 text-white shadow-md shadow-emerald-200' 
                : 'bg-white text-slate-700 hover:bg-slate-100 border border-slate-200'
            }">
            🌟 All Department Goods
        </button>
    `;

    currentCategories.forEach(cat => {
        const isSelected = activeCategory === cat.id;
        html += `
            <button onclick="selectCategory(${cat.id})" 
                class="px-4 py-2 rounded-full text-sm font-medium transition-all flex items-center gap-2 whitespace-nowrap ${
                    isSelected 
                    ? 'bg-emerald-600 text-white shadow-md shadow-emerald-200' 
                    : 'bg-white text-slate-700 hover:bg-slate-100 border border-slate-200'
                }">
                <span>${cat.name}</span>
                <span class="text-xs ${isSelected ? 'bg-emerald-700 text-emerald-100' : 'bg-slate-100 text-slate-600'} px-2 py-0.5 rounded-full">${cat.product_count}</span>
            </button>
        `;
    });

    container.innerHTML = html;
}

function selectCategory(catId) {
    activeCategory = catId;
    renderCategoryPills();
    loadProducts();
}

async function loadProducts() {
    const grid = document.getElementById("productsGrid");
    if (!grid) return;

    grid.innerHTML = `
        <div class="col-span-full py-16 flex flex-col items-center justify-center text-slate-400">
            <svg class="animate-spin h-8 w-8 text-emerald-600 mb-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <p>Loading Godown Fresh Inventory...</p>
        </div>
    `;

    try {
        let url = `/api/products?sort_by=${activeSort}&in_stock_only=${inStockOnly}`;
        if (activeCategory) url += `&category_id=${activeCategory}`;
        if (searchQuery) url += `&search=${encodeURIComponent(searchQuery)}`;

        const res = await fetch(url);
        if (!res.ok) throw new Error("Failed to fetch products");
        currentProducts = await res.json();
        renderProducts();
    } catch (err) {
        console.error("Products error:", err);
        grid.innerHTML = `<div class="col-span-full text-center py-12 text-red-500">Failed to load items. Please refresh.</div>`;
    }
}

function renderProducts() {
    const grid = document.getElementById("productsGrid");
    const countEl = document.getElementById("productsCount");
    if (countEl) countEl.innerText = `${currentProducts.length} items available in godown`;

    if (currentProducts.length === 0) {
        grid.innerHTML = `
            <div class="col-span-full py-16 text-center">
                <div class="inline-flex items-center justify-center w-16 h-16 rounded-full bg-amber-50 text-amber-500 mb-4">
                    🔍
                </div>
                <h3 class="text-lg font-semibold text-slate-800 mb-1">No grocery items found</h3>
                <p class="text-slate-500 text-sm">Try clearing your search or switching to another category.</p>
                <button onclick="clearFilters()" class="mt-4 px-4 py-2 bg-emerald-600 text-white text-sm rounded-lg hover:bg-emerald-700">Clear Filters</button>
            </div>
        `;
        return;
    }

    let html = "";
    currentProducts.forEach(product => {
        const cartItem = cart.find(item => item.product_id === product.id);
        const cartQty = cartItem ? cartItem.quantity : 0;
        const isOutOfStock = product.stock_quantity <= 0;
        const discountPercent = Math.round(((product.mrp - product.price) / product.mrp) * 100);

        html += `
            <div class="product-card bg-white rounded-2xl border border-slate-200 overflow-hidden flex flex-col justify-between relative group">
                ${product.badge ? `
                    <div class="absolute top-3 left-3 z-10">
                        <span class="px-2.5 py-1 bg-emerald-600/90 backdrop-blur-md text-white text-xs font-semibold rounded-md shadow-sm">
                            ${product.badge}
                        </span>
                    </div>
                ` : ''}

                ${product.stock_quantity <= product.low_stock_threshold && product.stock_quantity > 0 ? `
                    <div class="absolute top-3 right-3 z-10">
                        <span class="px-2 py-0.5 bg-amber-500 text-white text-[11px] font-bold rounded-md shadow-sm pulse-badge">
                            Only ${product.stock_quantity} left in godown!
                        </span>
                    </div>
                ` : ''}

                <div class="relative overflow-hidden aspect-video bg-slate-100">
                    <img src="${product.image_url || 'https://images.unsplash.com/photo-1542838132-92c53300491e?w=500'}" 
                         alt="${product.name}" 
                         class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                         loading="lazy">
                </div>

                <div class="p-5 flex-1 flex flex-col justify-between">
                    <div>
                        <div class="flex items-center justify-between text-xs text-slate-500 mb-1.5">
                            <span class="font-medium text-emerald-700 uppercase tracking-wider">${product.category_name || 'Grocery'}</span>
                            <span class="flex items-center gap-1 font-semibold text-amber-500">
                                ★ ${product.rating} <span class="text-slate-400 font-normal">(${product.review_count})</span>
                            </span>
                        </div>

                        <h3 class="font-semibold text-slate-900 text-base line-clamp-1 mb-1" title="${product.name}">
                            ${product.name}
                        </h3>
                        <p class="text-xs text-slate-500 line-clamp-2 mb-3">
                            ${product.description}
                        </p>
                        <div class="text-xs font-medium text-slate-600 bg-slate-100 inline-block px-2.5 py-1 rounded-md mb-4">
                            ⚖️ Unit: ${product.unit}
                        </div>
                    </div>

                    <div>
                        <div class="flex items-baseline gap-2 mb-4">
                            <span class="text-xl font-bold text-slate-900">$${product.price.toFixed(2)}</span>
                            ${product.mrp > product.price ? `
                                <span class="text-xs text-slate-400 line-through">$${product.mrp.toFixed(2)}</span>
                                <span class="text-xs font-bold text-emerald-600 bg-emerald-50 px-1.5 py-0.5 rounded">${discountPercent}% OFF</span>
                            ` : ''}
                        </div>

                        ${isOutOfStock ? `
                            <button disabled class="w-full py-2.5 bg-slate-200 text-slate-400 font-medium text-sm rounded-xl cursor-not-allowed">
                                Out of Stock at Godown
                            </button>
                        ` : cartQty === 0 ? `
                            <button onclick="addToCart(${product.id})" class="w-full py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white font-medium text-sm rounded-xl flex items-center justify-center gap-2 shadow-sm shadow-emerald-200 transition-colors">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
                                Add to Cart
                            </button>
                        ` : `
                            <div class="flex items-center justify-between border-2 border-emerald-600 rounded-xl bg-emerald-50/50 p-1">
                                <button onclick="changeCartQty(${product.id}, -1)" class="w-8 h-8 rounded-lg bg-white shadow-sm flex items-center justify-center text-emerald-700 font-bold hover:bg-emerald-600 hover:text-white transition-colors">
                                    -
                                </button>
                                <span class="font-bold text-slate-900 text-sm px-2">${cartQty} in cart</span>
                                <button onclick="changeCartQty(${product.id}, 1)" class="w-8 h-8 rounded-lg bg-white shadow-sm flex items-center justify-center text-emerald-700 font-bold hover:bg-emerald-600 hover:text-white transition-colors">
                                    +
                                </button>
                            </div>
                        `}
                    </div>
                </div>
            </div>
        `;
    });

    grid.innerHTML = html;
}

function clearFilters() {
    activeCategory = null;
    searchQuery = "";
    const sInput = document.getElementById("searchInput");
    if (sInput) sInput.value = "";
    renderCategoryPills();
    loadProducts();
}


// ================= CART OPERATIONS =================
function addToCart(productId) {
    const prod = currentProducts.find(p => p.id === productId);
    if (!prod) return;

    const existing = cart.find(item => item.product_id === productId);
    if (existing) {
        if (existing.quantity >= prod.stock_quantity) {
            showToast(`Maximum godown stock reached for ${prod.name}`, "warning");
            return;
        }
        existing.quantity += 1;
    } else {
        cart.push({
            product_id: prod.id,
            name: prod.name,
            unit: prod.unit,
            price: prod.price,
            image_url: prod.image_url,
            max_stock: prod.stock_quantity,
            quantity: 1
        });
    }

    saveCart();
    renderProducts();
    updateCartUI();
    showToast(`Added ${prod.name} to cart!`, "success");
}

function changeCartQty(productId, delta) {
    const itemIndex = cart.findIndex(item => item.product_id === productId);
    if (itemIndex === -1) return;

    const item = cart[itemIndex];
    const newQty = item.quantity + delta;

    if (newQty <= 0) {
        cart.splice(itemIndex, 1);
        showToast(`Removed from cart`, "info");
    } else {
        if (newQty > item.max_stock) {
            showToast(`Only ${item.max_stock} available in godown`, "warning");
            return;
        }
        item.quantity = newQty;
    }

    saveCart();
    renderProducts();
    updateCartUI();
}

function saveCart() {
    localStorage.setItem("freshgodown_cart", JSON.stringify(cart));
}

function getCartCalculations() {
    let subtotal = 0;
    cart.forEach(item => {
        subtotal += item.price * item.quantity;
    });
    subtotal = Math.round(subtotal * 100) / 100;

    let discount = 0;
    if (appliedCoupon === "UCTNEW") {
        discount = Math.round(subtotal * 0.15 * 100) / 100; // 15%
    } else if (appliedCoupon === "FRESH50") {
        discount = Math.round(Math.min(subtotal * 0.10, 50.0) * 100) / 100; // 10%
    }

    const discountedSubtotal = Math.max(0, subtotal - discount);
    const deliveryFee = discountedSubtotal >= MIN_FREE_DELIVERY || cart.length === 0 ? 0.0 : STANDARD_DELIVERY;
    const tax = Math.round(discountedSubtotal * TAX_RATE * 100) / 100;
    const total = Math.round((discountedSubtotal + deliveryFee + tax) * 100) / 100;

    return {
        subtotal,
        discount,
        discountedSubtotal,
        deliveryFee,
        tax,
        total,
        freeDeliveryRemaining: Math.max(0, MIN_FREE_DELIVERY - discountedSubtotal)
    };
}

function updateCartUI() {
    const totalCount = cart.reduce((acc, item) => acc + item.quantity, 0);
    
    // Update badge counter
    const badges = document.querySelectorAll(".cart-count-badge");
    badges.forEach(b => {
        b.innerText = totalCount;
        b.classList.toggle("hidden", totalCount === 0);
    });

    const calc = getCartCalculations();

    // Update Drawer Elements
    const itemsList = document.getElementById("cartItemsList");
    const subtotalEl = document.getElementById("cartSubtotal");
    const discountEl = document.getElementById("cartDiscount");
    const deliveryEl = document.getElementById("cartDelivery");
    const taxEl = document.getElementById("cartTax");
    const totalEl = document.getElementById("cartTotal");
    const freeShippingNotice = document.getElementById("freeShippingNotice");
    const checkoutBtn = document.getElementById("openCheckoutBtn");

    if (subtotalEl) subtotalEl.innerText = `$${calc.subtotal.toFixed(2)}`;
    if (discountEl) discountEl.innerText = `-$${calc.discount.toFixed(2)}`;
    if (deliveryEl) deliveryEl.innerText = calc.deliveryFee === 0 ? "FREE" : `$${calc.deliveryFee.toFixed(2)}`;
    if (taxEl) taxEl.innerText = `$${calc.tax.toFixed(2)}`;
    if (totalEl) totalEl.innerText = `$${calc.total.toFixed(2)}`;

    if (freeShippingNotice) {
        if (calc.discountedSubtotal >= MIN_FREE_DELIVERY) {
            freeShippingNotice.innerHTML = `
                <div class="bg-emerald-50 text-emerald-800 text-xs px-3 py-2 rounded-lg flex items-center gap-1.5">
                    <span>🎉</span> <span class="font-medium">You unlocked FREE Godown Delivery!</span>
                </div>
            `;
        } else {
            freeShippingNotice.innerHTML = `
                <div class="bg-amber-50 text-amber-900 text-xs px-3 py-2 rounded-lg">
                    Add <span class="font-bold text-amber-800">$${calc.freeDeliveryRemaining.toFixed(2)}</span> more to qualify for <span class="font-bold text-emerald-700">FREE Delivery</span>!
                </div>
            `;
        }
    }

    if (checkoutBtn) {
        checkoutBtn.disabled = cart.length === 0;
    }

    if (itemsList) {
        if (cart.length === 0) {
            itemsList.innerHTML = `
                <div class="py-16 text-center text-slate-400">
                    <div class="text-4xl mb-3">🛒</div>
                    <p class="font-semibold text-slate-700">Your cart is empty</p>
                    <p class="text-xs text-slate-500 mt-1">Explore our departmental categories to add items.</p>
                </div>
            `;
            return;
        }

        let itemsHtml = "";
        cart.forEach(item => {
            itemsHtml += `
                <div class="flex items-center gap-3 p-3 bg-slate-50 rounded-xl border border-slate-100">
                    <img src="${item.image_url}" class="w-14 h-14 object-cover rounded-lg bg-white border border-slate-200">
                    <div class="flex-1 min-w-0">
                        <h4 class="font-semibold text-slate-900 text-xs truncate">${item.name}</h4>
                        <div class="text-[11px] text-slate-500">${item.unit}</div>
                        <div class="text-xs font-bold text-emerald-700 mt-0.5">$${item.price.toFixed(2)}</div>
                    </div>
                    <div class="flex items-center gap-1.5 bg-white border border-slate-200 rounded-lg p-1">
                        <button onclick="changeCartQty(${item.product_id}, -1)" class="w-6 h-6 flex items-center justify-center text-slate-600 hover:bg-slate-100 rounded text-xs font-bold">-</button>
                        <span class="text-xs font-bold text-slate-800 px-1">${item.quantity}</span>
                        <button onclick="changeCartQty(${item.product_id}, 1)" class="w-6 h-6 flex items-center justify-center text-slate-600 hover:bg-slate-100 rounded text-xs font-bold">+</button>
                    </div>
                </div>
            `;
        });
        itemsList.innerHTML = itemsHtml;
    }
}

function toggleCartDrawer() {
    const drawer = document.getElementById("cartDrawer");
    const overlay = document.getElementById("cartOverlay");
    if (!drawer || !overlay) return;

    const isOpen = !drawer.classList.contains("translate-x-full");
    if (isOpen) {
        drawer.classList.add("translate-x-full");
        overlay.classList.add("hidden");
    } else {
        drawer.classList.remove("translate-x-full");
        overlay.classList.remove("hidden");
    }
}

function applyCouponCode() {
    const input = document.getElementById("couponInput");
    if (!input) return;
    const code = input.value.trim().toUpperCase();
    if (code === "UCTNEW" || code === "FRESH50") {
        appliedCoupon = code;
        localStorage.setItem("freshgodown_coupon", code);
        updateCartUI();
        showToast(`Promo code '${code}' applied successfully!`, "success");
    } else {
        showToast("Invalid coupon code. Try 'UCTNEW' for 15% off.", "error");
    }
}


// ================= DELIVERY SLOT PICKER & CHECKOUT =================
let availableSlots = [];

async function openCheckoutFlow() {
    if (cart.length === 0) {
        showToast("Please add items to your cart first", "warning");
        return;
    }

    toggleCartDrawer(); // close drawer
    const modal = document.getElementById("checkoutModal");
    if (!modal) return;
    modal.classList.remove("hidden");

    // Load delivery slots
    await loadDeliverySlots();
}

function closeCheckoutModal() {
    const modal = document.getElementById("checkoutModal");
    if (modal) modal.classList.add("hidden");
}

async function loadDeliverySlots() {
    const container = document.getElementById("slotsContainer");
    if (!container) return;

    container.innerHTML = `<div class="p-4 text-center text-slate-400 text-sm">Loading delivery slots...</div>`;

    try {
        const res = await fetch("/api/slots");
        if (!res.ok) throw new Error("Could not load slots");
        availableSlots = await res.json();
        renderSlots();
    } catch (err) {
        container.innerHTML = `<div class="p-4 text-red-500 text-sm text-center">Failed to load delivery slots.</div>`;
    }
}

function renderSlots() {
    const container = document.getElementById("slotsContainer");
    if (!container || availableSlots.length === 0) return;

    // Group by slot_date
    const dates = [...new Set(availableSlots.map(s => s.slot_date))];

    let html = "";
    dates.forEach((dateStr, idx) => {
        const slotsForDate = availableSlots.filter(s => s.slot_date === dateStr);
        const dateObj = new Date(dateStr + "T00:00:00");
        const formattedDate = dateObj.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
        const isToday = idx === 0;

        html += `
            <div class="mb-4">
                <div class="text-xs font-bold text-slate-700 uppercase tracking-wider mb-2 flex items-center gap-2">
                    <span>📅 ${formattedDate}</span>
                    ${isToday ? '<span class="bg-emerald-100 text-emerald-800 text-[10px] px-2 py-0.5 rounded-full font-bold">TODAY</span>' : ''}
                </div>
                <div class="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                    ${slotsForDate.map(slot => {
                        const isSelected = selectedSlot && selectedSlot.id === slot.id;
                        const isFull = slot.is_full;

                        return `
                            <div onclick="${isFull ? '' : `chooseSlot(${slot.id})`}" 
                                 class="slot-card p-3 rounded-xl border text-left flex items-center justify-between ${
                                     isFull ? 'bg-slate-100 border-slate-200 opacity-60 cursor-not-allowed' :
                                     isSelected ? 'border-emerald-600 bg-emerald-50/70 shadow-sm ring-2 ring-emerald-600' :
                                     'border-slate-200 bg-white hover:border-emerald-400 hover:bg-emerald-50/20'
                                 }">
                                <div>
                                    <div class="font-semibold text-xs text-slate-900">${slot.time_window}</div>
                                    <div class="text-[11px] text-slate-500">${slot.slot_label}</div>
                                </div>
                                <div class="text-right">
                                    ${isFull ? `
                                        <span class="text-[10px] font-bold text-red-600 bg-red-50 px-2 py-0.5 rounded">FULL</span>
                                    ` : `
                                        <span class="text-[10px] font-medium text-emerald-700 bg-emerald-100/80 px-2 py-0.5 rounded">
                                            ${slot.available_spots} slots left
                                        </span>
                                    `}
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
        `;
    });

    container.innerHTML = html;

    // Auto-select first available slot if none selected
    if (!selectedSlot) {
        const firstAvailable = availableSlots.find(s => !s.is_full);
        if (firstAvailable) chooseSlot(firstAvailable.id);
    }
}

function chooseSlot(slotId) {
    selectedSlot = availableSlots.find(s => s.id === slotId);
    renderSlots();
}

// Payment method selection
let activePaymentMethod = "CARD";
function selectPaymentMethod(method) {
    activePaymentMethod = method;
    document.querySelectorAll(".pay-tab").forEach(tab => {
        tab.classList.remove("border-emerald-600", "bg-emerald-50", "text-emerald-800");
        tab.classList.add("border-slate-200", "text-slate-700");
    });
    const targetTab = document.getElementById(`payTab_${method}`);
    if (targetTab) {
        targetTab.classList.add("border-emerald-600", "bg-emerald-50", "text-emerald-800");
    }

    // Toggle forms
    document.getElementById("cardForm").classList.toggle("hidden", method !== "CARD");
    document.getElementById("upiForm").classList.toggle("hidden", method !== "UPI");
    document.getElementById("netbankingForm").classList.toggle("hidden", method !== "NETBANKING");
    document.getElementById("codForm").classList.toggle("hidden", method !== "COD");
}

async function submitOrder() {
    if (!selectedSlot) {
        showToast("Please choose an available delivery slot.", "warning");
        return;
    }

    const name = document.getElementById("orderName").value.trim();
    const email = document.getElementById("orderEmail").value.trim();
    const phone = document.getElementById("orderPhone").value.trim();
    const address = document.getElementById("orderAddress").value.trim();
    const city = document.getElementById("orderCity").value.trim() || "Central City";
    const pincode = document.getElementById("orderPincode").value.trim();
    const notes = document.getElementById("orderNotes").value.trim();

    if (!name || !email || !phone || !address || !pincode) {
        showToast("Please complete all required address fields.", "warning");
        return;
    }

    const submitBtn = document.getElementById("confirmOrderBtn");
    submitBtn.disabled = true;
    submitBtn.innerHTML = `
        <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white inline" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        Processing Payment & Reserving Godown Inventory...
    `;

    const payload = {
        customer_name: name,
        customer_email: email,
        customer_phone: phone,
        delivery_address: address,
        delivery_city: city,
        delivery_pincode: pincode,
        delivery_notes: notes,
        slot_id: selectedSlot.id,
        coupon_code: appliedCoupon,
        payment_method: activePaymentMethod,
        items: cart.map(item => ({
            product_id: item.product_id,
            quantity: item.quantity
        }))
    };

    try {
        const res = await fetch("/api/orders", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const data = await res.json();

        if (!res.ok) {
            throw new Error(data.detail || "Order could not be placed.");
        }

        // Success! Clear cart
        cart = [];
        saveCart();
        updateCartUI();
        closeCheckoutModal();

        // Show Success Modal
        showSuccessModal(data);
    } catch (err) {
        showToast(err.message, "error");
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = `Confirm Order & Pay Now`;
    }
}

function showSuccessModal(orderData) {
    const modal = document.getElementById("successModal");
    if (!modal) return;

    document.getElementById("successOrderNum").innerText = orderData.order_number;
    document.getElementById("successSlot").innerText = `${orderData.slot_date} (${orderData.slot_window})`;
    document.getElementById("successAmount").innerText = `$${orderData.total_amount.toFixed(2)}`;
    document.getElementById("successAddress").innerText = orderData.delivery_address;
    
    const trackBtn = document.getElementById("successTrackBtn");
    if (trackBtn) {
        trackBtn.href = `/track/${orderData.order_number}`;
    }

    modal.classList.remove("hidden");
}


// ================= TOAST NOTIFICATIONS =================
function showToast(message, type = "info") {
    const container = document.getElementById("toastContainer");
    if (!container) return;

    const toast = document.createElement("div");
    const colors = {
        success: "bg-emerald-800 text-white border-emerald-600",
        warning: "bg-amber-800 text-white border-amber-600",
        error: "bg-red-800 text-white border-red-600",
        info: "bg-slate-900 text-white border-slate-700"
    };

    toast.className = `flex items-center gap-3 px-4 py-3 rounded-xl shadow-lg border text-sm transform transition-all duration-300 translate-y-2 opacity-0 ${colors[type] || colors.info}`;
    toast.innerHTML = `
        <span class="text-base">${type === 'success' ? '✅' : type === 'warning' ? '⚠️' : type === 'error' ? '❌' : 'ℹ️'}</span>
        <span class="font-medium">${message}</span>
    `;

    container.appendChild(toast);
    setTimeout(() => {
        toast.classList.remove("translate-y-2", "opacity-0");
    }, 10);

    setTimeout(() => {
        toast.classList.add("opacity-0", "translate-y-2");
        setTimeout(() => toast.remove(), 300);
    }, 3500);
}
