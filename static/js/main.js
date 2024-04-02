(function ($) {
    "use strict";

    // Spinner
    var spinner = function () {
        setTimeout(function () {
            if ($('#spinner').length > 0) {
                $('#spinner').removeClass('show');
            }
        }, 1);
    };
    spinner(0);

    // Function to auto-swipe the slides
    function autoSwipe() {
        // Get the width of a single slide
        var slideWidth = $('.blog-slide').outerWidth();

        // Function to show the next slide
        function showNextSlide() {
            // Get the current position of the wrapper
            var currentPosition = parseInt($('.swiper-wrapper').css('left'));

            // Calculate the new position
            var newPosition = currentPosition - slideWidth;

            // Animate the transition to the new position
            $('.swiper-wrapper').animate({
                left: newPosition + 'px'
            }, 500, function () {
                // After animation, move the first slide to the end
                $('.blog-slide:first-child').appendTo('.swiper-wrapper');
                // Reset the position of the wrapper
                $('.swiper-wrapper').css('left', '0');
            });
        }

        // Start auto-swiping
        setInterval(showNextSlide, 5000); // 5000 milliseconds = 5 seconds
    }

    // Call autoSwipe function when the page is loaded
    window.onload = autoSwipe;

    // Fixed Navbar
    $(window).scroll(function () {
        if ($(window).width() < 992) {
            if ($(this).scrollTop() > 55) {
                $('.fixed-top').addClass('shadow');
            } else {
                $('.fixed-top').removeClass('shadow');
            }
        } else {
            if ($(this).scrollTop() > 55) {
                $('.fixed-top').addClass('shadow').css('top', -55);
            } else {
                $('.fixed-top').removeClass('shadow').css('top', 0);
            }
        }
    });


    // Back to top button
    $(window).scroll(function () {
        if ($(this).scrollTop() > 300) {
            $('.back-to-top').fadeIn('slow');
        } else {
            $('.back-to-top').fadeOut('slow');
        }
    });
    $('.back-to-top').click(function () {
        $('html, body').animate({
            scrollTop: 0
        }, 1500, 'easeInOutExpo');
        return false;
    });


    // Testimonial carousel
    $(".testimonial-carousel").owlCarousel({
        autoplay: true,
        smartSpeed: 2000,
        center: false,
        dots: true,
        loop: true,
        margin: 25,
        nav: true,
        navText: [
            '<i class="bi bi-arrow-left"></i>',
            '<i class="bi bi-arrow-right"></i>'
        ],
        responsiveClass: true,
        responsive: {
            0: {
                items: 1
            },
            576: {
                items: 1
            },
            768: {
                items: 1
            },
            992: {
                items: 2
            },
            1200: {
                items: 2
            }
        }
    });


    // vegetable carousel
    $(".vegetable-carousel").owlCarousel({
        autoplay: true,
        smartSpeed: 1500,
        center: false,
        dots: true,
        loop: true,
        margin: 25,
        nav: true,
        navText: [
            '<i class="bi bi-arrow-left"></i>',
            '<i class="bi bi-arrow-right"></i>'
        ],
        responsiveClass: true,
        responsive: {
            0: {
                items: 1
            },
            576: {
                items: 1
            },
            768: {
                items: 2
            },
            992: {
                items: 3
            },
            1200: {
                items: 4
            }
        }
    });


    // Modal Video
    $(document).ready(function () {
        var $videoSrc;
        $('.btn-play').click(function () {
            $videoSrc = $(this).data("src");
        });
        console.log($videoSrc);

        $('#videoModal').on('shown.bs.modal', function (e) {
            $("#video").attr('src', $videoSrc + "?autoplay=1&amp;modestbranding=1&amp;showinfo=0");
        })

        $('#videoModal').on('hide.bs.modal', function (e) {
            $("#video").attr('src', $videoSrc);
        })
    });

    // FAQ Blocks
    document.addEventListener("DOMContentLoaded", function () {
        var faqBlocks = document.querySelectorAll(".faq-block");

        // Loop through each faq block
        faqBlocks.forEach(function (faqBlock) {
            var faqContent = faqBlock.querySelector(".faq-content");
            var plusIcon = faqBlock.querySelector(".plus-icon");

            // Add click event listener to toggle faq content visibility
            faqBlock.addEventListener("click", function () {
                faqContent.classList.toggle("open");
                // Rotate the plus icon
                plusIcon.classList.toggle("rotate");
            });
        });
    });

})(jQuery);
