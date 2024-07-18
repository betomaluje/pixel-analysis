$(document).ready(function(){
    const form = document.getElementById('steam-form');
    const submitButton = form.querySelector('button[type="submit"]');
    const steamIdInput = document.getElementById('steam-id');
    const title = document.getElementById('title');
    const summary = document.getElementById('summary');
    const prompt = document.getElementById('prompt');
    const gameDetails = document.getElementById('game-details');

    gameDetails.style.display = 'none';

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const steamId = steamIdInput.value;        
        var promptInput = '';

        if (prompt && prompt.value) {
            promptInput = prompt.value
        }
        
        title.innerText = '';
        summary.innerText = '';

        gameDetails.style.display = 'none';

        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Loading';
        
        const response = await fetch('/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json',},
            body: JSON.stringify({ steam_id: steamId, prompt: promptInput }),
        });

        if (response.ok) {
            const result = await response.json();

            populateAll(steamId, result.title);

            gameDetails.style.display = 'block';

            if (result.summary) {
                summary.innerText = result.summary;
            } else {
                summary.innerText = `There is no reviews for ${result.title}. Please try another game.`;
            }
        }

        submitButton.disabled = false;
        submitButton.innerHTML = 'Get Report';
    });    
});

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