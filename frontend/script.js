document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('simulation-form');
    const startButton = document.getElementById('start-button');
    const pauseButton = document.getElementById('pause-button');
    const clearButton = document.getElementById('clear-button');
    const workloadInput = document.getElementById('workload-type');
    const customWorkloadRow = document.getElementById('custom-workload-row');
    const statusMessage = document.getElementById('status-message');
    const chartCanvas = document.getElementById('hit-rate-chart');
    const toggleButtons = document.querySelectorAll('.toggle-btn');
    const cacheContainers = document.querySelectorAll('.cache-container');

    const ui = {
        lru: { col: document.getElementById('lru-container').parentElement, hits: document.getElementById('lru-hits'), misses: document.getElementById('lru-misses'), rate: document.getElementById('lru-hit-rate'), list: document.getElementById('lru-cache-list') },
        lfu: { col: document.getElementById('lfu-container').parentElement, hits: document.getElementById('lfu-hits'), misses: document.getElementById('lfu-misses'), rate: document.getElementById('lfu-hit-rate'), list: document.getElementById('lfu-cache-list') },
        lruk: { col: document.getElementById('lruk-container').parentElement, hits: document.getElementById('lruk-hits'), misses: document.getElementById('lruk-misses'), rate: document.getElementById('lruk-hit-rate'), history: document.getElementById('lruk-history-list'), main: document.getElementById('lruk-main-cache-list'), adapt: document.getElementById('adaptive-k-display') }
    };

    let hitRateChart = null, socket = null, isPaused = false;
    let activeCaches = { lru: true, lfu: true, lruk: true };

    form.addEventListener('submit', handleStart);
    pauseButton.addEventListener('click', handlePause);
    clearButton.addEventListener('click', handleClear);
    workloadInput.addEventListener('change', () => {
        customWorkloadRow.style.display = (workloadInput.value === 'custom') ? 'flex' : 'none';
    });
    toggleButtons.forEach(btn => btn.addEventListener('click', handleToggle));
    cacheContainers.forEach(container => {
        container.addEventListener('mouseenter', () => handleHover(container, true));
        container.addEventListener('mouseleave', () => handleHover(container, false));
    });

    function handleToggle(event) {
        const btn = event.currentTarget;
        const cacheKey = btn.dataset.cache;
        activeCaches[cacheKey] = !activeCaches[cacheKey];
        btn.classList.toggle('active');
        btn.textContent = activeCaches[cacheKey] ? 'ON' : 'OFF';
        ui[cacheKey].col.classList.toggle('disabled');
        if (hitRateChart) {
            const datasetIndex = Object.keys(activeCaches).indexOf(cacheKey);
            hitRateChart.setDatasetVisibility(datasetIndex, activeCaches[cacheKey]);
            hitRateChart.update('none');
        }
    }

    function handleStart(event) {
        event.preventDefault();
        if (socket) socket.close();
        const config = {
            capacity: parseInt(document.getElementById('capacity').value),
            k_value: parseInt(document.getElementById('k-value').value),
            adaptive_k: document.getElementById('adaptive-k').checked,
            speed: 1.05 - parseFloat(document.getElementById('speed-slider').value),
            workload_type: workloadInput.value,
            custom_workload: document.getElementById('custom-workload').value,
            active_caches: activeCaches,
            workload_size: 50
        };
        if (Object.values(activeCaches).every(v => !v)) {
            statusMessage.textContent = "Error: At least one cache must be active.";
            return;
        }
        startButton.disabled = true;
        pauseButton.disabled = false;
        isPaused = false;
        pauseButton.textContent = 'Pause';
        statusMessage.textContent = 'Connecting...';
        resetUI();
        initializeChart();
        socket = new WebSocket(`ws://127.0.0.1:8000/ws/simulation`);
        socket.onopen = () => {
            statusMessage.textContent = 'Connection open. Starting simulation...';
            socket.send(JSON.stringify(config));
        };
        socket.onmessage = (msg) => {
            if (isPaused) return;
            const data = JSON.parse(msg.data);
            updateUI(data);
            updateChart(data);
        };
        socket.onclose = () => {
            statusMessage.textContent = 'Simulation finished. Ready for a new run.';
            startButton.disabled = false;
            pauseButton.disabled = true;
        };
    }

    function handlePause() {
        isPaused = !isPaused;
        pauseButton.textContent = isPaused ? 'Resume' : 'Pause';
        statusMessage.textContent = `Simulation ${isPaused ? 'paused' : 'resumed'}.`;
    }
    
    function handleClear() {
        if (socket) socket.close();
        resetUI();
        initializeChart();
        statusMessage.textContent = 'Ready to start simulation.';
        startButton.disabled = false;
        pauseButton.disabled = true;
    }

    function handleHover(element, isEntering) {
        if (isEntering) element.classList.add('hover-active');
        else element.classList.remove('hover-active');
    }

    function updateUI(data) {
        statusMessage.innerHTML = `Step ${data.step}/${data.total_steps}: Accessing Key <span class="highlight">${data.current_key}</span>`;
        Object.keys(activeCaches).forEach(key => {
            if (!activeCaches[key] || !data[`${key}_cache`]) return;
            const cacheData = data[`${key}_cache`];
            const misses = data.step - cacheData.hits;
            ui[key].hits.textContent = cacheData.hits;
            ui[key].misses.textContent = misses;
            ui[key].rate.textContent = (cacheData.hit_rate * 100).toFixed(2) + '%';
        });
        if (activeCaches.lru && data.lru_cache) updateList(ui.lru.list, data.lru_cache.state, data.current_key, null, 'lru');
        if (activeCaches.lfu && data.lfu_cache) updateList(ui.lfu.list, data.lfu_cache.state, data.current_key, null, 'lfu');
        if (activeCaches.lruk && data.lruk_cache) {
            updateList(ui.lruk.history, data.lruk_cache.state.history_cache, data.current_key, null, 'lruk');
            updateList(ui.lruk.main, data.lruk_cache.state.main_cache, data.current_key, data.lruk_cache.last_event, 'lruk');
            ui.lruk.adapt.textContent = document.getElementById('adaptive-k').checked ? `(K=${data.lruk_cache.state.current_k})` : '';
        }
    }

    function updateList(listEl, items, currentKey, event, type) {
        listEl.innerHTML = '';
        items.forEach(item => {
            const itemEl = document.createElement('div');
            itemEl.classList.add('cache-item');
            itemEl.textContent = item;
            if (item === currentKey) {
                if (event && event.promoted) itemEl.classList.add('item-promoted');
                else itemEl.classList.add('item-accessed', type);
            }
            listEl.appendChild(itemEl);
        });
    }

    function resetUI() {
        Object.values(ui).forEach(cacheUI => {
            Object.values(cacheUI).forEach(el => {
                if (el.tagName === 'SPAN') el.textContent = '0';
                else if (el.tagName === 'DIV' && el.classList.contains('cache-list')) el.innerHTML = '';
            });
            ui.lru.rate.textContent = ui.lfu.rate.textContent = ui.lruk.rate.textContent = '0.00%';
        });
        ui.lruk.adapt.textContent = '';
    }

    function initializeChart() {
        if (hitRateChart) hitRateChart.destroy();
        const brighterTextColor = '#e5e7eb';
        hitRateChart = new Chart(chartCanvas.getContext('2d'), {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    { label: 'LRU', data: [], borderColor: '#4a90e2', tension: 0.3, hidden: !activeCaches.lru },
                    { label: 'LFU', data: [], borderColor: '#b87fe9', tension: 0.3, hidden: !activeCaches.lfu },
                    { label: 'LRU-K', data: [], borderColor: '#50e3c2', tension: 0.3, hidden: !activeCaches.lruk }
                ]
            },
            options: {
                scales: {
                    y: { beginAtZero: true, max: 1, ticks: { color: brighterTextColor, callback: v => (v * 100).toFixed(0) + '%' }, title: { display: true, text: 'Hit Rate', color: '#f0f0f0', font: {size: 14} } },
                    x: { ticks: { color: brighterTextColor }, title: { display: true, text: 'Simulation Step', color: '#f0f0f0', font: {size: 14} } }
                },
                plugins: { legend: { labels: { color: '#f0f0f0' } } },
                animation: { duration: 0 }, maintainAspectRatio: false
            }
        });
    }
    
    function updateChart(data) {
        if (!hitRateChart) return;
        hitRateChart.data.labels.push(data.step);
        
        const datasets = hitRateChart.data.datasets;
        datasets[0].data.push(data.lru_cache ? data.lru_cache.hit_rate : NaN);
        datasets[1].data.push(data.lfu_cache ? data.lfu_cache.hit_rate : NaN);
        datasets[2].data.push(data.lruk_cache ? data.lruk_cache.hit_rate : NaN);

        hitRateChart.update('none');
    }

    handleClear();
});