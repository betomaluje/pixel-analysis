document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('#steam-form');
    const submitButton = form.querySelector('button[type="submit"]');
    const steamIdInput = document.querySelector('#steam-id');
    const title = document.querySelector('#title');
    const summary = document.querySelector('#summary');

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const steamId = steamIdInput.value;        
        
        title.innerText = '';
        summary.innerText = '';

        submitButton.disabled = true;
        submitButton.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Loading';
        
        const response = await fetch('/', {
            method: 'POST',
            headers: {'Content-Type': 'application/json',},
            body: JSON.stringify({ steam_id: steamId }),
        });

        if (response.ok) {
            const result = await response.json();            
            title.innerHTML = `<a href="https://store.steampowered.com/app/${steamId}" target="_blank">${result.title} <span style="font-size: 48px; color: Dodgerblue">
            <i class="fa-solid fa-arrow-up-right-from-square"></i>
          </span></a>`;
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

function change(input) {
    const steamIdInput = document.querySelector('#steam-id');
    steamIdInput.value = input.value;
}