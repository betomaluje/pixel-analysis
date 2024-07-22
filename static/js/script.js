document.addEventListener('DOMContentLoaded', () => {
    const isMobile = navigator.userAgentData.mobile;
    // Ensure the mobile menu is hidden initially
    if (isMobile) {        
        $(".hamburger-menu").click(function() {
            $('#nav-mobile').toggleClass("active");
            $(".hamburger-menu").toggleClass("icon-white");
        });
    }
});