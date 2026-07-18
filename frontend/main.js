document.getElementById("loginForm").addEventListener("submit",async function(e){
    e.preventDefault();

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;
    
    formData = new URLSearchParams();
    formData.append("username",username);
    formData.append("password",password);   

    const response = await fetch("http://127.0.0.1:8000/auth/login",
        {method : "POST",
        headers : {"Content-Type": "application/x-www-form-urlencoded"},
        body : formData
        });
    if(response.ok){
        const data = await response.json();
        localStorage.setItem("token",data.access_token);
        document.getElementById("message").textContent = "Successfully logged in";

        window.location.href = "watchlist.html";
    }
    else{
        document.getElementById("message").textContent = "Wrong username or password";
    }

});
