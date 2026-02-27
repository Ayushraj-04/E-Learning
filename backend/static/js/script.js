/* =====================================================
   1. TAB SWITCHING LOGIC 
===================================================== */
function openTab(tabId, btnElement) {
    // Hide all tab content boxes
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    // Remove highlight from all defined bar buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected box and highlight bar
    document.getElementById(tabId).classList.add('active');
    btnElement.classList.add('active');
}

/* =====================================================
   2. LIVE FILTERING LOGIC (For the Result Boxes)
===================================================== */
const durationFilter = document.getElementById("durationFilter");
const costFilter = document.getElementById("costFilter");

function filterResults() {
    if (!durationFilter || !costFilter) return;

    const selectedDuration = durationFilter.value;
    const selectedCost = costFilter.value;
    const cards = document.querySelectorAll(".result-card");

    cards.forEach(card => {
        const cardDuration = card.getAttribute("data-duration");
        const cardCost = card.getAttribute("data-cost");

        const matchesDuration = (selectedDuration === "all") || (cardDuration === selectedDuration);
        const matchesCost = (selectedCost === "all") || (cardCost === selectedCost);

        if (matchesDuration && matchesCost) {
            card.style.display = "flex"; 
        } else {
            card.style.display = "none";
        }
    });
}

// Attach listeners if on the results page
if (durationFilter && costFilter) {
    durationFilter.addEventListener("change", filterResults);
    costFilter.addEventListener("change", filterResults);
    
    // Parse URL params to apply filters directly from Home Page
    const urlParams = new URLSearchParams(window.location.search);
    const urlDuration = urlParams.get('duration');
    const urlCost = urlParams.get('cost');
    
    if (urlDuration) durationFilter.value = urlDuration;
    if (urlCost) costFilter.value = urlCost;
    
    // Run filter immediately
    filterResults();
}