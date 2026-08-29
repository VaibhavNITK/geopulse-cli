document.addEventListener("DOMContentLoaded", () => {
    let map = null;
    let marker = null;

    // Elements
    const targetInput = document.getElementById("target-input");
    const searchForm = document.getElementById("search-form");
    const searchBtn = document.getElementById("search-btn");
    const btnText = document.getElementById("btn-text");
    const btnSpinner = document.getElementById("btn-spinner");
    const copyBtn = document.getElementById("copy-btn");
    const queryBadge = document.getElementById("query-badge");

    // Stat fields
    const valIp = document.getElementById("val-ip");
    const valLocation = document.getElementById("val-location");
    const valCoords = document.getElementById("val-coords");
    const valIsp = document.getElementById("val-isp");
    const valAsn = document.getElementById("val-asn");
    const valTz = document.getElementById("val-tz");
    const valLatency = document.getElementById("val-latency");

    // Initialize Leaflet Map (Using Public Esri Dark Gray Base Tiles - No API Key Required)
    function initMap(lat = 20, lon = 77) {
        if (!map) {
            map = L.map("map").setView([lat, lon], 4);
            L.tileLayer("https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}", {
                attribution: 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ',
                maxZoom: 16,
            }).addTo(map);
        }
    }

    function updateMap(lat, lon, title) {
        if (!map) initMap(lat, lon);
        map.flyTo([lat, lon], 9, { duration: 1.5 });

        if (marker) {
            map.removeLayer(marker);
        }

        const customIcon = L.divIcon({
            className: 'custom-map-pin',
            html: `<div style="background-color: #00f2fe; width: 16px; height: 16px; border-radius: 50%; border: 3px solid #fff; box-shadow: 0 0 18px #00f2fe;"></div>`,
            iconSize: [22, 22],
            iconAnchor: [11, 11]
        });

        marker = L.marker([lat, lon], { icon: customIcon }).addTo(map)
            .bindPopup(`<b>${title}</b><br>Lat: ${lat}, Lon: ${lon}`)
            .openPopup();
    }

    // Fetch IP Geolocation Data
    async function fetchGeoData(target = "") {
        setLoading(true);
        const startTime = performance.now();

        try {
            const url = target ? `https://ipapi.co/${target}/json/` : `https://ipapi.co/json/`;
            const resp = await fetch(url);
            const data = await resp.json();
            const latency = Math.round(performance.now() - startTime);

            if (data.error || data.reason) {
                // Fallback to ip-api
                const fbResp = await fetch(`https://ipapi.co/${target}/json/`);
                const fbData = await fbResp.json();
                renderData(fbData, latency, target === "");
            } else {
                renderData(data, latency, target === "");
            }
        } catch (err) {
            console.error("Fetch error:", err);
            try {
                const fbResp = await fetch(`https://ipapi.co/${target}/json/`);
                const fbData = await fbResp.json();
                renderData(fbData, Math.round(performance.now() - startTime), target === "");
            } catch (e) {
                alert("Network error fetching IP geolocation.");
            }
        } finally {
            setLoading(false);
        }
    }

    function renderData(data, latency, isSelf) {
        valIp.textContent = data.ip || "--";
        valLocation.textContent = `${data.city || ''}, ${data.region || ''} | ${data.country_name || ''} (${data.country_code || ''})`;
        valCoords.textContent = `${data.latitude || 0}, ${data.longitude || 0}`;
        valIsp.textContent = data.org || data.network || "--";
        valAsn.textContent = data.asn || data.asn || "--";
        valTz.textContent = data.timezone || "--";
        valLatency.textContent = `${latency} ms`;

        queryBadge.textContent = isSelf ? "My Network" : "Target Diagnostics";
        queryBadge.className = isSelf ? "badge badge-success" : "badge badge-primary";

        if (data.latitude && data.longitude) {
            updateMap(data.latitude, data.longitude, `${data.ip} (${data.city || 'Target'})`);
        }
    }

    function setLoading(isLoading) {
        if (isLoading) {
            btnText.classList.add("hidden");
            btnSpinner.classList.remove("hidden");
            searchBtn.disabled = true;
        } else {
            btnText.classList.remove("hidden");
            btnSpinner.classList.add("hidden");
            searchBtn.disabled = false;
        }
    }

    // Search Form Handler
    searchForm.addEventListener("submit", (e) => {
        e.preventDefault();
        const query = targetInput.value.trim();
        if (query) {
            fetchGeoData(query);
        }
    });

    // Quick Tag Chips
    document.querySelectorAll(".chip").forEach(chip => {
        chip.addEventListener("click", () => {
            const ip = chip.getAttribute("data-ip");
            targetInput.value = ip;
            fetchGeoData(ip);
        });
    });

    // Copy Code Handler
    copyBtn.addEventListener("click", () => {
        const text = "curl -fsSL https://raw.githubusercontent.com/VaibhavNITK/geopulse-cli/main/install.sh | bash";
        navigator.clipboard.writeText(text).then(() => {
            copyBtn.innerHTML = '<i class="fa-solid fa-check" style="color:#10b981;"></i>';
            setTimeout(() => {
                copyBtn.innerHTML = '<i class="fa-regular fa-copy"></i>';
            }, 2000);
        });
    });

    // Initial Load
    initMap();
    fetchGeoData("");
});
