document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('#steam-form');
    const submitButton = form.querySelector('button[type="submit"]');
    const steamIdInput = document.querySelector('#steam-id');
    const title = document.querySelector('#title');
    const summary = document.querySelector('#summary');
    const prompt = document.querySelector('#prompt');

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const steamId = steamIdInput.value;
        var promptInput = '';

        if (prompt && prompt.value) {
            promptInput = prompt.value
        }
        
        title.innerText = '';
        summary.innerText = '';

        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Loading';
        
        const response = await fetch('/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json',},
            body: JSON.stringify({ steam_id: steamId, prompt: promptInput }),
        });

        if (response.ok) {
            const result = await response.json();
            title.innerHTML = `<a href="https://store.steampowered.com/app/${steamId}" target="_blank">
            ${result.title} <i class="fa-solid fa-arrow-up-right-from-square fa-2xs"></i></a>`;
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