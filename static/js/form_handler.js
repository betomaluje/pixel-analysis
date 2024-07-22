$(document).ready(function(){
    const form = document.getElementById('steam-form');
    const submitButton = form.querySelector('button[type="submit"]');
    const steamIdInput = document.getElementById('steam-id');
    const summary = document.getElementById('summary');
    const prompt = document.getElementById('prompt');

    hideDetails();   

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const steamId = steamIdInput.value;

        const input = document.getElementById("game-name").value;

        if ((input == null || input == "") || !input.trim().length) {
            const Toast = Swal.mixin({
                toast: true,
                position: "top-end",
                showConfirmButton: false,
                timer: 2500,
                timerProgressBar: true,
                didOpen: (toast) => {
                    toast.onmouseenter = Swal.stopTimer;
                    toast.onmouseleave = Swal.resumeTimer;
                },
                });
                Toast.fire({
                    icon: "error",
                    title: "You need to enter a Steam game id or search by name first.",
                    });
            return;
        }

        var promptInput = '';

        if (prompt && prompt.value) {
            promptInput = prompt.value
        }
        
        summary.innerHTML = '';

        hideDetails();

        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Loading';

        Swal.fire({
            title: 'Loading...',
            html: 'Fetching reviews from Steam and then preparing the analysis.\nDepending on the popularity of the game it might take up to a couple of minutes.\nPlease wait...',
            allowEscapeKey: false,
            allowOutsideClick: false,
            didOpen: () => {
                Swal.showLoading()
            }
        });
        
        const response = await fetch('/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json',},
            body: JSON.stringify({ steam_id: steamId, prompt: promptInput, title: title.value }),
        });

        Swal.close();

        if (response.ok) {
            const result = await response.json();

            const chart = document.getElementById('game-chart');
            chart.src = "https://steamdb.info/embed/?appid=" + steamId;

            populateAll(steamId, result.title);

            showDetails();            

            if (result.summary) {
                const newDiv = document.createElement('p');
                newDiv.innerText = `${result.summary}`;
                summary.appendChild(newDiv);
            }
        } else {
            console.log(response);
            Swal.fire({
                icon: 'error',
                title: 'Error',
                text: 'Error: ' + response.statusText,
            });
        }


        submitButton.disabled = false;
        submitButton.innerHTML = 'Get Report';
    });    
});

function hideDetails() {
    const title = document.getElementById('title');
    const gameDetails = document.getElementById('game-details');
    const chart = document.getElementById('game-chart');

    gameDetails.style.display = 'none';
    chart.style.display = 'none';
    title.style.display = 'none';
}

function showDetails() {
    const title = document.getElementById('title');
    const gameDetails = document.getElementById('game-details');
    const chart = document.getElementById('game-chart');

    gameDetails.style.display = 'block';
    chart.style.display = 'block';
    title.style.display = 'block';
}

function showImages() {
    document.getElementById("dialog").showModal();
}

function hideImages() {
    document.getElementById("dialog").close();
}

function populateAll(steamId, title) {
    if (steamId == null) {
        return;
    }

    populate(steamId, "capsule_header", "header.jpg");
    populate(steamId, "capsule_small", "capsule_231x87.jpg");
    populate(steamId, "capsule_main", "capsule_616x353.jpg");
    populate(steamId, "capsule_vertical", "hero_capsule.jpg");
    populate(steamId, "page_background", "page_bg_generated_v6b.jpg");
    populate(steamId, "library_capsule", "library_600x900.jpg");
    populate(steamId, "library_hero", "library_hero.jpg");
    populate(steamId, "library_logo", "logo.png");
    populateURL(steamId, title);    
}

function populateURL(steamId, gameTitle)  {
    const title = document.querySelector('#title');
    title.innerHTML = "<a href=\"https://store.steampowered.com/app/"+ steamId + " target=\"_blank\">" + gameTitle + "<i class=\"fa-solid fa-arrow-up-right-from-square fa-2xs\"></i></a>";
}

function populate(steamId, elementID, filename)  {
    let contentHolder = document.getElementById(elementID);
    if (contentHolder == null) {
        return;
    }
    let content = "<img src=\"https://cdn.cloudflare.steamstatic.com/steam/apps/" + steamId + "/" + filename + "\"></img>";
    contentHolder.innerHTML = content;
}