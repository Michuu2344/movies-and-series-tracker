const API_URL = "http://localhost:8000";
async function fetch_search_results(search_query, mediaTypeValue) {
  if (search_query) {
    try {
      const url = `${API_URL}/search?query=${encodeURIComponent(search_query)}&media_type=${mediaTypeValue}`;

      const response = await fetch(url, {
        method: "GET",
        
      });
      if (!response.ok) {
        throw new Error(`Błąd HTTP: ${response.status}`);
      }
      const data = await response.json();

      return data;
    } catch (error) {
      console.error("Could not fetch data", error);
    }
    return null;
  }
};
const authLink = document.getElementById("authLink");
const profileLink = document.querySelector(".profile-picture");
async function updateNavBar() {
  

  try{

  
  const url = `${API_URL}/auth/me`;
  const response = await fetch(url,{
    credentials : "include"
  })
  if(response.ok){
    authLink.textContent = "Log Out";

    authLink.href = "#";
    authLink.dataset.loggedIn = "true";
    profileLink.classList.remove("hidden");
  }
  else{
    authLink.textContent = "Sign in";

    authLink.href = "index.html"
    authLink.dataset.loggedIn = "false";
    profileLink.classList.add("hidden");

  }
} catch(error){
  console.error("Could not check authentication", error)
}

  
};
async function logout() {
  
  const url = `${API_URL}/auth/logout`
  const response = await fetch(url,{
    method : "POST",
    credentials : "include"
  });
  if(response.ok){
    authLink.dataset.loggedIn = "false";
    await updateNavBar();
  }
  

};
authLink.addEventListener("click", (e) =>{
  if(authLink.dataset.loggedIn == "true"){
    e.preventDefault();
    logout();
  }
});

function redirectDetails(tmdbId,mediaType){
  window.location.href = `details.html?tmdb_id=${encodeURIComponent(tmdbId)}&media_type=${mediaType}`;

}

