document.addEventListener('DOMContentLoaded', function () {
    const showMenuBtn = document.querySelector('.show-edit-categories-menu');
    const editCategoriesFormWrapper = document.querySelector('.edit-categories-form-wrapper');
    const deleteBtn = document.getElementById('delete-category-btn');
    const deleteButtons = document.querySelectorAll('.button-delete-circle');

    showMenuBtn.addEventListener('click', function () {
        editCategoriesFormWrapper.classList.toggle('hidden');
    });

    deleteBtn.addEventListener('click', function () {
        deleteButtons.forEach(button => {
            button.classList.toggle('hidden');
        });
    });
});