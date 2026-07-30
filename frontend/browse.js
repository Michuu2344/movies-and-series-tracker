async function fetch_search_results(search_query, mediaTypeValue) {
  if (search_query) {
    try {
      const url = `http://127.0.0.1:8000/search?query=${encodeURIComponent(search_query)}&media_type=${mediaTypeValue}`;

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
}
async function showDetails(tmdbId, mediaType) {
  try {
    const response = await fetch(
      `http://127.0.0.1:8000/media/${tmdbId}?media_type=${mediaType}`,
      {
        method: "GET",
      },
    );
    if (!response.ok) throw new Error("Failed to fetch details");

    const data = await response.json();
    const modalContent = document.getElementById("modalContent");
    modalContent.replaceChildren();

    const template = document.getElementById("modalContentTemplate");

    const clone = template.content.cloneNode(true);

    const titleEl = clone.querySelector(".modal-movie-title");
    if (titleEl) titleEl.textContent = data.name;

    const posterEl = clone.querySelector(".modal-movie-poster");
    if (posterEl)
      posterEl.src = data.poster || "https://via.placeholder.com/200x300";

    const ratingEl = clone.querySelector(".modal-movie-rating");
    if (ratingEl) ratingEl.textContent = `⭐ Rating: ${data.rating || "0.0"}`;

    const release_dateEl = clone.querySelector(".modal-movie-date");
    if (release_dateEl) release_dateEl.textContent = data.release_date;

    const overviewEl = clone.querySelector(".modal-movie-overview");
    if (overviewEl) overviewEl.textContent = data.overview;

    const genresContainer = clone.querySelector(".modal-movie-genre");

    if (genresContainer && Array.isArray(data.genre)) {
      genresContainer.innerHTML = "";

      data.genre.forEach((genre) => {
        const genreTag = document.createElement("span");
        genreTag.classList.add(
          "badge",
          "bg-primary",
          "text-dark",
          "fs-6",
          "gap-3",
        );
        genreTag.textContent = genre.name;

        genresContainer.appendChild(genreTag);
      });
    }

    const watchlistBtn = clone.querySelector(".modal-movie-btn");
    if (watchlistBtn) {
      watchlistBtn.onclick = async (e) => {
        e.preventDefault();
        
        const itemData= {
          tmdb_id : tmdbId ,
          media_type : mediaTypeValue,
          status : "want_to_watch",
          rating : null
        }
        const response = await fetch("http://127.0.0.1:8000/watchlist",{
          method : "POST",
          headers : {
            "Content-Type" : "application/json"
          },
          credentials : "include",
          body : JSON.stringify(itemData)
        });
        if(response.ok){
          btn.textContent = "✓ Added an item to watchlist";
          btn.classList.remove("btn-warning");
          btn.classList.add("btn-success");
          btn.disabled = true;
        }
        else if(response.status === 401){
          alert("You have to log in if you want to add an item to your watchlist");
        }
        else{
          alert("Could not add an item to your watchlist");
        }
      };
    };
    modalContent.appendChild(clone);

    const myModal = new bootstrap.Modal(
      document.getElementById("detailsModal"),
    );

    myModal.show();
  } catch (error) {
    console.error("Error fetching details", error);
  }
}
function displayResults(results, mediaTypeValue) {
  const resultsdiv = document.getElementById("results");
  resultsdiv.innerHTML = "";

  if (!results || results.length === 0) {
    resultsdiv.innerHTML =
      "<p class='text-center mt-4'>No results found</p>";
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
    clone.querySelector(".movie-date").textContent = item.release_date;
    clone.querySelector(".movie-poster").src = item.poster;
    clone.querySelector(".movie-rating").textContent = item.rating;

    const badge = clone.querySelector(".movie-badge");
    badge.textContent =
      mediaTypeValue === "movie" ? "🎬 Movie" : "📺 TV Series";
    badge.classList.add(
      mediaTypeValue === "movie" ? "bg-primary" : "bg-success",
    );

    const mainRow = clone.querySelector(".card-row");
    mainRow.onclick = () => showDetails(item.tmdb_id, mediaTypeValue);

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
      const response = await fetch("http://127.0.0.1:8000/watchlist",{
        method : "POST",
        headers : {
          "Content-Type" : "application/json",
        },
        credentials : "include",
        body : JSON.stringify(itemData)
      });
      if(response.ok){
        btn.textContent = "✓";
        btn.classList.remove("btn-primary");
        btn.classList.add("btn-success");
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

  const queryParam = urlParams.get("query");

  const mediaTypeParam = urlParams.get("type");
  if (queryParam) {
    data = await fetch_search_results(queryParam, mediaTypeParam || "movie");
    displayResults(data, mediaTypeParam || "movie");
  }
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
