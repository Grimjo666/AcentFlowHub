document.addEventListener('DOMContentLoaded', function () {
    const addSubGoalBtns = document.querySelectorAll('.add-sub-goal-btn');
    const modalWindow = document.querySelector('.modal-window');
    const overlay = document.querySelector('.overlay');
    const parentInput = document.getElementById('parent_id_input');

    addSubGoalBtns.forEach(function (btn) {
        btn.addEventListener('click', function () {
            showModal();
            const goalId = btn.getAttribute('data-goal-id');
            parentInput.value = goalId;
        });
    });

    overlay.addEventListener('click', hideModal);

    function showModal() {
        modalWindow.classList.remove('hidden');
        overlay.classList.remove('hidden');
    }

    function hideModal() {
        modalWindow.classList.add('hidden');
        overlay.classList.add('hidden');
        parentInput.value = '';
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
