async function fetchIp() {
    const response = await fetch('/get_ip');
    const data = await response.json();
    const videoElement = document.getElementById('link');
    videoElement.href = `http://${data.ip}:${data.port}/video_feed`;
}

async function setSizeRange() {
    const minWidth = document.getElementById('min-width').value;
    const maxWidth = document.getElementById('max-width').value;
    const minHeight = document.getElementById('min-height').value;
    const maxHeight = document.getElementById('max-height').value;

    const response = await fetch('/set_size_range', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            min_width: minWidth,
            max_width: maxWidth,
            min_height: minHeight,
            max_height: maxHeight
        }),
    });

    const result = await response.json();
    if (result.status === 'success') {
        alert('Size range set successfully');
    } else {
        alert('Failed to set size range');
    }
}

async function resetSizeRange() {
    const response = await fetch('/reset_size_range', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
    });

    const result = await response.json();
    if (result.status === 'success') {
        alert('Size range reset successfully');
    } else {
        alert('Failed to reset size range');
    }
}

async function setArucoSize() {
    const arucoSize = document.getElementById('aruco-size').value;

    const response = await fetch('/set_aruco_size', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            aruco_size: arucoSize
        }),
    });

    const result = await response.json();
    if (result.status === 'success') {
        alert('Aruco size set successfully');
    } else {
        alert('Failed to set Aruco size');
    }
}

async function refreshMeasurements() {
    try {
        const response = await fetch('/measurements');
        const data = await response.json();
        const tbody = document.getElementById('measurements-body');
        tbody.innerHTML = '';

        data.measurements.forEach(m => {
            const row = document.createElement('tr');
            const timestamp = new Date(m.timestamp);
            const formattedTime = timestamp.toLocaleString();
            
            row.innerHTML = `
                <td>${m.width.toFixed(1)}</td>
                <td>${m.height.toFixed(1)}</td>
                <td>${formattedTime}</td>
                <td>${m.is_in_range ? '<span class="in-range">In Range</span>' : '<span class="out-of-range">Out of Range</span>'}</td>
                <td>${m.measurement_mode}</td>
            `;
            tbody.appendChild(row);
        });
    } catch (error) {
        console.error('Error fetching measurements:', error);
    }
}

async function clearOldMeasurements() {
    try {
        const response = await fetch('/clear_old_measurements', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ days: 7 })
        });
        
        const result = await response.json();
        if (result.status === 'success') {
            refreshMeasurements();
        }
    } catch (error) {
        console.error('Error clearing old measurements:', error);
    }
}

// Auto-refresh measurements every 5 seconds
setInterval(refreshMeasurements, 5000);

window.onload = () => {
    fetchIp();
    refreshMeasurements();
};