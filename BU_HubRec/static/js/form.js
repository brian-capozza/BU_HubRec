// static/js/form.js

document.addEventListener('DOMContentLoaded', function() {
    console.log('Form JS loaded');
    
    // Handle hub selection count inputs
    const hubCheckboxes = document.querySelectorAll('[data-hub-checkbox]');
    console.log('Found checkboxes:', hubCheckboxes.length);
    
    hubCheckboxes.forEach(checkbox => {
        const hubName = checkbox.getAttribute('data-hub-checkbox');
        const countWrapper = document.querySelector(`[data-count-wrapper="${hubName}"]`);
        const countInput = document.querySelector(`#id_${hubName}_count`);
        
        console.log(`Setting up ${hubName}:`, {
            checkbox: !!checkbox,
            countWrapper: !!countWrapper,
            countInput: !!countInput,
            initialChecked: checkbox.checked,
            initialValue: countInput?.value
        });
        
        // Function to update count wrapper visibility
        function updateCountVisibility() {
            if (checkbox.checked) {
                if (countWrapper) {
                    countWrapper.style.display = 'block';
                    countWrapper.classList.add('active');
                }
                // Set default value if empty
                if (countInput && (!countInput.value || countInput.value === '')) {
                    countInput.value = '1';
                    console.log(`Set default value for ${hubName}`);
                }
                // DON'T disable the input - we need it to submit
                if (countInput) {
                    countInput.disabled = false;
                }
            } else {
                if (countWrapper) {
                    countWrapper.style.display = 'none';
                    countWrapper.classList.remove('active');
                }
                // Clear the value but don't disable (let form validation handle it)
                if (countInput) {
                    countInput.value = '';
                }
            }
            
            console.log(`Updated ${hubName}:`, {
                checked: checkbox.checked,
                value: countInput?.value,
                disabled: countInput?.disabled
            });
        }
        
        // Set initial state
        updateCountVisibility();
        
        // Handle checkbox changes
        checkbox.addEventListener('change', function() {
            console.log(`${hubName} checkbox changed to:`, this.checked);
            updateCountVisibility();
        });
        
        // Log when count input changes
        if (countInput) {
            countInput.addEventListener('change', function() {
                console.log(`${hubName} count changed to:`, this.value);
            });
        }
    });
    
    // Log form data before submission
    const form = document.querySelector('.wizard-form');
    if (form) {
        form.addEventListener('submit', function(e) {
            console.log('Form submitting...');
            
            const formData = new FormData(form);
            console.log('Form data:');
            for (let [key, value] of formData.entries()) {
                if (key.includes('hub')) {
                    console.log(`  ${key}: ${value}`);
                }
            }
            
            const checkedHubs = document.querySelectorAll('[data-hub-checkbox]:checked');
            console.log('Checked hubs:', checkedHubs.length);
            
            checkedHubs.forEach(checkbox => {
                const hubName = checkbox.getAttribute('data-hub-checkbox');
                const countInput = document.querySelector(`#id_${hubName}_count`);
                
                if (countInput) {
                    const value = countInput.value.trim();
                    console.log(`  ${hubName}: value="${value}", disabled=${countInput.disabled}`);
                    
                    if (!value || value === '' || parseInt(value) < 1) {
                        console.log(`  -> Setting default value for ${hubName}`);
                        countInput.value = '1';
                    }
                }
            });
        });
    }
});