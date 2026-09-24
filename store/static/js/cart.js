// ================= OPEN / CLOSE CART =================
function openCart() {
    const cartDrawer = document.getElementById("cartDrawer");
    const cartOverlay = document.getElementById("cartOverlay");

    cartDrawer.classList.remove("translate-x-full");
    cartOverlay.classList.remove("opacity-0", "invisible");
    document.body.classList.add("overflow-hidden");
}

function closeCart() {
    const cartDrawer = document.getElementById("cartDrawer");
    const cartOverlay = document.getElementById("cartOverlay");

    cartDrawer.classList.add("translate-x-full");
    cartOverlay.classList.add("opacity-0", "invisible");
    document.body.classList.remove("overflow-hidden");
}

// ================= ADD TO CART =================
document.addEventListener("click", function (e) {
    let button = e.target.closest(".add-to-cart-btn");
    if (button) {
        console.log("CLICK DETECTED");
        let productId = button.dataset.product;
        console.log("Product ID:", productId);

        fetch(`/cart/add/${productId}/`, {
            method: "POST",
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
                "Content-Type": "application/json"
            }
        })
            .then(res => res.json())
            .then(data => {
                console.log("RESPONSE:", data);
                let cartCount = document.querySelector("#cart-count");
                cartCount.innerText = data.cart_count;
                console.log("ELEMENT:", cartCount);
                if (!cartCount) {
                    console.error("Cart count element not found!");
                    return;
                }
                if (data.cart_count > 0) {
                    cartCount.innerText = data.cart_count;
                    cartCount.style.display = "flex";
                } else {
                    cartCount.style.display = "none";
                }


                if (data.status === "success") {
                    document.querySelector("#cart-count").innerText = data.cart_count;
                    let cartContainer = document.getElementById("cartItems");
                    let existingItem = document.getElementById(`cart-item-${data.product_id}`);
                    if (existingItem) {
                        existingItem.querySelector(".quantity").innerText = data.quantity;
                    } else {
                        let itemHTML = `
            <div id="cart-item-${data.product_id}" class="flex gap-4 items-center border-b pb-4">

                <img src="${data.image}" class="w-16 h-16 object-cover rounded">

                <div class="flex-1">
                    <h4 class="text-sm text-[#4c5d7d] font-semibold">${data.name}</h4>
                    <p class="text-[#4c5d7d]">₹${data.price}</p>

                    <div class="flex gap-2 mt-2">
                        <button class="decrement text-[#4c5d7d] border px-2" data-product="${data.product_id}">-</button>
                        <span class="quantity text-[#4c5d7d]">${data.quantity}</span>
                        <button class="increment text-[#4c5d7d] border px-2" data-product="${data.product_id}">+</button>
                    </div>
                </div>

                <button class="remove-item text-red-500" data-product="${data.product_id}">
                    Remove
                </button>
            </div>
            `;

                        cartContainer.insertAdjacentHTML("afterbegin", itemHTML);
                    }

                    openCart();
                }
            });
    }
});

// ================= UPDATE QUANTITY =================
document.addEventListener("DOMContentLoaded", function () {
document.addEventListener("click", function (e) {

    let incBtn = e.target.closest(".increment");
    let decBtn = e.target.closest(".decrement");

    if (incBtn || decBtn) {

        let productId = (incBtn || decBtn).dataset.product;
        let action = incBtn ? "increase" : "decrease";

        fetch(`/cart/update/`, {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: `product_id=${productId}&action=${action}`
        })
            .then(res => res.json())
            .then(data => {

                // ❌ If removed
                if (data.removed) {
                    document.getElementById(`cart-item-${productId}`).remove();
                } else {
                    // ✅ Update quantity
                    document.querySelector(`#cart-item-${productId} .quantity`).innerText = data.quantity;

                    // ✅ Update item total
                    document.querySelector(`#cart-item-${productId} .item-total`).innerText = data.item_total;
                }

                // ✅ Update subtotal
                document.getElementById("cart-subtotal").innerText = "₹" + data.cart_subtotal;

                // ✅ Update cart count
                let cartCount = document.getElementById("cart-count");

                if (data.cart_count > 0) {
                    cartCount.innerText = data.cart_count;
                    cartCount.style.display = "flex";
                } else {
                    cartCount.style.display = "none";
                }
            });
    }
});
});
// ================= REMOVE ITEM =================
document.addEventListener("click", function (e) {
    let button = e.target.closest(".remove-item");
    if (button) {
        let productId = button.dataset.product;
        console.log("REMOVE PRODUCT:", productId);
        fetch("/remove-from-cart/", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded",
                "X-CSRFToken": getCookie("csrftoken")
            },
            body: `product_id=${productId}`
        })
            .then(res => res.json())
            .then(data => {
                console.log("REMOVE RESPONSE:", data);

                if (data.status === "success") {

                    // ✅ Remove item
                    document.getElementById(`cart-item-${productId}`).remove();
                    document.getElementById("cart-subtotal").innerText =
                        "₹" + data.cart_subtotal;
                    let cartCount = document.querySelector("#cart-count");

                    if (data.cart_count > 0) {
                        cartCount.innerText = data.cart_count;
                        cartCount.style.display = "flex";   // show badge
                    } else {
                        cartCount.style.display = "none";   // hide badge
                    }
                }
            });
    }
});

// ================= CSRF TOKEN =================
function getCookie(name) {
    let cookieValue = null;

    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");

        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();

            if (cookie.substring(0, name.length + 1) === (name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }

    return cookieValue;
}