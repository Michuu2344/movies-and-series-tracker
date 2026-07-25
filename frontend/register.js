
document.getElementById("registerForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    
    
    const payload = {
        username : document.getElementById("username").value,
        email: document.getElementById("email").value,
        full_name: document.getElementById("fullname").value,
        password :  document.getElementById("password").value
    };


    const response = await fetch("http://127.0.0.1:8000/auth/register",{

        method : "POST",
        headers : {"Content-Type" : "application/json"},
        body : JSON.stringify(payload)
});
   if(response.ok){
    data = await response.json();
    localStorage.setItem("token",data.access_token);
    window.location.href = "menu.html";

   }
   else{
    document.getElementById("message").textContent = "The registration was not successfull";
   }

});
