const nav_links = document.querySelectorAll(".side-menu-item");
const page_info = document.querySelector(".page-info");
const page_settings = document.querySelector(".page-settings");
nav_links[0].addEventListener("click", () => {
    page_info.classList.add("showed");
    page_settings.classList.remove("showed");
    nav_links[0].classList.add("side-selected");
    nav_links[1].classList.remove("side-selected");
});

nav_links[1].addEventListener("click", () => {
    page_info.classList.remove("showed");
    page_settings.classList.add("showed");
    nav_links[0].classList.remove("side-selected");
    nav_links[1].classList.add("side-selected");
});
