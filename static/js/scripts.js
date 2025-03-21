// Підтвердження видалення
function confirmDelete() {
    return confirm("Ви впевнені, що хочете видалити цей елемент?");
}

// Додавання обробників подій для всіх кнопок видалення
document.addEventListener('DOMContentLoaded', function () {
    const deleteButtons = document.querySelectorAll('.btn.delete');
    deleteButtons.forEach(button => {
        button.addEventListener('click', confirmDelete);
    });
});