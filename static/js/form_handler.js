document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('#steam-form');
    const dropdown = document.querySelector('#game-dropdown');
    const gameNameInput = document.querySelector('#game-name');
    const steamIdInput = document.querySelector('#steam-id');

    const title = document.querySelector('#title');
    const summary = document.querySelector('#summary');

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        const steamId = steamIdInput.value;
        const submitButton = form.querySelector('button[type="submit"]');
        submitButton.disabled = true;
        title.innerText = '';
        summary.innerText = '';
        submitButton.innerHTML = '<i class="fa fa-spinner fa-spin"></i> Loading';
        
        const response = await fetch('/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ steam_id: steamId }),
        });
        if (response.ok) {
            const result = await response.json();            
            title.innerHTML = `<a href="https://store.steampowered.com/app/${steamId}" target="_blank">${result.title}</a><span style="font-size: 48px; color: Dodgerblue">
            <i class="fa-solid fa-arrow-up-right-from-square"></i>
          </span>`;
            if (result.summary) {
                summary.innerText = result.summary;
            } else {
                summary.innerText = "Error fetching summary. Please try again.";
            }
        }
        dropdown.innerHTML = '';
        submitButton.disabled = false;
        submitButton.innerHTML = 'Submit';
    });

    let debounceTimeout;
    gameNameInput.addEventListener('input', async (event) => {
        clearTimeout(debounceTimeout);
        const input = event.target.value;
        dropdown.innerHTML = '';
        debounceTimeout = setTimeout(async () => {
            const response = await fetch(`/search?term=${input}`);
            const result = await response.json();

            var options = [];

            for (const suggestion of Object.values(result.suggestions)) {
                var option = document.createElement('option');
                option.value = suggestion.id;
                option.label = suggestion.name;
                option.textContent = suggestion.name; // Ensure text content is set

                options.push(option.outerHTML);
            }

            dropdown.insertAdjacentHTML('beforeEnd', options.join('\n'));
        }, 300);
    });
});

function change(input) {
    const steamIdInput = document.querySelector('#steam-id');
    steamIdInput.value = input.value;
}