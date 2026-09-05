const API_URL = "http://localhost:8000";
function redirectDetails(tmdbId,mediaType){
  window.location.href = `details.html?tmdb_id=${encodeURIComponent(tmdbId)}&media_type=${mediaType}`;

}
const searchForm = document.getElementById("navSearchForm");

searchForm.addEventListener("submit", (e)=>{
  e.preventDefault();

  const query=document.getElementById("navSearchInput").value.trim();

  const mediatype = document.getElementById("navMediaType").value;

  if(!query){
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
    authLink.href = "index.html";
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
const homeSearch = document.getElementById("homeSearchForm");

homeSearch.addEventListener("submit" , (e)=>{
  e.preventDefault();
  const query = document.getElementById("homeSearchInput").value.trim();
  const mediatype = document.querySelector('input[name="media"]:checked').value;

  if(!query){
    return;
  }
  window.location.href = `browse.html?query=${encodeURIComponent(query)}&type=${mediatype}`;
})
function showToast(message){
  document.getElementById("toastMessage").textContent = message;

  const toastElement = document.getElementById("watchListToast");

  const toast = new bootstrap.Toast(toastElement);
  
  toast.show()
};
async function showDetails(tmdbId, mediaType) {
  
  
try{


  
  const response = await fetch(
    `${API_URL}/media/${tmdbId}?media_type=${mediaType}`,{
    method : "GET"}
    
    
  );
  if(!response.ok) throw new Error("Failed to fetch details");
  
  const data = await response.json();
  const modalContent = document.getElementById("modalContent");
  modalContent.replaceChildren();

  const template = document.getElementById("modalContentTemplate")
   
  const clone = template.content.cloneNode(true);

  const titleEl = clone.querySelector(".modal-movie-title");
  if (titleEl) titleEl.textContent = data.name;
  
  const posterEl = clone.querySelector(".modal-movie-poster");
  if(posterEl) posterEl.src = data.poster || 'https://via.placeholder.com/200x300';

  const ratingEl = clone.querySelector(".modal-movie-rating");
  if(ratingEl) ratingEl.textContent = `⭐ Ocena: ${data.rating || '0.0'}`;

  const release_dateEl = clone.querySelector(".modal-movie-date");
  if(release_dateEl) release_dateEl.textContent = data.release_date;

  const overviewEl = clone.querySelector(".modal-movie-overview");
  if(overviewEl) overviewEl.textContent = data.overview;
  
  const genresContainer = clone.querySelector((".modal-movie-genre"));

  if(genresContainer && Array.isArray(data.genre)){ 
    genresContainer.innerHTML ="";

    data.genre.forEach(genre => {
      const genreTag = document.createElement("span");
      genreTag.classList.add("badge","bg-primary","text-dark","fs-6","gap-3");
      genreTag.textContent = genre.name;

      genresContainer.appendChild(genreTag);

    });

  };
  
    
 
  const watchlistBtn = clone.querySelector(".modal-movie-btn");
  if(watchlistBtn){
    watchlistBtn.onclick = () =>{
      
      console.log("Dodaję element z  ID:", tmdbId);
    };
  }
  modalContent.appendChild(clone);
  
  const myModal = new bootstrap.Modal(document.getElementById("detailsModal"));

  myModal.show();

  }
  catch(error){
    console.error("Error fetching details",error)
  }
};

async function displayPopularMovies(){
    const container = document.getElementById("popularMovies");
    const template = document.getElementById("popularMoviesTemplate");

    try{
      const url = `${API_URL}/movies/popular`
      const response = await fetch(url);

      if(!response.ok){
        console.log("Error displaying popular movies");
        return;
      }
      const data = await response.json();
      const popularMovies = data.slice(0,5);
      container.innerHTML = "";
      popularMovies.forEach(item => {
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
      console.log("Something went wrong",error)
    }
};


async function displayTrendingMovies(){
  const container = document.getElementById("trendingMovies");
  
  const template = document.getElementById("trendingMoviesTemplate");
  try{
    const url= `${API_URL}/movies/trending`
    const response = await fetch(url);
    
    if(!response.ok){
      console.log("Error displaying trending movies");
      return;
    };
    const data = await response.json();
    const trendingMovies = data.slice(0,5)
    container.innerHTML ="";
    trendingMovies.forEach(item => {
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
    console.error(error);
  }

};
async function displayPopularTvShows(){
    const container = document.getElementById("popularTvShows");
    const template = document.getElementById("popularTvTemplate");

    try{
      const url = `${API_URL}/tv/popular`
      const response = await fetch(url);

      if(!response.ok){
        console.log("Error displaying popular movies");
        return;
      }
      const data = await response.json();
      const popularMovies = data.slice(0,5);
      container.innerHTML = "";
      popularMovies.forEach(item => {
        const clone = template.content.cloneNode(true);
        
        const poster = clone.querySelector(".movie-poster");
        if(poster){
          poster.src = item.poster;
        }
        const tvCard = clone.querySelector(".movie-card");
        tvCard.onclick = () => redirectDetails(item.tmdb_id,item.media_type);
        container.appendChild(clone);
      });
    }
    catch(error){
      console.log("Something went wrong",error)
    }
};
async function displayTrendingTvShows(){
    const container = document.getElementById("trendingTvShows");
    const template = document.getElementById("trendingTvTemplate");

    try{
      const url = `${API_URL}/tv/popular`
      const response = await fetch(url);

      if(!response.ok){
        console.log("Error displaying popular movies");
        return;
      }
      const data = await response.json();
      const popularMovies = data.slice(0,5);
      container.innerHTML = "";
      popularMovies.forEach(item => {
        const clone = template.content.cloneNode(true);
        
        const poster = clone.querySelector(".movie-poster");
        if(poster){
          poster.src = item.poster;
        }
        const tvCard = clone.querySelector(".movie-card");
        tvCard.onclick = () => redirectDetails(item.tmdb_id,item.media_type);
        container.appendChild(clone);
      });
    }
    catch(error){
      console.log("Something went wrong",error)
    }
};






displayTrendingMovies();
displayPopularMovies();
displayPopularTvShows();
displayTrendingTvShows();
updateNavBar();
