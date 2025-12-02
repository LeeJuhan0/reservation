document.addEventListener('DOMContentLoaded', () => {
    const registerForm = document.getElementById('registerForm');
    const errorAlert = document.getElementById('errorAlert');
    const alertTitle = document.getElementById('alertTitle');
    const alertMessage = document.getElementById('alertMessage');
    const closeAlertBtn = document.getElementById('closeAlert');

    closeAlertBtn.addEventListener('click', () => {
        errorAlert.style.display = 'none';
    });

    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        // 폼 데이터 수집
        const formData = new FormData(registerForm);
        const data = Object.fromEntries(formData.entries());

        // 개인정보 수집 동의 확인
        if (data.privacy_agree !== 'yes') {
            showAlert('Registration Failed', 'You must agree to the privacy policy.');
            return;
        }

        const requestPayload = {
            fullName: data.full_name,
            email: data.email,
            password: data.password,
            mobileNumber: data.mobile_number,
            studentId: data.student_id,
            message: data.message,
            marketingAgree: data.marketing_agree === 'yes'
        };

        try {
            const response = await fetch('/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(requestPayload)
            });

            const result = await response.json();

            if (response.ok) {
                alert('Registration successful! Moving to reservation page.');
                // result.redirect에 "/reservation"이 들어있음
                window.location.href = result.redirect;
            } else {
                showAlert('Registration Error', result.message || 'Failed to register.');
            }
        } catch (error) {
            console.error('Error:', error);
            showAlert('Network Error', 'A network error occurred. Please check your connection.');
        }
    });

    function showAlert(title, message) {
        alertTitle.textContent = title;
        alertMessage.textContent = message;
        errorAlert.style.display = 'flex';
        errorAlert.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
});