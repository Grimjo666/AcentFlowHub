document.addEventListener('DOMContentLoaded', function () {
    var changePhotoButton = document.querySelector('.button-change-photo');
    var updateOrRemoveBlock = document.querySelector('.update-or-remove-photo-block');

    changePhotoButton.addEventListener('click', function () {
        // Переключаем видимость блока при каждом клике
        updateOrRemoveBlock.classList.toggle('hidden');
    });
});