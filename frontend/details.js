let currentTmdbId = null;
let currentMediaType = null;
let isOnWatchlist = false;
const API_URL = "http://localhost:8000";



document.addEventListener("DOMContentLoaded", async () =>{

    const urlParams = new URLSearchParams(window.location.search);

    const tmdb_id = urlParams.get("tmdb_id");

    const mediaType = urlParams.get("media_type");

    if(!tmdb_id || !mediaType){
        // document.querySelector(".details-content").style.display = "none";
        // document.querySelector("#noMovieMessage").style.display = "flex";

        return;
    
    }
    await loadDetails(tmdb_id,mediaType);

});
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
function displayMeta(data,mediaType){
    const meta = document.querySelector(".movie-meta");

    const date = mediaType === "movie" ? data.release_date : data.first_air_date;

    const year = date ? date.substring(0,4) : "Unknown";

    if(mediaType === "movie"){

        meta.innerHTML = `<div>
        <span>${year}</span>
        <span>•</span>
        <span>Movie</span>`
    }
    else{
        meta.innerHTML = `<div>
        <span>${year}</span>
        <span>•</span>
        <span>TV Series</span>
        <span>•</span>
        <span>${data.number_of_seasons} Seasons</span>
        </div>`
    }
}
function openTrailerVideo(trailerKey){
    const trailerButton = document.getElementById("trailer-button");
    const backdropImage = document.getElementById("backdrop-image");
    const trailerIframe = document.getElementById("trailer-iframe");

    trailerButton.addEventListener("click", (e) => {
        e.preventDefault();
        backdropImage.style.display = "none";
        trailerButton.style.display = "none";

        trailerIframe.src = `https://www.youtube.com/embed/${trailerKey}?autoplay=1`;
        trailerIframe.style.display = "block";
    });
};

function detailsSection(data,mediaType){
    const infoGridContainer = document.querySelector(".info-grid");

    if(mediaType === "movie"){
        infoGridContainer.innerHTML = `<div class="info-item">
            <span>Release date</span>
            <strong>${data.release_date}</strong>
        </div>

        <div class="info-item">
            <span>Runtime in minutes</span>
            <strong>${data.runtime}</strong>
        </div>

        <div class="info-item">
            <span>Country</span>
            <strong>${data.origin_country}</strong>
        </div>

      <div class="info-item">
            <span>Language</span>
            <strong>${data.original_language}</strong>
        </div>`;
    }
    else{
        infoGridContainer.innerHTML = `<div class="info-item">
            <span>First air date</span>
            <strong>${data.first_air_date}</strong>
        </div>
        <div class="info-item">
            <span>Last air date</span>
            <strong>${data.last_air_date}</strong>
        </div>

        <div class="info-item">
            <span>Country</span>
            <strong>${data.origin_country}</strong>
        </div>

      <div class="info-item">
            <span>Original Language</span>
            <strong>${data.original_language}</strong>
        </div>`;
    }

}
function displayCredits(data,mediaType){
    const stars = data.most_popular_cast_members;
    
    const creators = mediaType === "movie"
    ? data.crew || []
    : data.created_by || [];
    const credits = document.querySelector(".credits")
    credits.innerHTML = "";
    
    const creatorsSection = document.createElement("div");
    
    creatorsSection.classList.add("credit-section");
    if(mediaType ==="movie"){
        creatorsSection.innerHTML = `<strong>Most popular crew members</strong>`;
    }
    else{
        creatorsSection.innerHTML = `<strong>Created by</strong>`;
    }
    

    const creatorsList = document.createElement("div");
    creatorsList.classList.add("credits-list");

    creators.forEach(creator =>{
        const creditItem = document.createElement("div");
        creditItem.classList.add("credit-item");
        
        creditItem.innerHTML =
        `<span>${creator.name}</span>`;

        creatorsList.appendChild(creditItem);



        });
    creatorsSection.appendChild(creatorsList);
    credits.appendChild(creatorsSection);
        
    const starsSection = document.createElement("div");
    starsSection.classList.add("credits-section");
    starsSection.innerHTML = `<strong>Actors</strong>`;

    const starsList = document.createElement("div");
    starsList.classList.add("credits-list");
    

    stars.forEach(star => {
        const creditStars = document.createElement("div");
        creditStars.classList.add("credit-item");
        creditStars.innerHTML =`
            <span>${star.name}</span>`;
        starsList.appendChild(creditStars);
    });
    starsSection.appendChild(starsList);
    credits.appendChild(starsSection);
    


};

