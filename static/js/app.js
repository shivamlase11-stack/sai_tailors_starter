document.addEventListener("DOMContentLoaded", () => {
    const notificationBtn = document.getElementById("notificationBtn");
    const notificationPanel = document.getElementById("notificationPanel");

    if (notificationBtn && notificationPanel) {
        notificationBtn.addEventListener("click", async (e) => {
            e.stopPropagation();
            notificationPanel.classList.toggle("open");
            if (notificationPanel.classList.contains("open")) {
                const res = await fetch("/search?q=");
                const data = await res.json();
                const today = new Date().toISOString().slice(0, 10);
                const deliveries = data.filter(x => x.delivery_date === today && x.status !== "Completed");
                const list = document.getElementById("deliveryList");
                if (list) {
                    list.innerHTML = deliveries.length
                        ? deliveries.map(x => `<div class="delivery-item"><strong>${x.name}</strong><span>${x.receipt_no} · ${x.status}</span></div>`).join("")
                        : '<p class="muted">No deliveries scheduled for today.</p>';
                }
            }
        });
        document.addEventListener("click", () => notificationPanel.classList.remove("open"));
    }

    const search = document.getElementById("customerSearch");
    const results = document.getElementById("searchResults");
    let timer;

    if (search && results) {
        search.addEventListener("input", () => {
            clearTimeout(timer);
            const q = search.value.trim();
            if (!q) {
                results.innerHTML = "";
                results.classList.remove("show");
                return;
            }
            timer = setTimeout(async () => {
                const res = await fetch(`/search?q=${encodeURIComponent(q)}`);
                const data = await res.json();
                results.innerHTML = data.length
                    ? data.map(x => `<div class="result-item"><div><strong>${x.name}</strong><span>${x.mobile} · ${x.receipt_no}</span></div><span class="status ${x.status.toLowerCase()}">${x.status}</span></div>`).join("")
                    : '<div class="result-item"><span>No customer found.</span></div>';
                results.classList.add("show");
            }, 180);
        });
    }

    const shirtToggle = document.getElementById("shirtToggle");
    const pantToggle = document.getElementById("pantToggle");
    const shirtSection = document.getElementById("shirtSection");
    const pantSection = document.getElementById("pantSection");
    const shirtQty = document.getElementById("shirtQty");
    const pantQty = document.getElementById("pantQty");
    const paid = document.getElementById("paid");
    const shirtSubtotal = document.getElementById("shirtSubtotal");
    const pantSubtotal = document.getElementById("pantSubtotal");
    const totalAmount = document.getElementById("totalAmount");
    const balance = document.getElementById("balance");

    function calculate() {
        if (!shirtToggle) return;
        if (!shirtToggle.checked) shirtQty.value = 0;
        if (!pantToggle.checked) pantQty.value = 0;
        const shirt = Number(shirtQty.value || 0) * 350;
        const pant = Number(pantQty.value || 0) * 350;
        const total = shirt + pant;
        const paidValue = Number(paid.value || 0);
        shirtSubtotal.textContent = `₹${shirt}`;
        pantSubtotal.textContent = `₹${pant}`;
        totalAmount.textContent = `₹${total}`;
        balance.value = Math.max(total - paidValue, 0);
    }

    function toggleSections() {
        if (!shirtToggle) return;
        shirtSection.classList.toggle("hidden", !shirtToggle.checked);
        pantSection.classList.toggle("hidden", !pantToggle.checked);
        calculate();
    }

    shirtToggle?.addEventListener("change", toggleSections);
    pantToggle?.addEventListener("change", toggleSections);
    shirtQty?.addEventListener("input", calculate);
    pantQty?.addEventListener("input", calculate);
    paid?.addEventListener("input", calculate);
    toggleSections();
});
