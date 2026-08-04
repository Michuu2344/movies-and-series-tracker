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

function showToast(message){
  document.getElementById("toastMessage").textContent = message;

  const toastElement = document.getElementById("watchListToast");

  const toast = new bootstrap.Toast(toastElement);
  
  toast.show()
};
async function addItemToFavourites(tmdbId,mediaType) {
    try{
    
    const response  = await fetch(
      `http://127.0.0.1:8000/watchlist/${tmdbId}/favourites?media_type=${mediaType}`,
      {
        method: "PATCH",
        credentials: "include",
        headers : {
          "Content-Type":"application/json"
        },
      },
    );
    const message = "Added to favourites";
    if(!response.ok){
      showToast("We could not add this item to favourites");
      return;
    }
    showToast(message)
  }
  catch(error){
    showToast("We could not add this item to favourites");
    console.error("Error favourites update",error);
  }
};
async function updateStatus(status,tmdb_id,media_type){
  try{
    statusData = { 
      "status": status
    }
    const response  = await fetch(
      `http://127.0.0.1:8000/watchlist/${tmdb_id}?media_type=${media_type}`,
      {
        method: "PATCH",
        credentials: "include",
        headers : {
          "Content-Type":"application/json"
        },
        body : JSON.stringify(statusData)
      },
    );
    message = "Status updated";
    if(!response.ok){
      showToast("We could not update item status");
    }
    showToast("Status updated")
  }
  catch(error){
    showToast("We could not update item status");
    console.error("Error status update",error);
  }
};

async function removeFromWatchlist(tmdb_id, media_type = "movie") {
  try {
    const response = await fetch(
      `http://127.0.0.1:8000/watchlist/${tmdb_id}?media_type=${media_type}`,
      {
        method: "DELETE",
        credentials: "include",
      },
    );

    if (response.ok) {
      console.log("Successfully deleted an item from watchlist");
      loadWatchlist();
    } else {
      console.error("Error deleting an item", response.status);
    }
  } catch (error) {
    console.error("Network error", error);
  }
};
async function loadWatchlist() {
  const container = document.getElementById("results");
  const template = document.getElementById("movieCardTemplate");

  container.innerHTML =
    "<p class='text-center fs-5'>Ładowanie watchlisty...</p>";

  try {
    const response = await fetch("http://127.0.0.1:8000/watchlist", {
      method: "GET",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
    });
    if (response.status === 401) {
      container.innerHTML = `<div class="alert alert-warning text-center">
         You have to log in to view your watchlist
        </div>`;
      return;
    }
    if (!response.ok) {
      throw new Error("Error loading the watchlist");
    }
    const watchlist = await response.json();
    container.innerHTML = "";
    if (watchlist.length === 0) {
      container.innerHTML = `
        <div class="text-center mt-5">
          <h3 class="text-muted">Twoja watchlista jest pusta!</h3>
          <p>Dodaj jakieś filmy lub seriale, aby wyświetlić je w tym miejscu.</p>
        </div>`;
      return;
    }
    watchlist.forEach((item) => {
      const clone = template.content.cloneNode(true);
      const poster = clone.querySelector(".movie-poster");
      if (poster) {
        poster.src = item.poster_url
          ? item.poster_url
          : "https://via.placeholder.com/150x225?text=Brak+Plakatu";
        poster.alt = item.name;
      }

      const name = clone.querySelector(".movie-title");
      if (name) {
        name.textContent = item.title;
      }
      const release_date = clone.querySelector(".movie-date");
      if (release_date) {
        release_date.textContent = item.year;
      }

      const badge = clone.querySelector(".movie-badge");
      if (badge) {
        badge.textContent =
          item.media_type === "movie" ? "🎬 Movie" : "📺 TV Series";
      }
      const rating = clone.querySelector(".movie-rating");
      if (rating) {
        rating.textContent = item.rating;
      }
      
      const statusButton= clone.querySelector(".status-button")

      if(statusButton && item.status){
        labels = {
          watching : "Watching",
          completed : "Completed",
          want_to_watch : "Want to watch",
          dropped : "Dropped"
        };
        statusButton.textContent = labels[item.status];

        statusButton.dataset.currentStatus = item.status;
      }; 
      
      const statusLinks = clone.querySelectorAll(".status-item")

      statusLinks.forEach((link)=> {

        link.addEventListener("click", async (e) => {
          e.preventDefault();
          e.stopPropagation();

          const newStatus = link.dataset.status;
          const newStatusText = link.textContent.trim();

          statusButton.textContent = newStatusText;


          statusButton.dataset.currentStatus = newStatus;
          updateStatus(newStatus,item.tmdb_id,item.media_type);
        });
      
      });

      const removeBtn = clone.querySelector(".watchlist-remove-btn");
      removeBtn.onclick = async (e) => {
        e.stopPropagation();
        removeFromWatchlist(item.tmdb_id,item.media_type);
        message = "Removed from watchlist."
        showToast(message);
      };
      const favBtn = clone.querySelector(".watchlist-favourite-btn");
      favBtn.onclick = async (e) => {
        e.stopPropagation();
        
        addItemToFavourites(item.tmdb_id,item.media_type);
        console.log(".")
      }


      container.appendChild(clone);
    });
  } catch (error) {
    console.error("Error", error);
  }
}
loadWatchlist();

