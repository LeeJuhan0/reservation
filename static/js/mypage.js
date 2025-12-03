document.addEventListener('DOMContentLoaded', () => {
    fetchUserName();
    loadMyReservations();
});

// 사용자 이름 가져오기
async function fetchUserName() {
    try {
        const response = await fetch('/auth/me');
        if (response.ok) {
            const data = await response.json();
            document.getElementById('userName').textContent = data.name;
        }
    } catch (error) {
        console.error("User fetch error:", error);
    }
}

// 예약 목록 불러오기
async function loadMyReservations() {
    const tableBody = document.getElementById('myResTableBody');

    try {
        const response = await fetch('/reservation/api/my-reservations');

        if (!response.ok) { // 로그인 안됨
            window.location.href = '/';
            return;
        }

        const reservations = await response.json();

        tableBody.innerHTML = '';

        if (reservations.length === 0) {
            tableBody.innerHTML = '<tr><td colspan="7" style="padding: 30px;">No reservations found.</td></tr>';
            return;
        }

        reservations.forEach(res => {
            const row = `
                <tr>
                    <td>${res.date}</td>
                    <td>${res.time_slot}</td>
                    <td>${res.building_name}</td>
                    <td>${res.room_no}</td>
                    <td>${res.people_count}</td>
                    <td><span class="status-badge">Reserved</span></td>
                    <td>
                        <button class="btn-cancel" onclick="cancelBooking(${res.id})">
                            Cancel
                        </button>
                    </td>
                </tr>
            `;
            tableBody.insertAdjacentHTML('beforeend', row);
        });

    } catch (error) {
        console.error("Error loading reservations:", error);
        tableBody.innerHTML = '<tr><td colspan="7">Error loading data.</td></tr>';
    }
}

// 예약 취소 함수
async function cancelBooking(reservationId) {
    if (!confirm("Are you sure you want to cancel this reservation?")) {
        return;
    }

    try {
        const response = await fetch('/reservation/api/cancel', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ reservation_id: reservationId })
        });

        const result = await response.json();

        if (response.ok) {
            alert("Reservation cancelled.");
            loadMyReservations(); // 목록 새로고침
        } else {
            alert("Failed: " + result.message);
        }

    } catch (error) {
        console.error("Cancel error:", error);
        alert("Server error.");
    }
}