const token = localStorage.getItem("token");
if(!token){
    window.location.href = "index.html";
}
function displayResults(results){
    const resultsdiv = document.getElementById("results");
    resultsdiv.innerHTML ="";

    if(!results || results.length ===0 ){

        displayresultsdiv.innerHTML = "<p class=mt-3 text-danger text-center>No results found<p>";
        return;
    
    }
    results.forEach(item => {
        const div = document.createElement("div");
        div.className = "movie-card";

        const title = item.title || item.name;
        div.innerHTML = `<h1>Siema</h1>`
        div.innerHTML = `
            <h3>${title}</h3>
            <p>Release date: ${item.release_date || 'No data'}</p>
            
            <img src="${item.poster}" class="w-25 img-fluid" alt="thumbnail">
        `;
        resultsdiv.appendChild(div);
        
        
    });

};
document.getElementById("searchForm").addEventListener("submit", async function(e) {
    e.preventDefault()
    const search_query = document.getElementById("search_watchlist").value;
    const mediaTypeValue = document.querySelector('input[name="mediatype"]:checked').value;
    const url =`http://127.0.0.1:8000/search?query=${encodeURIComponent(search_query)}&media_type=${mediaTypeValue}`;
    const token = localStorage.getItem("token")
    try{
        const response = await fetch(url,{
        method : "GET",
        headers : {
            "Authorization": `Bearer ${token}`
        }
    });
    if(response.ok){
        const data = await response.json();
        
        displayResults(data);


    };
    }
    catch (error){
        console.log("Error:",error);


    }
    
});

