let hideAdButton = document.querySelector('.ad-header button');
let hideAdButton2 = document.querySelector('.ad-header-2 button');

hideAdButton.addEventListener('click', () => {
    let adSection = document.getElementById('advertisement-slide');
    adSection.style.display = "none";
    //No social media actually hides ads forever
    setTimeout(() => {
        adSection.style.display = "block";
    }, 15000)
})
hideAdButton2.addEventListener('click', () => {
    let adSection = document.getElementById('advertisement-slide-2');
    adSection.style.display = "none";
    //No social media actually hides ads forever
    setTimeout(() => {
        adSection.style.display = "block";
    }, 15000)
})

// Day la phan backend

