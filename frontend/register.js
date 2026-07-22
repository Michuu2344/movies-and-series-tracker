
document.getElementById("registerForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    const username = document.getElementById("username").value;
    const email = document.getElementById("email").value;
    const full_name = document.getElementById("full_name").value;
    const password = document.getElementById("password").value;
    
    formData = new URLSearchParams();
    formData.append("username",username);
    formData.append("email",email);
    formData.append("full_name",full_name);
    formData.append("password",password);
    
    const response = await fetch("http://127.0.0.1:8000/auth/register",{

        method : "POST",
        headers : {"Content-Type" : "application/x-www-form-urlencoded"},
        body : formData
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
