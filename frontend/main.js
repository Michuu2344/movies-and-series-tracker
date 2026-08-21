const API_URL = "http://localhost:8000";
document
  .getElementById("loginForm")
  .addEventListener("submit", async function (e) {
    e.preventDefault();

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const formData = new URLSearchParams();
    formData.append("username", username);
    formData.append("password", password);

    const response = await fetch(`${API_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      credentials: "include",
      body: formData,
    });
    if (response.ok) {
      const data = await response.json();
      document.getElementById("message").textContent = "Successfully logged in";

      window.location.href = "menu.html";
    } else {
      document.getElementById("message").textContent =
        "Wrong username or password";
    }
  });
