document.addEventListener('DOMContentLoaded', function () {
    const universalCheckbox = document.querySelector('#id_is_universal');
    const modelSelector = document.querySelector('#id_bike_models_from'); // Django admin left-side selector

    function toggleBikeModelField() {
        if (universalCheckbox.checked) {
            modelSelector.closest('.selector').style.display = 'none';  // hide bike model field
        } else {
            modelSelector.closest('.selector').style.display = '';
        }
    }

    if (universalCheckbox && modelSelector) {
        toggleBikeModelField();  // on load
        universalCheckbox.addEventListener('change', toggleBikeModelField);  // on change
    }
});

