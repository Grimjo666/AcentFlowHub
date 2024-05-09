document.addEventListener("DOMContentLoaded", function () {
    var photoItems = document.querySelectorAll('.photo-item');
    var formBlock = document.querySelector('.form-block');
    var changePhotoButton = document.querySelector('.change-photo');
    var deletePhotoButton = document.querySelector('.delete-photo');

    function updateFormVisibility() {
        // Подсчет выбранных чекбоксов
        var checkedCheckboxes = document.querySelectorAll('.photo-item input[type="checkbox"]:checked');

        // Изменение видимости кнопок в зависимости от количества выбранных чекбоксов
        if (checkedCheckboxes.length > 1) {
            changePhotoButton.classList.add('hidden');
            deletePhotoButton.classList.remove('hidden');
        } else if (checkedCheckboxes.length === 1) {
            changePhotoButton.classList.remove('hidden');
            deletePhotoButton.classList.remove('hidden');
        } else {
            changePhotoButton.classList.remove('hidden');
            deletePhotoButton.classList.add('hidden');
            formBlock.classList.add('hidden'); // Скрыть форму, если нет выбранных чекбоксов
        }
    }

    photoItems.forEach(function (photoItem) {
        var checkbox = photoItem.querySelector('input[type="checkbox"]');
        var img = photoItem.querySelector('img');

        img.addEventListener('click', function () {
            // Изменение состояния чекбокса при клике на изображение
            checkbox.checked = !checkbox.checked;

            // Добавление/удаление стиля при активации/деактивации
            if (checkbox.checked) {
                img.style.border = 'solid 3px var(--font_color_activ)';
            } else {
                img.style.border = 'none';
            }

            // Показать или скрыть форму в зависимости от выбора
            formBlock.classList.remove('hidden');

            // Обновить видимость формы
            updateFormVisibility();
        });
    });

    // Добавлен обработчик для чекбоксов, чтобы они не изменялись при клике на изображение
    photoItems.forEach(function (photoItem) {
        var checkbox = photoItem.querySelector('input[type="checkbox"]');
        var img = photoItem.querySelector('img');

        checkbox.addEventListener('click', function (event) {
            // Остановить всплытие события, чтобы избежать дополнительных кликов
            event.stopPropagation();

            // Добавление/удаление стиля при активации/деактивации
            if (checkbox.checked) {
                img.style.border = 'solid 3px var(--font_color_activ)';
            } else {
                img.style.border = 'none';
            }

            // Обновить видимость формы
            updateFormVisibility();
        });
    });
});

