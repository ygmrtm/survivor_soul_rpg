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
    log.value += (weekNumber + '|' + currentTime + ' | ' + message + '\n'); // Append the new message
    log.scrollTop = log.scrollHeight; // Scroll to the bottom
}

document.addEventListener("DOMContentLoaded", function () {
    document.getElementById('week-number').innerText = weekNumber;
    document.getElementById('current-year').innerText = new Date().getFullYear();
    const characterCards = document.querySelectorAll(".character-card");
    const healImage = document.getElementById('heal-image');

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
                logActivity(`❌❌ Error : ${error.message}`);
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

        logActivity(`Challenges | Creating challenges for week ${weekNumber} and year ${yearNumber}...`);
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
            logActivity(`Challenges | Challenges created/retrieved for current week: ${data.count_challenges}`);

            // Now execute individual challenge endpoints sequentially
            logActivity(`Challenges | Evaluating challenges for week ${prevWeekNumber} and year ${yearNumber}...`);

            // Execute challenges sequentially
            return executeChallengeSequentially(prevWeekNumber, yearNumber);
        })
        .then(() => {
            logActivity(`Challenges | All challenges evaluated successfully!`);
        })
        .catch(error => {
            console.error('Error creating/retrieving challenges:', error);
            logActivity(`❌❌ Error : ${error.message}`);
        })
        .finally(() => {
            button.disabled = false; // Re-enable the button after all operations
        });
    });

    // Function to execute challenges sequentially
    function executeChallengeSequentially(weekNumber, yearNumber) {
        // Define the sequence of challenges to execute
        const challenges = [
            { name: 'Consecutive Days', endpoint: `/api/adventure/challenges/consecutive/${weekNumber}/${yearNumber}`, method: 'POST' },
            { name: 'Habits Counts', endpoint: `/api/adventure/challenges/habits/${weekNumber}/${yearNumber}`, method: 'POST' },
            { name: 'Habits Longest Streak (Created)', endpoint: `/api/adventure/challenges/habit_longest_streak_created/${weekNumber}/${yearNumber}`, method: 'POST' },
            { name: 'Habits Longest Streak (Executed)', endpoint: `/api/adventure/challenges/habit_longest_streak_executed`, method: 'POST' },
            { name: 'Coding', endpoint: `/api/adventure/challenges/coding/${weekNumber}/${yearNumber}`, method: 'POST' },
            { name: 'Bike', endpoint: `/api/adventure/challenges/bike/${weekNumber}/${yearNumber}`, method: 'POST' },
            { name: 'Stencil', endpoint: `/api/adventure/challenges/stencil/${weekNumber}/${yearNumber}`, method: 'POST' },
            { name: 'Epics', endpoint: `/api/adventure/challenges/epics/${weekNumber}/${yearNumber}`, method: 'POST' },
            { name: 'Expired', endpoint: `/api/adventure/challenges/expired/${weekNumber}/${yearNumber}`, method: 'POST' },
            { name: 'Due Soon', endpoint: `/api/adventure/challenges/due_soon/21`, method: 'POST' },
            { name: 'Watchlist', endpoint: `/api/adventure/challenges/watchlist`, method: 'POST' }
        ];

        // Execute challenges one by one
        return challenges.reduce((promiseChain, challenge) => {
            return promiseChain.then(() => {
                logActivity(`Challenges | Executing ${challenge.name}...`);
                return fetch(challenge.endpoint, {
                    method: challenge.method
                })
                .then(response => {
                    if (!response.ok) {
                        return response.json().then(errData => {
                            throw new Error(`${challenge.name} failed with status: ${response.status}. ${errData.error || ''}`);
                        });
                    }
                    return response.json();
                })
                .then(data => {
                    // Extract count from the response
                    const countKey = Object.keys(data).find(key => key.endsWith('_count'));
                    const count = countKey ? data[countKey] : 0;
                    logActivity(`Challenges | ${challenge.name}: ${count}`);

                    // Check for errors in the response
                    if (data.error) {
                        logActivity(`❌❌ Error in ${challenge.name}: ${data.error}`);
                    }
                })
                .catch(error => {
                    logActivity(`❌❌ Error in ${challenge.name}: ${error.message}`);
                    // Continue with the next challenge even if this one fails
                    return Promise.resolve();
                });
            });
        }, Promise.resolve());
    }

    document.getElementById('underworld-button').addEventListener('click', function() {
        const button = this;
        button.disabled = true;
        let still_dead = 0;
        let reborn = 0;
        let totalDead = 0;
        logActivity(`Executing 💀 underworld(s)...`);

        // Define sequential underworld steps
        const steps = [
            {
                name: 'Underworlds Created',
                endpoint: '/api/adventure/underworld/create',
                process: (data) => {
                    const created = data.created_count || 0;
                    totalDead = data.dead_people_count || 0;
                    logActivity(`Underworlds 💀 created: ${created}`);
                }
            },
            {
                name: 'Underworlds Executed',
                endpoint: '/api/adventure/underworld/execute',
                process: (data) => {
                    const executed = data.executed_count || 0;
                    reborn = executed;
                    still_dead = Math.max(0, totalDead - executed);
                    logActivity(`Underworlds 💀 executed: ${executed}`);
                }
            },
            {
                name: 'Underworlds Awaked',
                endpoint: '/api/adventure/underworld/awake',
                process: (data) => {
                    const awaked = data.awaked_count || 0;
                    logActivity(`Underworlds 💀 awaked: ${awaked}`);
                }
            },
            {
                name: 'Adventures Punishment Execution',
                endpoint: '/api/adventure/underworld/punish',
                process: (data) => {
                    const punishments = data.punishments_count || 0;
                    logActivity(`Underworlds 💩 punishments: ${punishments}`);
                }
            }
        ];

        // Execute steps sequentially
        steps.reduce((p, step) => {
            return p.then(() => {
                logActivity(`${step.name}...`);
                return fetch(step.endpoint, { method: 'POST' })
                    .then(response => {
                        if (!response.ok) {
                            return response.json().then(err => {
                                throw new Error(`${step.name} failed with status: ${response.status}. ${err.error || ''}`);
                            });
                        }
                        return response.json();
                    })
                    .then(data => {
                        step.process(data);
                    })
                    .catch(error => {
                        logActivity(`❌❌ Error in ${step.name}: ${error.message}`);
                        // Continue with next steps even if one fails
                        return Promise.resolve();
                    });
            });
        }, Promise.resolve())
        .finally(() => {
            const still_dead_str = "(" + reborn + " but " + still_dead + " still ☠️)";
            logActivity(still_dead_str);
            if (still_dead > 0){
                document.getElementById('dead-people').innerText = still_dead_str;
                button.disabled = false;
            }
            fetch('/api/notion/countpeoplepills')
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    if(data.count > 0){
                        logActivity(`People with pills 💊 ${data.count}`);
                        document.getElementById('heal-button').disabled = false;
                        setTimeout(() => {
                            logActivity(`People with pills 💊 timeout.`);
                            document.getElementById('heal-button').disabled = true;
                        }, 60000 * 10);
                    }
                })
                .catch(error => {
                    console.error('Error fetching counts:', error);
                    logActivity(`❌❌ Error : ${error.message}`);
                });
        });
    });

    document.getElementById('tournament-button').addEventListener('click', function() {
        const button = this;
        button.disabled = true;
        current_to_execute = document.getElementById('pending-tournaments').innerText;
        let still_not_executed = 0;
        let actually_executed = 0;
        logActivity(`Executing ${current_to_execute} ⚔️ tournament(s)...`);

        // First endpoint to
        fetch(`/api/tournament/evaluate/all`, {
            method: 'GET'
        })
        .then(response => response.json())
        .then(data => {
            console.log('tournaments response', data);
            still_not_executed = data.still_not_executed
            actually_executed = data.actually_executed
        })
        .catch(error => {
            console.error('Error in tournament:', error);
            logActivity(`❌❌ Error in tournament:: ${error.message}`);
        })
        .finally(() => {
            document.getElementById('pending-tournaments').innerText = "(" + still_not_executed + ")";
            if(still_not_executed > 0){
                button.disabled = false;
                logActivity(`Still pending ${still_not_executed} tournaments.`);
            }else{
                logActivity(`Tournaments executed 🗡️ ${actually_executed}/${current_to_execute}`)
            }
        });
    });

    document.getElementById('flush-button').addEventListener('click', function() {
        const button = this;
        button.disabled = true;
        logActivity(`Flushing cache (Redis)...`);
        // First endpoint to
        fetch(`/api/notion/flushredis`, {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            logActivity(`🚽 ${data.message}`);
            logActivity(`characters:* (${data.characters_del})`)
            logActivity(`loaded_characters_*:* (${data.indicators_del})`)
        })
        .catch(error => {
            console.error('Error flushing:', error);
            logActivity(`❌❌ Error flushing: ${error.message}`);
        })
        .finally(() => {
            button.disabled = false;
        });
    });

    document.getElementById('heal-button').addEventListener('click', function() {
        const button = this;
        button.disabled = true;
        logActivity(`Healing with 💊 ...`);
        healImage.src = "/static/img/smoking-logo.png";

        // First endpoint to
        fetch(`/api/notion/characters/applypills/deep_level/l3`, {
            method: 'POST'
        })
        .then(response => response.json())
        .then(data => {
            for (let color in data){
                logActivity(`${color} 💊 ${data[color]['message']}`);
            }
            healImage.src = "/static/img/redeye-logo.png";
        })
        .catch(error => {
            console.error('Error healing:', error);
            logActivity(`❌❌ Error healing: ${error.message}`);
        })
        .finally(() => {
            button.disabled = true;
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
            logActivity(`Version: ${data.version}`);
            document.getElementById('version-number').innerText = data.version;
        })
        .catch(error => {
            console.error('Error fetching version:', error);
            logActivity(`❌❌ Error : ${error.message}`);
            document.getElementById('version-number').innerText = '0.0.0'; // Fallback version
        });

    // Fetch the dead people number from the new endpoint
    fetch('/api/notion/countdeadpeople/l3')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if(data.count > 0){
                logActivity(`Dead people 💀 ${data.count}`);
                document.getElementById('underworld-button').disabled = false;
                document.getElementById('dead-people').innerText = "(" + data.count + "☠️)";
            }
        })
        .catch(error => {
            console.error('Error fetching counts:', error);
            logActivity(`❌❌ Error : ${error.message}`);
            document.getElementById('dead-people').innerText = '0'; // Fallback version
        });

    fetch('/api/notion/countpeoplepills/l3')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if(data.count > 0){
                logActivity(`People with pills 💊 ${data.count}`);
                document.getElementById('heal-button').disabled = false;
                setTimeout(() => {
                    logActivity(`People with pills 💊 timeout.`);
                    document.getElementById('heal-button').disabled = true;
                }, 60000 * 10); // Disable the heal button after 60 seconds

            }
        })
        .catch(error => {
            console.error('Error fetching counts:', error);
            logActivity(`❌❌ Error : ${error.message}`);
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
                logActivity(`Pending tournaments ⚔️ ${data.pending_tournaments}`);
                document.getElementById('tournament-button').disabled = false;
                document.getElementById('pending-tournaments').innerText = "(" + data.pending_tournaments + ")";
            }
        })
        .catch(error => {
            console.error('Error fetching counts:', error);
            logActivity(`❌❌ Error : ${error.message}`);
            document.getElementById('pending-tournaments').innerText = '0'; // Fallback version
        });
});
