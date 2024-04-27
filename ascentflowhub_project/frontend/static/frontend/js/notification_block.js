
// Отслеживаем загрузку страницы
document.addEventListener("DOMContentLoaded", function() {
// Находим элемент всплывающего окна
var notification = document.getElementById("notifications");

// Если всплывающее окно присутствует
if (notification) {
  // Задаем таймаут (в миллисекундах) для автоматического исчезновения
  setTimeout(function() {
    notification.style.display = "none";
  }, 7000);
}
});