window.onload = () => {
    const restore_button = document.querySelector("#restore-password");
    const back_button = document.querySelector("#back-to-auth");
    const restore_form = document.querySelector("#restore-form");
    const auth_form = document.querySelector("#auth-form");

    const toggle_forms = () => {
        restore_form.classList.toggle("hidden");
        auth_form.classList.toggle("hidden");
    };    

    restore_button.addEventListener("click", toggle_forms);
    back_button.addEventListener("click", toggle_forms);
    //fix?
}