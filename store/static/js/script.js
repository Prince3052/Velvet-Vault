window.addEventListener("load", function () {
  const skeleton = document.querySelector("#skeleton-loader");
  const products_grid = document.querySelector("#product-container");

  // Hide skeleton after page fully loads
  skeleton.classList.add('hidden');
  products_grid.classList.remove("hidden");


  const searchIcon = document.getElementById("searchIcon");
  const searchPopup = document.querySelector("#searchPopup");
  const closeSearch = document.getElementById("closeSearch");
  const searchInput = document.getElementById("searchInput");
  const searchResults = document.getElementById("searchResults");
  const searchBox = document.getElementById("searchBox");
  let pageBody = document.body;
  // Open popup
  searchIcon.addEventListener("click", () => {
    searchPopup.classList.remove("hidden");
    searchPopup.classList.add("flex");
    pageBody.style.overflow = 'hidden';
  });

  // Close only when clicking outside
  searchPopup.addEventListener("click", () => {
    searchPopup.classList.add("hidden");
    pageBody.style.overflow = 'scroll';
  });

  // 🚀 IMPORTANT: stop closing when clicking inside
  searchBox.addEventListener("click", (e) => {
    e.stopPropagation();
  });

  // Fetch search results
  searchInput.addEventListener("input", async () => {
    let query = searchInput.value;

    if (query.length === 0) {
      searchResults.innerHTML = "";
      return;
    }

    let res = await fetch(`/search/?q=${query}`);
    let data = await res.json();

    if (data.length === 0) {
      searchResults.innerHTML = "<p class='text-[#4c5d7d]'>No products found</p>";
      return;
    }

    searchResults.innerHTML = data.map(product => `
    <div class="flex items-center gap-3 border p-2 rounded-lg hover:bg-gray-100 cursor-pointer" onclick="window.location.href='/product/${product.slug}/'">
      
      <img src="${product.image}" class="w-12 h-12 object-cover rounded">

      <div>
        <h4 class="font-semibold text-[#4c5d7d]">${product.name}</h4>
        <p class="text-sm text-gray-600">₹${product.price}</p>
      </div>

    </div>
  `).join("");
  });

  let timeout;

  searchInput.addEventListener("input", () => {
    clearTimeout(timeout);

    timeout = setTimeout(() => {
      fetchResults();
    }, 300);
  });
});

const btn = document.getElementById("payBtn");

var options = {
    key: btn.dataset.key,
    amount: btn.dataset.amount,
    currency: "INR",
    name: "Velvet Vault",
    description: btn.dataset.name,
    order_id: btn.dataset.order,

    handler: function (response){
        console.log(response);
    }
};
