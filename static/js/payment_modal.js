document.addEventListener('DOMContentLoaded', () => {
    const modal = document.querySelector('#payment-modal');
    const closeButton = document.querySelector('.close-button');
    const submitButton = document.querySelector('.btn-submit');
    const cancelButton = document.querySelector('.btn-cancel');

    closeButton.addEventListener('click',(event) => closeModal(event));
    cancelButton.addEventListener('click', (event) => closeModal(event));
    
});

function closeModal(event) {
    event.preventDefault();
    window.location.href = "/";
}