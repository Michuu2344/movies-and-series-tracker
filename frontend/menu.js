

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


async function showDetails(tmdbId, mediaType) {
  
  
try{


  
  const response = await fetch(
    `http://127.0.0.1:8000/media/${tmdbId}?media_type=${mediaType}`,{
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
function displayResults(results, mediaTypeValue) {
  const resultsdiv = document.getElementById("results");
  resultsdiv.innerHTML = "";

  if (!results || results.length === 0) {
    displayresultsdiv.innerHTML =
      "<p class=' text-center mt-4'>No results found<p>";
    return;
  }
  const template = document.getElementById("movieCardTemplate");
  if(!template) {
    console.error("No element template found");
    return;
  }
  
  results.forEach((item) => {
    const clone = template.content.cloneNode(true);
    clone.querySelector(".movie-title").textContent = item.name;
    clone.querySelector(".movie-date").textContent = item.release_date;
    clone.querySelector(".movie-poster").src = item.poster;
    clone.querySelector(".movie-rating").textContent = item.rating;
    

    const badge = clone.querySelector(".movie-badge");
    badge.textContent = mediaTypeValue === "movie" ? "🎬 Movie" : "📺 TV Series";
    badge.classList.add(mediaTypeValue === "movie"? "bg-primary":"bg-success");

    const mainRow = clone.querySelector(".card-row");
    mainRow.onclick = () => showDetails(item.tmdb_id,mediaTypeValue)

    const btn = clone.querySelector(".watchlist-btn");
    if (btn) {
        btn.onclick = (e) => {
            
         

            console.log("Dodaję do bazy TMDB ID:", item.tmdb_id);
            
        };
      };

    
    resultsdiv.append(clone);
  });
};
document.getElementById("searchForm").addEventListener("submit", async function (e) {
    e.preventDefault();
    const search_query = document.getElementById("search_watchlist").value;
    
    const mediaTypeValue = document.querySelector('input[name="mediatype"]:checked').value;
    const url = `http://127.0.0.1:8000/search?query=${encodeURIComponent(search_query)}&media_type=${mediaTypeValue}`;
    try {
      const response = await fetch(url, {
        method: "GET",
        
      });
      if (response.ok) {
        const data = await response.json();

        displayResults(data, mediaTypeValue);
      }
    } catch (error) {
      console.log("Error:", error);
    }
  })
