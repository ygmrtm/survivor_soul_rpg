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

    // Calculate the current week number based on ISO calendar
    function getISOWeekNumber(date) {
        const tempDate = new Date(date.getTime());
        // Set to nearest Thursday: current date + 4 - current day number
        tempDate.setDate(tempDate.getDate() + 4 - (tempDate.getDay() || 7));
        const yearStart = new Date(tempDate.getFullYear(), 0, 1);
        // Calculate full weeks to the nearest Thursday
        return Math.ceil((((tempDate - yearStart) / 86400000) + 1) / 7);
    }

    const currentDate = new Date();
    const weekNumber = getISOWeekNumber(currentDate);
    document.getElementById('week-number').innerText = weekNumber;

    // Add event listener to the button
    document.getElementById('challenges-button').addEventListener('click', function() {
        fetch(`/api/adventure/challenges/${weekNumber}`, {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            console.log('Challenges created:', data);
            // Handle the response as needed (e.g., display a message or update the UI)
        })
        .catch(error => {
            console.error('Error creating challenges:', error);
        });
    });

    document.getElementById('current-year').innerText = new Date().getFullYear();
        
    // Fetch the version number from the new endpoint
    fetch('/api/adventure/version')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            document.getElementById('version-number').innerText = data.version;
        })
        .catch(error => {
            console.error('Error fetching version:', error);
            document.getElementById('version-number').innerText = '1.0.0'; // Fallback version
        });
});


