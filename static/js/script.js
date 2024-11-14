document.addEventListener("DOMContentLoaded", function () {
    const characterCards = document.querySelectorAll(".character-card");

    characterCards.forEach(card => {
        card.addEventListener("mouseover", () => {
            card.style.transform = "scale(1.1)";
        });
        card.addEventListener("mouseleave", () => {
            card.style.transform = "scale(1)";
        });
    });
});
