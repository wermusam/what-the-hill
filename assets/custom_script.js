// assets/custom_script.js

console.log("Custom script loaded");

document.addEventListener('DOMContentLoaded', function () {
    console.log("DOM fully loaded and parsed");

    // Retry logic to wait for the nav links to appear
    const maxRetries = 10;  // Maximum number of retries
    let retries = 0;

    function findNavLinks() {
        const navLinks = document.querySelectorAll('a[href^="#"]');
        console.log(`Found nav links (attempt ${retries + 1}):`, navLinks);
        if (navLinks.length > 0) {

            // If links are found, set up click events
            navLinks.forEach(link => {

                console.log("Adding click event for:", link.href);  // Log the href attribute
                link.addEventListener('click', function (event) {
                    event.preventDefault();
                    console.log("Click event triggered for:", link.href);  // Log on click
                    const targetId = this.getAttribute('href');  // Get the target ID
                    const targetElement = document.querySelector(targetId);
                    if (targetElement) {
                        console.log("Found target:", targetElement);
                        
                        // Scroll to the target smoothly
                        setTimeout(() => {
                            console.log("Attempting to scroll to:", targetId);
                            targetElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
                            console.log("Scrolled to:", targetId);
                        }, 200);  // 200ms delay
                        window.history.pushState(null, null, targetId);
                    } else {
                        console.log("Target element not found for:", targetId);
                    }
                });
            });
        } else if (retries < maxRetries) {
            retries++;
            console.log("Retrying to find nav links...");
            setTimeout(findNavLinks, 200);  // Retry after 200ms
        } else {
            console.error("Failed to find nav links after retries.");
        }
    }
    // Initial call to find nav links
    findNavLinks();
});