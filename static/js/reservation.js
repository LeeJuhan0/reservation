document.addEventListener('DOMContentLoaded', () => {
    fetchUserName(); // 사용자 이름 표시
    const searchRoomsBtn = document.getElementById('searchRoomsBtn');
    const findSlotsBtn = document.getElementById('findSlotsBtn');
    const bookingBtn = document.getElementById('bookingBtn');
    const buildingSelect = document.getElementById('buildingSelect');
    const floorSelect = document.getElementById('floorSelect');
    const roomTableBody = document.getElementById('roomTableBody');
    const slotsGrid = document.getElementById('slotsGrid');
    const slotsMessage = document.getElementById('slotsMessage');

    // 상태 변수
    let selectedRoomId = null;
    let selectedRoomCapacity = 0;
    let selectedSlot = null;
    let selectedDate = null;


    //  방 검색
    searchRoomsBtn.addEventListener('click', async () => {
        const building = buildingSelect.value;
        const floor = floorSelect ? floorSelect.value : ''; // floorSelect가 없으면 빈 값

        if (!building && !floor) {
            alert("Please select at least a Building or Floor.");
            return;
        }

        try {
            const response = await fetch(`/reservation/api/rooms?building=${building}&room_floor=${floor}`);
            const rooms = await response.json();

            roomTableBody.innerHTML = '';
            selectedRoomId = null;
            clearSlots();

            if (rooms.length === 0) {
                roomTableBody.innerHTML = '<tr><td colspan="8" style="text-align:center;">No rooms found.</td></tr>';
                return;
            }

            rooms.forEach(room => {
                const isAvailable = (room.availability == 1);
                const statusColor = isAvailable ? 'green' : 'red';
                const statusText = isAvailable ? 'Available' : 'Unavailable';
                const disabledAttr = isAvailable ? '' : 'disabled';
                const cursorStyle = isAvailable ? 'cursor:pointer;' : 'cursor:not-allowed; opacity:0.5;';

                const row = `
                    <tr style="${cursorStyle}"> 
                        <td>                       
                            <input type="radio" name="selectedRoom" 
                                   value="${room.id}" 
                                   data-capacity="${room.capacity}" 
                                   ${disabledAttr}>
                        </td>
                        <td>${room.room_no}</td>
                        <td>${room.room_type || '-'}</td>
                        <td>${room.room_floor || '-'}</td>
                        <td>${room.desk_type || '-'}</td>
                        <td>${room.capacity || '-'}</td>
                        <td style="color: ${statusColor}; font-weight:bold;">${statusText}</td>
                        <td>${room.remark || '-'}</td>
                    </tr>
                `;
                roomTableBody.insertAdjacentHTML('beforeend', row);
            });

            document.querySelectorAll('input[name="selectedRoom"]').forEach(radio => {
                radio.addEventListener('change', (e) => {
                    selectedRoomId = e.target.value;
                    selectedRoomCapacity = parseInt(e.target.dataset.capacity || 0);

                    // 콘솔에서 확인 가능
                    console.log(`방 선택됨: ID=${selectedRoomId}, Capacity=${selectedRoomCapacity}`);

                    clearSlots();
                    slotsMessage.textContent = `Room selected (Max ${selectedRoomCapacity} people).`;
                });
            });

        } catch (error) {
            console.error("Error fetching rooms:", error);
        }
    });

    // 슬롯 찾기
    findSlotsBtn.addEventListener('click', async () => {
        const dateInput = document.getElementById('resDate').value;
        const peopleInput = document.getElementById('resPeople').value;

        if (!selectedRoomId) {
            alert("Please select a room from the list first.");
            return;
        }

        const inputCount = parseInt(peopleInput);
        if (!inputCount || inputCount < 1) {
            alert("Please enter a valid people count.");
            return;
        }

        if (inputCount > selectedRoomCapacity) {
            alert(`Capacity exceeded!\n\nThis room allows only up to ${selectedRoomCapacity} people.\n(Current input: ${inputCount})`);
            return;
        }

        if (!dateInput) {
            alert("Please select a date.");
            return;
        }

        if (!dateInput) {
            alert("Please select a date.");
            return;
        }
        if (!peopleInput || peopleInput < 1) {
            alert("Please enter valid people count.");
            return;
        }

        selectedDate = dateInput; // 날짜 저장

        try {
            const response = await fetch(`/reservation/api/slots?building_id=${selectedRoomId}&date=${dateInput}`);
            const data = await response.json();

            renderSlots(data.available_slots);

        } catch (error) {
            console.error("Error fetching slots:", error);
        }
    });

    // 슬롯 렌더링 함수
    function renderSlots(slots) {
        slotsGrid.innerHTML = ''; // 초기화
        selectedSlot = null;

        if (slots.length === 0) {
            slotsMessage.textContent = "No slots available for this date.";
            return;
        }

        slotsMessage.textContent = "Select a time slot below.";

        slots.forEach(time => {
            const btn = document.createElement('button');
            btn.className = 'slot-btn';
            btn.textContent = time;

            btn.addEventListener('click', () => {

                document.querySelectorAll('.slot-btn').forEach(b => b.classList.remove('selected'));
                btn.classList.add('selected');
                selectedSlot = time;
            });

            slotsGrid.appendChild(btn);
        });
    }

    //  예약하기 (Booking)
    bookingBtn.addEventListener('click', async () => {
        const peopleInput = document.getElementById('resPeople').value;

        if (!selectedRoomId || !selectedDate || !selectedSlot) {
            alert("Please select a room, date, and a time slot.");
            return;
        }

        if(!confirm(`Book Room for ${selectedDate} at ${selectedSlot}?`)) {
            return;
        }

        try {
            const response = await fetch('/reservation/api/book', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    building_id: selectedRoomId,
                    date: selectedDate,
                    time_slot: selectedSlot,
                    people_count: peopleInput
                })
            });

            const result = await response.json();

            if (response.ok) {
                alert(result.message);
                window.location.reload(); // 페이지 새로고침
            } else {
                alert("Booking failed: " + result.message);
            }

        } catch (error) {
            console.error("Booking error:", error);
            alert("Server error during booking.");
        }
    });

    // 슬롯 초기화 함수
    function clearSlots() {
        slotsGrid.innerHTML = '';
        slotsMessage.textContent = "Select a room and click 'Find Slots'.";
        selectedSlot = null;
    }

    // 사용자 이름 가져오기
    async function fetchUserName() {
        try {
            const response = await fetch('/auth/me');
            if (response.ok) {
                const data = await response.json();
                document.getElementById('userName').textContent = data.name;
            } else {
                document.getElementById('userName').textContent = "Guest";
            }
        } catch (error) {
            console.error("User fetch error:", error);
        }
    }
});