async function displayResults(results, mediaTypeValue) {
  const resultsdiv = document.getElementById("results");
  resultsdiv.innerHTML = "";

  if (!results || results.length === 0) {
    resultsdiv.innerHTML =
      "<p class='text-center mt-4' style='font-size:32px;font-weight: bold;color : white;'>No results found</p>";
    return;
  }
  const template = document.getElementById("movieCardTemplate");
  if (!template) {
    console.error("No element template found");
    return;
  }
  const cleanResults = results.filter(item =>{
    return item.poster !== null && item.rating > 0;
  })
  cleanResults.forEach((item) => {
    const clone = template.content.cloneNode(true);
    clone.querySelector(".movie-title").textContent = item.name;
    clone.querySelector(".movie-date").textContent = 
      item.release_date ? item.release_date.slice(0,4) : "—";
    clone.querySelector(".movie-poster").src = item.poster;
    clone.querySelector(".movie-rating").textContent = Number(item.rating).toFixed(1);

    const badge = clone.querySelector(".movie-badge");
    badge.textContent = mediaTypeValue === "movie" ? "Movie" : "TV Series";
    clone.querySelector(".movie-row").onclick = () => redirectDetails(item.tmdb_id,mediaTypeValue);
      

    const btn = clone.querySelector(".watchlist-btn");
    if (btn) {
      btn.onclick = async (e) => {
        e.stopPropagation();
        const itemData= {
          tmdb_id : item.tmdb_id,
          media_type : mediaTypeValue,
          status : "want_to_watch",
          rating: null,
          is_favourite : false
        };
    try {
      const response = await fetch(`${API_URL}/watchlist`,{
        method : "POST",
        headers : {
          "Content-Type" : "application/json",
        },
        credentials : "include",
        body : JSON.stringify(itemData)
      });
      if(response.ok){
        btn.classList.add("added")
        btn.disabled = true;
      }
      else if(response.status === 401){
        alert("You have to log in if you want to add an item to your watchlist");
      }
      else {
        alert("Could not add an item to your watchlist");
      }
    }
    catch(error){
      console.error("Error connecting with API",error)
    };
  }
  };
    resultsdiv.append(clone);
  });
};  
document.addEventListener("DOMContentLoaded", async () => {
  const urlParams = new URLSearchParams(window.location.search);
  const browsePage = document.getElementById("browse-page");
  const resultsDiv = document.getElementById("results");


  const queryParam = urlParams.get("query");

  const mediaTypeParam = urlParams.get("type");
  if (queryParam) {

    if(browsePage){
      browsePage.style.display = "none";
      
    }
    if(resultsDiv){
      resultsDiv.style.display = "";
    }

    data = await fetch_search_results(queryParam, mediaTypeParam || "movie");
    displayResults(data, mediaTypeParam || "movie");
  }
  else {
    resultsDiv.style.display = "none";
    resultsDiv.innerHTML = "";
  }
});
updateNavBar();
const searchForm = document.getElementById("navSearchForm");
searchForm.addEventListener("submit", (e) => {
  e.preventDefault();

  const query = document.getElementById("navSearchInput").value.trim();

  const mediatype = document.getElementById("navMediaType").value;

  if (!query) {
    return;
  }
  window.location.href = `browse.html?query=${encodeURIComponent(query)}&type=${mediatype}`;
});
function displayBrowseDefault(data){

        lastItems = data.slice(0,5);
        lastItems.forEach(item => {
        const clone = template.content.cloneNode(true);
        const poster = clone.querySelector(".movie-poster");
        if(poster){
          poster.src = item.poster;
        }
        const tvCard = clone.querySelector(".poster-card");

        tvCard.onclick = () => redirectDetails(item.tmdb_id,item.media_type);
        container.appendChild(clone);
      });
};
async function loadDetails(tmdbId,mediaType) {
    currentTmdbId = tmdbId;
    currentMediaType = mediaType;
try{
    const response = await fetch(`${API_URL}/recently-viewed`,{
      method : "GET",
      credentials : "include"
    }
    );
    if(!response.ok){
        throw new Error("Failed to display details");
    }

    const data = await response.json();
    displayDetails(data,mediaType);
    if(data.trailer_key){
        openTrailerVideo(data.trailer_key);
    }
    try{
    const watchlistResponse = await fetch(`${API_URL}/watchlist/${tmdbId}?media_type=${mediaType}`,{
        method : "GET",
        credentials : "include"
    });
    if (!watchlistResponse.ok){
        throw new Error("Failed to check watchlist")
    }
    else if(watchlistResponse.status === 401) {
        updateWatchlistButton({isLoggedOut : true});
        return;
    }
    const inWatchlist = await watchlistResponse.json();
    updateWatchlistButton({isLoggedOut : false, isOnWatchlist : inWatchlist});
   } 
   catch (error) {
            console.error("Watchlist check failed:", error);
        }
}
   catch(error){
    console.error(error)
   }
};
async function displayRecentlyViewed(){
      const container = document.querySelector(".poster-section");
      const template = document.getElementById("poster-items-row");
    try{
      const url = `${API_URL}/recently-viewed`
      const response = await fetch(url,{
        method : "GET",
        credentials : "include"
    });;

      if(!response.ok){
        console.log("Error displaying recently viewed items");
        return;
      }
      const data = await response.json();
      const mostRecent = data.slice(0,5);
      container.innerHTML = "";
      mostRecent.forEach(item => {
        const clone = template.content.cloneNode(true);
        
        const poster = clone.querySelector(".movie-poster");
        if(poster){
          poster.src = item.poster;
        }
        const tvCard = clone.querySelector(".poster-card");
        tvCard.onclick = () => redirectDetails(item.tmdb_id,item.media_type);
        container.appendChild(clone);
      });
    }
    catch(error){
      console.log("Something went wrong",error)
    }
};

