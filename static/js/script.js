document.addEventListener("DOMContentLoaded", function () {
    const characterCards = document.querySelectorAll(".character-card");

    characterCards.forEach(card => {
        card.addEventListener("mouseover", () => {
            card.style.transform = "scale(1.1)";
        });
        card.addEventListener("mouseleave", () => {
            card.style.transform = "scale(1)";
        });
        card.addEventListener("click", () => {
            const characterId = card.dataset.characterId;
            fetch(`/api/adventure/${characterId}/create`, {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                console.log('Adventure executed:', data);
            })
            .catch(error => {
                console.error('Error executing adventure:', error);
            });
        });
    });
});
