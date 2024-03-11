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