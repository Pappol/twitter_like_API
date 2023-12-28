document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const registerForm = document.getElementById('registerForm');
    const errorMessage = document.createElement('div');

    // Function to make authenticated requests
    async function fetchWithAuth(url, options = {}) {
        // Retrieve the token from local storage
        const token = localStorage.getItem('token');

        // Add the Authorization header to the request
        const headers = new Headers(options.headers || {});
        if (token) {
            headers.append('Authorization', `Bearer ${token}`);
        }

        // Make the fetch request with the updated headers
        const response = await fetch(url, { ...options, headers });
        return response.json();
    }

    // Login functionality
    if (loginForm) {
        loginForm.onsubmit = async (e) => {
            e.preventDefault();

            // Get user input
            const username = document.getElementById('loginUsername').value;
            const password = document.getElementById('loginPassword').value;

            try {
                // Send POST request to the server
                const response = await fetch('/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        username: username,
                        password: password
                    })
                });

                const result = await response.json();

                // Check if login was successful
                if (response.ok) {
                    // Store the token in local storage
                    localStorage.setItem('token', result.access_token);

                    // Redirect to the homepage
                    window.location.href = '/';
                } else {
                    // Display error message
                    errorMessage.textContent = result.detail || 'Login failed. Please try again.';
                    loginForm.appendChild(errorMessage);
                }
            } catch (error) {
                console.error('Error:', error);
                errorMessage.textContent = 'An error occurred. Please try again.';
                loginForm.appendChild(errorMessage);
            }
        };
    }

    // Registration functionality
    if (registerForm) {
        registerForm.onsubmit = async (e) => {
            e.preventDefault();

            // Get user input
            const username = document.getElementById('registerUsername').value;
            const password = document.getElementById('registerPassword').value;

            try {
                // Send POST request to the server
                const response = await fetch('/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        username: username,
                        password: password
                    })
                });

                const result = await response.json();

                // Check if registration was successful
                if (response.ok) {
                    alert('Registration successful! You can now log in.');
                    window.location.href = '/static/login.html'; // Redirect to the login page
                } else {
                    // Display error message
                    errorMessage.textContent = result.detail || 'Registration failed. Please try again.';
                    registerForm.appendChild(errorMessage);
                }
            } catch (error) {
                console.error('Error:', error);
                errorMessage.textContent = 'An error occurred. Please try again.';
                registerForm.appendChild(errorMessage);
            }
        };
    }
});
