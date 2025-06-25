document.addEventListener('DOMContentLoaded', function () {
    const universalCheckbox = document.getElementById('id_is_universal');
    const bikeModelBox = document.getElementById('id_bike_models');

    function toggleBikeModels() {
        const disabled = universalCheckbox.checked;
        bikeModelBox.disabled = disabled;
    }

    if (universalCheckbox && bikeModelBox) {
        toggleBikeModels();
        universalCheckbox.addEventListener('change', toggleBikeModels);
    }
});
