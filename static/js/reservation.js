document.addEventListener('DOMContentLoaded', function() {

    // 1. 사용자 이름 가져오기
    fetchUserName();

    // 요소 참조
    const buildingSelect = document.getElementById('buildingSelect');
    const roomSelect = document.getElementById('roomSelect');
    const searchRoomsBtn = document.getElementById('searchRoomsBtn');

    const findSlotsBtn = document.getElementById('findSlotsBtn');
    const bookingBtn = document.getElementById('bookingBtn');

    const slotsGrid = document.getElementById('slotsGrid');
    const slotsMessage = document.getElementById('slotsMessage');
    const roomTableBody = document.getElementById('roomTableBody');

    // 입력 필드
    const dateInput = document.getElementById('resDate');
    const peopleInput = document.getElementById('resPeople');

    // 상태 변수
    let selectedRoom = null; // 선택된 방 객체 { id, room_no, capacity ... }

    // --------------------------------------------------------
    // 1. 사용자 이름 Fetch
    // --------------------------------------------------------
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

    // --------------------------------------------------------
    // 2. [Search Rooms] 버튼 클릭 -> 방 리스트 DB 조회
    // --------------------------------------------------------
    searchRoomsBtn.addEventListener('click', async () => {
        const building = buildingSelect.value;
        const roomNo = roomSelect.value;

        // 건물 선택 필수
        if (!building) {
            alert("Please select a building.");
            return;
        }

        try {
            // room_no도 함께 보냄 (값이 없으면 빈 문자열)
            const params = new URLSearchParams({
                building: building,
                room_no: roomNo || ''
            });

            const response = await fetch(`/reservation/api/rooms?${params}`);
            if (!response.ok) throw new Error("Failed to fetch rooms");

            const rooms = await response.json();
            renderRoomTable(rooms);

        } catch (error) {
            console.error("Error fetching rooms:", error);
            alert("Failed to load room list.");
        }
    });

    // 방 목록 렌더링 함수
    function renderRoomTable(rooms) {
        roomTableBody.innerHTML = '';
        selectedRoom = null;
        slotsGrid.innerHTML = '';
        slotsMessage.textContent = 'Select a room and click \'Find Slots\' to see availability.';

        if (!rooms || rooms.length === 0) {
            roomTableBody.innerHTML = '<tr><td colspan="8" style="text-align:center;">No rooms found based on your criteria.</td></tr>';
            return;
        }

        rooms.forEach(room => {
            const tr = document.createElement('tr');

            // Status에 따른 스타일
            let badgeClass = 'status-vacant';
            const status = room.status || 'Vacant';

            if(status === 'Dirty') badgeClass = 'status-dirty';
            else if(status === 'Occupied') badgeClass = 'status-occupied';
            else if(status === 'Reserved') badgeClass = 'status-reserved';

            // DB 컬럼명 매핑 주의 (room.room_no, room.people_count 등)
            tr.innerHTML = `
                <td><input type="radio" name="room_selection" value="${room.id}"></td>
                <td>${room.room_no}</td>
                <td>${room.type}</td>
                <td>${room.floor}</td>
                <td>${room.desk_type}</td>
                <td><i class="fas fa-users"></i> ${room.capacity}</td>
                <td><span class="status-badge ${badgeClass}">${status}</span></td>
                <td>${room.remarks || '-'}</td>
            `;

            // 행 클릭 이벤트
            tr.addEventListener('click', () => {
                const radio = tr.querySelector('input[name="room_selection"]');
                radio.checked = true;
                selectedRoom = room;
            });

            roomTableBody.appendChild(tr);
        });
    }

    // --------------------------------------------------------
    // 3. [Find Slots] 버튼 클릭 -> 예약 가능 슬롯 DB 조회
    // --------------------------------------------------------
    findSlotsBtn.addEventListener('click', async () => {
        // 방 선택 여부 확인
        if (!selectedRoom) {
            alert("Please select a room from the list first.");
            return;
        }

        const date = dateInput.value;
        const people = parseInt(peopleInput.value);

        if (!date || !people) {
            alert("Please select Date and enter Number of People.");
            return;
        }

        // 인원 초과 체크
        if (people > selectedRoom.capacity) {
            alert(`This room allows up to ${selectedRoom.capacity} people.`);
            return;
        }

        try {
            // API 호출 시 room_id (DB PK)를 넘김
            const params = new URLSearchParams({
                room_id: selectedRoom.id,
                date: date,
                people: people
            });

            const response = await fetch(`/reservation/api/slots?${params}`);
            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.message || "Failed to fetch slots");
            }

            const availableSlots = await response.json();

            slotsMessage.textContent = `Available slots for Room ${selectedRoom.room_no} on ${date}`;
            renderTimeSlots(availableSlots);

        } catch (error) {
            console.error("Error fetching slots:", error);
            alert(error.message);
            slotsGrid.innerHTML = '';
        }
    });

    // 슬롯 버튼 렌더링
    function renderTimeSlots(slots) {
        slotsGrid.innerHTML = '';

        if (!slots || slots.length === 0) {
            slotsGrid.innerHTML = '<p style="color:red;">No available slots for this condition.</p>';
            return;
        }

        slots.forEach(time => {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'slot-btn';
            btn.textContent = time; // 예: "09:00"

            btn.addEventListener('click', () => {
                // 단일 선택 로직
                document.querySelectorAll('.slot-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
            });

            slotsGrid.appendChild(btn);
        });
    }

    // --------------------------------------------------------
    // 4. [Booking] 버튼 클릭 -> 예약 요청 전송
    // --------------------------------------------------------
    bookingBtn.addEventListener('click', async () => {
        const activeSlot = document.querySelector('.slot-btn.active');

        if (!selectedRoom || !activeSlot) {
            alert("Please select a room and a time slot.");
            return;
        }

        const ioTypeElement = document.querySelector('input[name="io_type"]:checked');
        const ioType = ioTypeElement ? ioTypeElement.value : 'in';

        const bookingData = {
            room_id: selectedRoom.id,       // DB PK
            room_no: selectedRoom.room_no,  // 필요 시 전송 (선택 사항)
            date: dateInput.value,
            time_slot: activeSlot.textContent,
            people: parseInt(peopleInput.value),
            type: ioType
        };

        try {
            const response = await fetch('/reservation/api/book', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(bookingData)
            });

            const result = await response.json();

            if (response.ok) {
                alert("Reservation Successful!");
                // 성공 후 페이지 새로고침하여 상태 반영
                window.location.reload();
            } else {
                alert("Booking Failed: " + (result.message || "Unknown error"));
            }

        } catch (error) {
            console.error("Booking Error:", error);
            alert("An error occurred during booking.");
        }
    });
});