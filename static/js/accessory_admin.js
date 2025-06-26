document.addEventListener('DOMContentLoaded', function () {
    const universalCheckbox = document.querySelector('#id_is_universal');
    const modelSelector = document.querySelector('#id_bike_models_from'); // fix typo here

    function toggleBikeModelField() {
        if (universalCheckbox.checked) {
            modelSelector.closest('.selector').style.display = 'none';  // hide bike model selector box
        } else {
            modelSelector.closest('.selector').style.display = '';
        }
    }

    if (universalCheckbox && modelSelector) {
        toggleBikeModelField();  // run once on load
        universalCheckbox.addEventListener('change', toggleBikeModelField);  // and on change
    }
});
