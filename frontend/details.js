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
function detailsSection(data,mediaType){
    const infoGridContainer = document.querySelector(".info-grid");

    if(mediaType === "movie"){
        infoGridContainer.innerHTML = `<div class="info-item">
            <span>Release date</span>
            <strong>${data.release_date}</strong>
        </div>

        <div class="info-item">
            <span>Runtime</span>
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

    const stars = data.most_popular_cast_members || [];
    const creators = data.created_by;
    const credits = document.querySelector(".credits")
    credits.innerHTML = "";
    
    const creatorsSection = document.createElement("div");
    creatorsSection.classList.add("credit-section");
    creatorsSection.innerHTML = `<strong>Created by</strong>`;

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
};




async function loadDetails(tmdbId,mediaType) {
    
try{
    const response = await fetch(`${API_URL}/media/${tmdbId}?media_type=${mediaType}`,
        {method : "GET"}
    );
    if(!response.ok){
        throw new Error("Failed to display details");
    }
    const data = await response.json();
    displayDetails(data,mediaType);


   } 
   catch(error){
    console.error(error)
   }
}