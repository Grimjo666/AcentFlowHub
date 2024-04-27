document.addEventListener('DOMContentLoaded', function () {
    const showMenuBtn = document.querySelector('.show-edit-categories-menu');
    const editCategoriesFormWrapper = document.querySelector('.edit-categories-form-wrapper');
    const deleteBtn = document.getElementById('delete-category-btn');
    const deleteButtons = document.querySelectorAll('.button-delete-circle');
    const addCategoryBtn = document.getElementById('add-category-btn');
    const modalWindow = document.querySelector('.modal-window');
    const overlay = document.querySelector('.overlay');

    showMenuBtn.addEventListener('click', function () {
        editCategoriesFormWrapper.classList.toggle('hidden');
    });

    deleteBtn.addEventListener('click', function () {
        deleteButtons.forEach(button => {
            button.classList.toggle('hidden');
        });
    });

    addCategoryBtn.addEventListener('click', function () {
        modalWindow.classList.remove('hidden');
        overlay.classList.remove('hidden');
    });
});


document.addEventListener('DOMContentLoaded', function () {
  // Находим необходимые элементы формы
  const form = document.querySelector('.modal-window form');
  const nameInput = document.getElementById('id_name');
  const colorPicker1 = document.getElementById('colorPicker1');
  const colorPicker2 = document.getElementById('colorPicker2');
  const nameNewCircle = document.getElementById('name-new-circle');
  const colorNewCircle = document.getElementById('color-new-circle');
  const idFirstColorInput = document.getElementById('id_first_color');
  const idSecondColorInput = document.getElementById('id_second_color');

  // Устанавливаем начальные значения из colorPicker1 и colorPicker2
  idFirstColorInput.value = colorPicker1.value;
  idSecondColorInput.value = colorPicker2.value;

  // Вызываем функцию для инициализации стилей круга
  updateCircleStyle();

  // Добавляем обработчик события для изменения значения поля name
  nameInput.addEventListener('input', function () {
    nameNewCircle.textContent = nameInput.value;
  });

  // Добавляем обработчик события для изменения значения цвета из colorPicker1
  colorPicker1.addEventListener('input', function () {
    idFirstColorInput.value = colorPicker1.value;
    updateCircleStyle();
  });

  // Добавляем обработчик события для изменения значения цвета из colorPicker2
  colorPicker2.addEventListener('input', function () {
    idSecondColorInput.value = colorPicker2.value;
    updateCircleStyle();
  });

  // Дополнительная функция для обновления стиля круга
  function updateCircleStyle() {
    const gradient = `linear-gradient(to bottom, ${idFirstColorInput.value}, ${idSecondColorInput.value})`;
    colorNewCircle.style.background = gradient;
  }
});
