document.addEventListener('DOMContentLoaded', () => {
    const isMobile = navigator.userAgentData.mobile;
    // Ensure the mobile menu is hidden initially
    if (!isMobile) {
        document.getElementById("mobile-menu").remove();
    } else {
        document.getElementById("desktop-menu").remove();  
        
        const hamburgerMenu = document.querySelector(".hamburger-menu");
        const nav = document.querySelector(".nav");

        var active = false;

        hamburgerMenu.addEventListener("click", () => {
            nav.classList.toggle("active");
            active = !active;
            if (active) {
            hamburgerMenu.classList.add("icon-white");
            } else {
            hamburgerMenu.classList.remove("icon-white");
            }
        });
    }

    Element.prototype.remove = function() {
        this.parentElement.removeChild(this);
    }
    NodeList.prototype.remove = HTMLCollection.prototype.remove = function() {
        for(var i = this.length - 1; i >= 0; i--) {
            if(this[i] && this[i].parentElement) {
                this[i].parentElement.removeChild(this[i]);
            }
        }
    }
});