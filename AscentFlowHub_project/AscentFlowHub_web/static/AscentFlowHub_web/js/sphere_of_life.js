document.addEventListener('DOMContentLoaded', function () {
    const showEditFormButtons = document.querySelectorAll('.goal-show-edit-form');
    const goalFormWrappers = document.querySelectorAll('.goal-form-wrapper');
    const showDescriptionButtons = document.querySelectorAll('.goal-show-description-btn');
    const goalDescriptionBlocks = document.querySelectorAll('.goal-description-block');

    showEditFormButtons.forEach(function (button, index) {
        button.addEventListener('click', function () {
            goalFormWrappers[index].classList.toggle('hidden');
        });
    });

    showDescriptionButtons.forEach(function (button, index) {
        button.addEventListener('click', function () {
            goalDescriptionBlocks[index].classList.toggle('hidden');
            toggleButtonSymbol(button);
        });
    });

    function toggleButtonSymbol(button) {
        const currentSymbol = button.textContent.trim();
        button.textContent = currentSymbol === '▼' ? '▲' : '▼';
    }
});

// код для визуальной логики чекбоксов
document.addEventListener('DOMContentLoaded', function () {
    const checkboxContainer = document.querySelectorAll('.checkbox-container input[type="checkbox"]');
    const formWrapper = document.querySelector('.checkbox-sub-goal-form-wrapper');

    // Функция для обновления состояния блока в зависимости от активности чекбоксов
    function updateFormVisibility() {
        const anyCheckboxChecked = Array.from(checkboxContainer).some(checkbox => checkbox.checked);

        if (anyCheckboxChecked) {
            formWrapper.classList.remove('hidden');
        } else {
            formWrapper.classList.add('hidden');
        }
    }

    // Добавляем обработчик события для каждого чекбокса
    checkboxContainer.forEach(checkbox => {
        checkbox.addEventListener('change', updateFormVisibility);
    });

    // Вызываем функцию при загрузке страницы, чтобы обновить состояние блока
    updateFormVisibility();
});

// логика кнопки формы добавления целей
document.addEventListener('DOMContentLoaded', function () {
    const modalWindow = document.querySelector('.modal-window');
    const overlay = document.querySelector('.overlay');
    const addGoalBtn = document.querySelector('.add-goal-btn');
    const addSubGoalBtns = document.querySelectorAll('.add-sub-goal-btn');
    const parentInput = document.getElementById('parent_id_input');

    // Функция для показа модального окна
    function showModal() {
        modalWindow.classList.remove('hidden');
        overlay.classList.remove('hidden');
    }

    // Функция для скрытия модального окна
    function hideModal() {
        modalWindow.classList.add('hidden');
        overlay.classList.add('hidden');
        parentInput.value = ''; // Очищаем parent_id_input при скрытии модального окна
    }

    // Обработчик события для кнопки добавления цели
    addGoalBtn.addEventListener('click', showModal);

    // Обработчик события для каждой кнопки добавления промежуточной цели
    addSubGoalBtns.forEach(function (btn) {
        btn.addEventListener('click', function () {
            showModal();
            const goalId = btn.dataset.goalId; // Извлекаем goal_id из data-атрибута кнопки
            parentInput.value = goalId; // Заполняем parent_id_input
        });
    });

    // Обработчик события для клика по оверлею
    overlay.addEventListener('click', hideModal);
});

