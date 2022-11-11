window.onload = () => {
    const restore_button = document.querySelector("#restore-password");
    const back_button = document.querySelector("#back-to-auth");
    const restore_form = document.querySelector("#restore-form");
    const auth_form = document.querySelector("#auth-form");
    const errors_block = document.querySelector(".errors");

    const toggle_forms = () => {
        restore_form.classList.toggle("hidden");
        auth_form.classList.toggle("hidden");
    };
    
    const send_auth_data = async () => {
        let data = {"login": auth_form.querySelector("#login").value, "password": auth_form.querySelector("#password").value};
        console.log(JSON.stringify(data));
        const response = await fetch('/auth', {
            method: 'POST',
            mode: 'cors',
            cache: 'no-cache',
            credentials: 'same-origin',
            headers: {
              'Content-Type': 'application/json; charset=utf-8'
            },
            body: JSON.stringify(data) // body data type must match "Content-Type" header
        });

        if (response.ok) { // если HTTP-статус в диапазоне 200-299
            let json = await response.json();
            
            if (json.status == 0) {
                setCookie("auth_token", json.auth_token, 100);
                document.location.href = json.redirect;
                
            } else {
                if (json.status == 1) {
                    errors_block.innerHTML = "Ошибка " + json.status + ": поля для ввода не могут оставаться пустыми.";
                } else if (json.status == 7) {
                    errors_block.innerHTML = "Ошибка " + json.status + ": неверный пароль.";
                } else if (json.status == 8) {
                    errors_block.innerHTML = "Ошибка " + json.status + ": пользователя с таким именем не существует.";
                } else if (json.status == 9) {
                    errors_block.innerHTML = "Ошибка " + json.status + ": неизвестная ошибка.";
                }
                errors_block.style.display = "grid";
            }
        } else {
            errors_block.innerHTML = "Ошибка HTTP: " + response.status;
            errors_block.style.display = "grid";
        }
    };

    restore_button.addEventListener("click", toggle_forms);
    back_button.addEventListener("click", toggle_forms);
    auth_form.addEventListener("submit", async (e) => {
        e.preventDefault();
        await send_auth_data();
    });
    
}