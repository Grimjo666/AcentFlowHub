document.addEventListener('DOMContentLoaded', function () {
    const overlay = document.querySelector('.overlay');
    const modalWindow = document.querySelector('.modal-window');

    overlay.addEventListener('click', function () {
        overlay.classList.add('hidden');
        modalWindow.classList.add('hidden');
    });
});
