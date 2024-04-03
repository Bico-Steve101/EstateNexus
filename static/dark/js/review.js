    // Get the modal
    var modal = document.getElementById("myModal");

    // Get the image and insert it inside the modal
    var img = document.getElementsByClassName("review-image");
    var modalImg = document.getElementById("img01");
    var captionText = document.getElementById("caption");
    for (var i = 0; i < img.length; i++) {
        img[i].onclick = function () {
            modal.style.display = "block";
            modalImg.src = this.src;
            modalImg.style.maxWidth = "80%"; // Set maximum width for the image
            modalImg.style.maxHeight = "80vh"; // Set maximum height for the image
            modalImg.style.marginTop = "20px"; // Add margin top to the image
            captionText.innerHTML = this.alt;
            downloadBtn.href = this.src; // Set download link to the clicked image
        }
    }

    // Get the <span> element that closes the modal
    var span = document.getElementsByClassName("close")[0];

    // Get the download button
    var downloadBtn = document.getElementById("downloadBtn");

    // When the user clicks on <span> (x), close the modal
    span.onclick = function () {
        modal.style.display = "none";
    }

    // When the user clicks anywhere outside of the modal, close it
    window.onclick = function (event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    }
    // Scroll to the bottom of the review section on page load
window.onload = function() {
    var reviewSection = document.querySelector('.review-section');
    reviewSection.scrollTop = reviewSection.scrollHeight;
}

// Scroll to the bottom of the review section whenever new content is added
function scrollToBottom() {
    var reviewSection = document.querySelector('.review-section');
    reviewSection.scrollTop = reviewSection.scrollHeight;
}
 function toggleReview(button) {
    var review = button.closest('.row');
    review.classList.toggle('collapsed');
}

function toggleCollapseAll(checkbox) {
    var reviews = document.querySelectorAll('.review-section .row');
    reviews.forEach(function(review) {
        if (checkbox.checked) {
            review.classList.add('collapsed');
        } else {
            review.classList.remove('collapsed');
        }
    });

    var label = document.querySelector('label[for="collapseAllCheckbox"]');
    if (checkbox.checked) {
        label.textContent = "Show all";
    } else {
        label.textContent = "Collapse all";
    }
}