async function displayRecommendations(tmdb_id,media_type){
    const container = document.getElementById("recommendationsContainer");
    const template = document.getElementById("RecommendationsTemplate");

    try{
      const url = `${API_URL}/recommendations?tmdb_id=${tmdb_id}&media_type=${media_type}`;
      const response = await fetch(url,{
        method : "GET"
      });

      if(!response.ok){
        console.log("Error displaying recommendations");
        return;
      }
      const data = await response.json();
      const recommendations = data.slice(0,5);
      container.innerHTML = "";
      recommendations.forEach(item => {
        const clone = template.content.cloneNode(true);
        
        const poster = clone.querySelector(".movie-poster");
        if(poster){
          poster.src = item.poster;
        }
        const movieCard = clone.querySelector(".movie-card");
        movieCard.onclick = () => redirectDetails(item.tmdb_id,item.media_type);
        container.appendChild(clone);
      });
    }
    catch(error){
      console.log("Something went wrong",error);
    }
};



async function loadDetails(tmdbId,mediaType) {
    currentTmdbId = tmdbId;
    currentMediaType = mediaType;
try{
    const response = await fetch(`${API_URL}/media/${tmdbId}?media_type=${mediaType}`,
        {method : "GET"}
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

    const watchlistStatus = await watchlistResponse.json();
    updateWatchlistButton(watchlistStatus);
   } 
   catch (error) {
            console.error("Watchlist check failed:", error);
        }
}
   catch(error){
    console.error(error)
   }
};
function displayDetails(data,mediaType){
    
    const year = mediaType === "movie" ? data.release_date : data.first_air_date;
    
    document.querySelector(".movie-title").textContent = data.name;
    const genres = data.genre;
    displayMeta(data,mediaType);

    document.querySelector(".rating-tmdb-value").textContent = data.rating;
    
    document.querySelector(".details-poster").src = data.poster;
    document.querySelector(".details-backdrop").src = data.backdrop;
    document.querySelector(".overview").textContent = data.overview;
    const genresContainer = document.querySelector(".genres");
    genresContainer.innerHTML = "";
    genres.forEach(genre => {
        const span = document.createElement("span");
        span.classList.add("genre");
        span.textContent = genre.name;
        genresContainer.appendChild(span);
        
    });



    detailsSection(data,mediaType);
    displayCredits(data,mediaType);
    displayRecommendations(data.tmdb_id,mediaType);
};
function updateWatchlistButton(value){
    isOnWatchlist = value;
    const button = document.getElementById("watchlist-button");
    if(isOnWatchlist){
        button.textContent = "✓ In Watchlist";
        button.classList.add("in-watchlist");
    }
    else{
        button.textContent = "＋ Add to Watchlist";
        button.classList.remove("in-watchlist");

    }

};
async function handleWatchlistClick(){

    try{
    if(isOnWatchlist){
        const response = await fetch(`${API_URL}/watchlist/${currentTmdbId}?media_type=${currentMediaType}`,{
        method : "DELETE",
        credentials : "include"});
        
        if(!response.ok){
            throw new Error("Failed to remove item from the watchlist");
        }
        updateWatchlistButton(false);
    } else{
        const itemData= {
          tmdb_id : currentTmdbId ,
          media_type : currentMediaType,
          status : "want_to_watch",
          rating : null
        }
        
        const response = await fetch(`${API_URL}/watchlist`,{
        method : "POST",
        headers : {
            "Content-Type" : "application/json"
          },
        credentials : "include",
        body : JSON.stringify(itemData)},);

        if(!response.ok){
            throw new Error("Failed to add item to the watchlist");
        }

        updateWatchlistButton(true);
        
        console.log("Updated");
    }
    }  catch (error) {

        console.error(error);
    }
};
document
    .getElementById("watchlist-button")
    .addEventListener("click",handleWatchlistClick);

updateNavBar();