document.addEventListener('DOMContentLoaded', () => {
    const modal = document.querySelector('#payment-modal');
    const closeButton = document.querySelector('.close-button');
    const submitButton = document.querySelector('.btn-submit');
    const cancelButton = document.querySelector('.btn-cancel');

    closeButton.addEventListener('click',(event) => closeModal(event));
    cancelButton.addEventListener('click', (event) => closeModal(event));

    submitButton.addEventListener('click', async (event) => {
        event.preventDefault();

        submitButton.disabled = true;

        const response = await fetch('/payment-success', {
            method: 'POST',
            headers: {'Content-Type': 'application/json',},
            body: JSON.stringify({payment: true}),
        });

        if (response.ok) {
            console.log('Payment successful');
            window.location.href = "/";
        }

        submitButton.disabled = false;
    });
    
});

function closeModal(event) {
    event.preventDefault();
    window.location.href = "/";
}