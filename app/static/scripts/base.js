window.onload = () => {
    const side_menu = document.querySelector(".side-menu");

    const menu_items = document.querySelectorAll(".menu-item");
    const triplet = document.querySelector(".menu-triplet svg");
    menu_items.forEach(menu_item => {
        menu_item.children[0].querySelector("a, div").addEventListener("click", () => {
            menu_items.forEach(menu_item2 => {
                menu_item2.children[1].classList.remove("selected");
            });
            menu_item.children[1].classList.toggle("selected");
        });
    });

    triplet.addEventListener("click", () => {
        side_menu.classList.toggle("opened");
    });

    document.addEventListener("click", (e) => {
        if (!e.target.classList.contains("hide-on-click")) {
            menu_items.forEach(menu_item => {
                menu_item.children[1].classList.remove("selected");
            });
        }
    });
};

/*
    const func = () => {};
    function func() {};
*/
