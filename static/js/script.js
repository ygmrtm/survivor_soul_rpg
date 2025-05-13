function closeModal() {
    document.getElementById('adventure-modal').style.display = 'none'; // Hide the modal
    // Re-enable all character cards
    const characterCards = document.querySelectorAll(".character-card");
    characterCards.forEach(card => {
        const alive_pts = parseInt(card.dataset.characterHp);
        const characterStatus = card.dataset.characterStatus;
        if(alive_pts > 0 && characterStatus == 'alive'){
            card.classList.remove('disabled'); // Remove disabled class
            card.style.pointerEvents = 'auto'; // Re-enable clicks
            card.style.transform = "scale(1)"; // Reset scale
        }
    });
}

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
console.log(currentDate, weekNumber, prevWeekNumber);

function logActivity(message) {
    const currentTime = new Date().toLocaleTimeString();
    const log = document.getElementById('activity-log');
    log.value += (weekNumber + ' | ' + currentTime + ' | ' + message + '\n'); // Append the new message
    log.scrollTop = log.scrollHeight; // Scroll to the bottom
}


document.addEventListener("DOMContentLoaded", function () {
    document.getElementById('week-number').innerText = weekNumber;
    document.getElementById('current-year').innerText = new Date().getFullYear();
    const characterCards = document.querySelectorAll(".character-card");

    characterCards.forEach(card => {
        const characterId = card.dataset.characterId; 
        const characterHp = parseInt(card.dataset.characterHp); 
        const characterStatus = card.dataset.characterStatus;
        // Disable card if character HP is less than zero
        if (characterHp < 0 || characterStatus != 'alive') {
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
            logActivity(`Starting adventure for ${card.dataset.characterName}...`); // Log activity
            document.getElementById('adventure-info').innerText = 'Loading... ' + card.dataset.characterName;
            document.getElementById('adventure-modal').style.display = 'block';
            fetch(`/api/adventure/${characterId}/create`, {
                method: 'POST'
            })
            .then(response => {
                if (!response.ok) {
                    // If the response is not ok (not 2xx status), throw an error
                    throw new Error(`Create adventure failed with status: ${response.status}`);
                }
                logActivity(`Adventure created for ${card.dataset.characterName}...`);
                document.getElementById('adventure-info').innerText += '... created 👍';
                return response.json();
            })
            .then(data => {
                console.log('Adventure created:', data);
                
                // Check if we received a valid adventure_id
                if (!data.adventure_id) {
                    throw new Error('Invalid adventure data: Missing adventure_id');
                }
                
                const adventureId = data.adventure_id;
                logActivity(`Executing adventure for ${card.dataset.characterName} ID ${adventureId}.`);
                
                // Only proceed to execute if we have a valid adventure_id
                return fetch(`/api/adventure/${adventureId}/execute`, {
                    method: 'POST'
                });
            })
            .then(response => {
                if (!response.ok) {
                    // If the execute response is not ok, throw an error
                    throw new Error(`Execute adventure failed with status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                let texto = `${data.who_name} has ${data.status} ID: ${data.adventure_id}`;
                logActivity(texto);
                document.getElementById('adventure-info').innerText = texto;                
            })
            .catch(error => {
                console.error('Error in adventure flow:', error);
                logActivity(`Error: ${error.message}`);
                document.getElementById('adventure-info').innerText = `Failed: ${error.message}`;
                
                // Re-enable the card if there was an error in the create step
                card.classList.remove('disabled');
                card.style.pointerEvents = 'auto';
            });
        });
        // Close modal logic
        document.querySelector('.close-button').addEventListener('click', () => {
            document.getElementById('adventure-modal').style.display = 'none'; // Hide the modal
        });        
    });


    // Add event listener to the button
    document.getElementById('challenges-button').addEventListener('click', function() {
        const button = this;
        button.disabled = true;
        const weekNumber = parseInt(document.getElementById('week-number').innerText);
        let prevWeekNumber = weekNumber - 1; // Calculate the previous week number
        let yearNumber = new Date().getFullYear(); // Get the current year


        // Clear the modal content before making requests
        document.getElementById('adventure-info').innerText = 'Loading...'; // Reset modal content


        // First endpoint to create/retrieve challenges for the current week
        fetch(`/api/adventure/challenges/${weekNumber}/${yearNumber}/create`, {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
        // Validate if prevWeekNumber is less than or equal to zero
            if (prevWeekNumber <= 0) {
                prevWeekNumber = 52; // Set to the last week of the previous year
                yearNumber -= 1; // Decrement the year
            }
            console.log('Challenges created/retrieved for current week:', data);
            // TODO: Implement what to do with the UI with the retrieved challenges if needed
            // Now execute the second endpoint for the previous week
            return fetch(`/api/adventure/challenges/${prevWeekNumber}/${yearNumber}/evaluate`, {
                method: 'POST'
            });
        })
        .then(response => response.json())
        .then(data => {
            console.log('Challenges retrieved for previous week:', data);
            // TODO: Here you can update the UI with the retrieved challenges if needed
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
        still_dead = 0
        reborn = 0

        // First endpoint to 
        fetch(`/api/adventure/underworld`, {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            console.log('underworld for current week:', data);
            still_dead = data.still_dead 
            reborn = data.reborn
        })
        .catch(error => {
            console.error('Error in underworld:', error);
        })
        .finally(() => {
            if (still_dead > 0){
                document.getElementById('dead-people').innerText = "(" + reborn  + " but "+ still_dead +" still ☠️)";
                button.disabled = false;
            }
        });
    });

    document.getElementById('tournament-button').addEventListener('click', function() {
        const button = this;
        button.disabled = true;
        still_not_executed = 0;

        // First endpoint to 
        fetch(`/api/tournament/evaluate/all`, {
            method: 'GET'
        })
        .then(response => response.json())
        .then(data => {
            console.log('tournaments response', data);
            still_not_executed = data.still_not_executed
        })
        .catch(error => {
            console.error('Error in tournament:', error);
        })
        .finally(() => {
            document.getElementById('pending-tournaments').innerText = "(" + still_not_executed + ")";
            if(still_not_executed > 0){
                button.disabled = false;
            }
        });
    });


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
            if(data.count > 0){
                document.getElementById('underworld-button').disabled = false;
                document.getElementById('dead-people').innerText = "(" + data.count + "☠️)";
            }
        })
        .catch(error => {
            console.error('Error fetching counts:', error);
            document.getElementById('dead-people').innerText = '0'; // Fallback version
        });

        fetch('/api/tournament/all')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if(data.pending_tournaments > 0){
                document.getElementById('tournament-button').disabled = false;
                document.getElementById('pending-tournaments').innerText = "(" + data.pending_tournaments + ")";
            }
        })
        .catch(error => {
            console.error('Error fetching counts:', error);
            document.getElementById('pending-tournaments').innerText = '0'; // Fallback version
        })        
});
