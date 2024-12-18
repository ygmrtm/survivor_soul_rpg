function closeModal() {
    document.getElementById('adventure-modal').style.display = 'none'; // Hide the modal
}

document.addEventListener("DOMContentLoaded", function () {
    const characterCards = document.querySelectorAll(".character-card");

    characterCards.forEach(card => {
        const characterId = card.dataset.characterId; // Get character ID from data attribute
        const characterHp = parseInt(card.dataset.characterHp); // Assuming you have hp in data attribute
        // Disable card if character HP is less than zero
        if (characterHp < 0) {
            console.log('Character HP is less than zero. Cannot execute adventure.');
            card.classList.add('disabled'); 
            card.style.pointerEvents = 'none'; 
        }

        card.addEventListener("mouseover", () => {
            card.style.transform = "scale(1.1)";
        });
        card.addEventListener("mouseleave", () => {
            card.style.transform = "scale(1)";
        });
        card.addEventListener("click", () => {
            if (card.classList.contains('disabled')) return; // Prevent action if card is disabled
            card.classList.add('disabled'); // Disable the card
            card.style.pointerEvents = 'none'; // Prevent further clicks
            document.getElementById('adventure-info').innerText = 'Loading...';
            document.getElementById('adventure-modal').style.display = 'block';
            fetch(`/api/adventure/${characterId}/create`, {
                method: 'POST'
            })
            .then(response => response.json())
            .then(data => {
                console.log('Adventure executed:', data);
                const adventureId = data.adventure_id;
                // Fetch adventure details using the adventure ID
                return fetch(`/api/adventure/${adventureId}/execute`, {
                    method: 'POST'
                });
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('adventure-info').innerText = `Adventure ID: ${data.adventure_id}, Status: ${data.status}`;
            })
            .catch(error => {
                console.error('Error fetching adventure details:', error);
                document.getElementById('adventure-info').innerText = 'Failed to load adventure details.';
            });
        });
        // Close modal logic
        document.querySelector('.close-button').addEventListener('click', () => {
            document.getElementById('adventure-modal').style.display = 'none'; // Hide the modal
            // Re-enable all character cards
            characterCards.forEach(card => {
                const alive_pts = parseInt(card.dataset.characterHp)
                if(alive_pts > 0){
                    card.classList.remove('disabled'); // Remove disabled class
                    card.style.pointerEvents = 'auto'; // Re-enable clicks
                    card.style.transform = "scale(1)"; // Reset scale
                }
            });
        });        
    });

    // Calculate the current week number based on ISO calendar
    function getISOWeekNumber(date) {
        const tempDate = new Date(date.getTime());
        tempDate.setDate(tempDate.getDate() + 4 - (tempDate.getDay() || 7));
        const yearStart = new Date(tempDate.getFullYear(), 0, 1);
        return Math.ceil((((tempDate - yearStart) / 86400000) + 1) / 7);
    }

    const currentDate = new Date();
    const weekNumber = getISOWeekNumber(currentDate);
    const prevWeekNumber = weekNumber - 1;
    document.getElementById('week-number').innerText = weekNumber;

    // Add event listener to the button
    document.getElementById('challenges-button').addEventListener('click', function() {
        const button = this;
        button.disabled = true;
        const weekNumber = document.getElementById('week-number').innerText;
        const prevWeekNumber = weekNumber - 1; // Calculate the previous week number

        // First endpoint to create/retrieve challenges for the current week
        fetch(`/api/adventure/challenges/${weekNumber}`, {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            console.log('Challenges created/retrieved for current week:', data);
            // TODO: Implement what to do with the UI with the retrieved challenges if needed
            // Now execute the second endpoint for the previous week
            return fetch(`/api/adventure/challenges/${prevWeekNumber}/evaluate`, {
                method: 'POST'
            });
        })
        .then(response => response.json())
        .then(data => {
            console.log('Challenges retrieved for previous week:', data);
            // Here you can update the UI with the retrieved challenges if needed
            // For example, you could display them in a specific section of your page
            // document.getElementById('challenges-info').innerText = JSON.stringify(data);
        })
        .catch(error => {
            console.error('Error creating/retrieving challenges:', error);
        })
        .finally(() => {
            button.disabled = false; // Re-enable the button after all operations
        });
    });

    document.getElementById('underworld-button').addEventListener('click', function() {
        const button = this;
        button.disabled = true;

        // First endpoint to 
        fetch(`/api/adventure/underworld`, {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            console.log('underworld for current week:', data);
            document.getElementById('dead-people').innerText = "(" + data.reborn  + " but "+ data.still_dead +" still ☠️)";
        })
        .catch(error => {
            console.error('Error in underworld:', error);
        })
        .finally(() => {
            button.disabled = false;
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

    // Fetch the dead people number from the new endpoint
    fetch('/api/notion/countdeadpeople')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            document.getElementById('dead-people').innerText = "(" + data.count + ")";
        })
        .catch(error => {
            console.error('Error fetching counts:', error);
            document.getElementById('dead-people').innerText = '0'; // Fallback version
        });
});
