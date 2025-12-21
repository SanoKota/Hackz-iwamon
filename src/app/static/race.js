document.addEventListener('DOMContentLoaded', () => {
    const horseGrid = document.getElementById('horse-grid');
    const raceSelector = document.getElementById('race-selector');

    // Function to generate checkboxes
    function generateCheckboxes(horses) {
        if (!horseGrid) return;

        horseGrid.innerHTML = ''; // Clear existing

        horses.forEach((horse, index) => {
            const wrapper = document.createElement('div');
            wrapper.className = 'horse-checkbox-wrapper';

            const checkbox = document.createElement('input');
            checkbox.type = 'checkbox';
            // Use index to ensure unique ID even if horse.id is duplicate or missing
            const uniqueId = `horse-idx-${index}`;
            checkbox.id = uniqueId;
            checkbox.value = horse.value; // Name + Pedigree
            checkbox.className = 'horse-checkbox';

            const label = document.createElement('label');
            label.htmlFor = uniqueId;
            label.textContent = horse.name;
            label.title = horse.value;

            wrapper.appendChild(checkbox);
            wrapper.appendChild(label);
            horseGrid.appendChild(wrapper);
        });
    }

    // Function to populate race dropdown
    function populateRaceDropdown(races) {
        if (!raceSelector) return;

        races.forEach(race => {
            const option = document.createElement('option');
            option.value = race.race_id;
            option.textContent = `${race.race_name} ${race.racetrack} ${race.track_type}${race.distance}m`;
            raceSelector.appendChild(option);
        });

        // Select first by default if available
        if (races.length > 0) {
            raceSelector.value = races[0].race_id;
        }
    }

    // Fetch Data from API via CSV
    async function loadData() {
        try {
            // Load Horses
            const horsesRes = await fetch('/api/horses');
            const horsesData = await horsesRes.json();
            if (horsesData.status === 'success') {
                generateCheckboxes(horsesData.horses);
            } else {
                console.error('Failed to load horses:', horsesData.message);
            }

            // Load Races
            const racesRes = await fetch('/api/races');
            const racesData = await racesRes.json();
            if (racesData.status === 'success') {
                populateRaceDropdown(racesData.races);
            } else {
                console.error('Failed to load races:', racesData.message);
            }

        } catch (error) {
            console.error('Error fetching data:', error);
        }
    }

    // Initial Load
    loadData();

    // Random Select
    const randomBtn = document.getElementById('select-random-btn');
    if (randomBtn) {
        randomBtn.addEventListener('click', () => {
            const checkboxes = Array.from(document.querySelectorAll('.horse-checkbox'));
            // Clear all
            checkboxes.forEach(cb => cb.checked = false);

            if (checkboxes.length > 0) {
                // Select up to 18 random
                const shuffled = checkboxes.sort(() => 0.5 - Math.random());
                const count = Math.min(18, shuffled.length);
                shuffled.slice(0, count).forEach(cb => cb.checked = true);
            }
        });
    }

    // Clear
    const clearBtn = document.getElementById('clear-btn');
    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            document.querySelectorAll('.horse-checkbox').forEach(cb => cb.checked = false);
        });
    }

    const startBtn = document.getElementById('start-race-btn');
    const loader = document.getElementById('loader');
    const responseArea = document.querySelector('.response-area');
    const responseContent = document.querySelector('.response-content');

    if (startBtn) {
        startBtn.addEventListener('click', async () => {
            // Get Selected Horses
            const selectedHorses = Array.from(document.querySelectorAll('.horse-checkbox:checked'))
                .map(cb => cb.value);
            const selectedRaceId = raceSelector ? raceSelector.value : null;

            if (selectedHorses.length < 5) {
                alert('最低5頭選んでください。');
                return;
            }

            if (selectedHorses.length > 18) {
                alert('最大18頭までしか選べません。');
                return;
            }

            if (!selectedRaceId) {
                alert('Please select a race.');
                return;
            }

            // UI Updates
            startBtn.textContent = "スタートしました！"; // Classic call
            startBtn.disabled = true;
            startBtn.style.opacity = '0.8';
            loader.style.display = 'flex';
            responseArea.style.display = 'none';

            try {
                const response = await fetch('/api/run_race', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        horses: selectedHorses,
                        race_id: selectedRaceId
                    })
                });
                const data = await response.json();

                if (data.status === 'success') {
                    responseContent.innerHTML = marked.parse(data.result);
                    responseArea.style.display = 'block';
                    responseArea.scrollIntoView({ behavior: 'smooth' });
                } else {
                    alert('レースのシミュレーションに失敗しました: ' + data.message);
                }

            } catch (error) {
                console.error('Error:', error);
                alert('レースシミュレーション中にエラーが発生しました。');
            } finally {
                // Reset UI
                loader.style.display = 'none';
                startBtn.textContent = 'ファンファーレ';
                startBtn.disabled = false;
                startBtn.style.opacity = '1';
            }
        });
    }
});
