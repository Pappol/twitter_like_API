document.getElementById('registerForm').addEventListener('submit', function(event) {
    event.preventDefault();
    let username = document.getElementById('registerUsername').value;
    let password = document.getElementById('registerPassword').value;
    registerUser(username, password);
});

document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault();
    let username = document.getElementById('loginUsername').value;
    let password = document.getElementById('loginPassword').value;
    loginUser(username, password);
});

function registerUser(username, password) {
    fetch('http://localhost:8000/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            username: username,
            password: password
        })
    })
    .then(response => response.json())
    .then(data => alert('Registration successful!'))
    .catch((error) => {
        console.error('Error:', error);
        alert('Registration failed!');
    });
}

function loginUser(username, password) {
    fetch('http://localhost:8000/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            username: username,
            password: password
        })
    })
    .then(response => response.json())
    .then(data => alert('Login successful!'))
    .catch((error) => {
        console.error('Error:', error);
        alert('Login failed!');
    });
}
