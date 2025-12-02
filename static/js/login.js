document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const togglePasswordBtn = document.getElementById('togglePassword');
    const passwordInput = document.getElementById('password');

    // 비밀번호 보이기/숨기기 토글
    if (togglePasswordBtn && passwordInput) {
        togglePasswordBtn.addEventListener('click', () => {
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);

            const icon = togglePasswordBtn.querySelector('i');
            if (type === 'text') {
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
                togglePasswordBtn.childNodes[2].nodeValue = ' Show';
            } else {
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
                togglePasswordBtn.childNodes[2].nodeValue = ' Hide';
            }
        });
    }

    // 로그인 폼 제출 처리
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            try {
                const response = await fetch('/auth/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ email: email, password: password })
                });

                const result = await response.json();

                if (response.ok) {
                    // 로그인 성공: 서버가 보내준 리다이렉트 주소로 이동
                    window.location.href = result.redirect;
                } else {
                    // 로그인 실패
                    alert(result.message || 'Login failed');
                }

            } catch (error) {
                console.error('Error:', error);
                alert('Network error occurred.');
            }
        });
    }
});