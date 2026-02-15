// Order Form
document.getElementById("orderForm").addEventListener("submit", function(e) {
  e.preventDefault();
  document.getElementById("successMessage").classList.remove("hidden");
  this.reset();
});

// Reviews
const reviewForm = document.getElementById("reviewForm");
const reviewList = document.getElementById("reviewList");

reviewForm.addEventListener("submit", function(e) {
  e.preventDefault();

  const name = document.getElementById("reviewName").value;
  const text = document.getElementById("reviewText").value;
  const rating = document.getElementById("reviewRating").value;

  const reviewDiv = document.createElement("div");
  reviewDiv.innerHTML = `
    <p><strong>${name}</strong> (${rating}⭐)</p>
    <p>${text}</p>
    <hr>
  `;

  reviewList.prepend(reviewDiv);
  reviewForm.reset();
});
