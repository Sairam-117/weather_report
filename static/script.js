document.addEventListener("DOMContentLoaded", () => {
    const cityInput = document.querySelector('input[name="city"]');
    const inputWrapper = cityInput.parentElement;
    const suggestionsBox = document.createElement("div");
    suggestionsBox.id = "suggestions";
    suggestionsBox.classList.add("suggestions-dropdown");
    inputWrapper.appendChild(suggestionsBox);
    // Actually, appending to form might mess up layout if not careful with CSS.

    const sliderContainer = document.getElementById("slider-container");
    const weatherCity = document.querySelector(".weather-card h2")?.innerText;

    // --- Search Suggestions ---
    let debounceTimer;
    cityInput.addEventListener("input", (e) => {
        const query = e.target.value.trim();
        clearTimeout(debounceTimer);

        if (query.length < 3) {
            suggestionsBox.style.display = "none";
            return;
        }

        debounceTimer = setTimeout(() => {
            fetch(`/api/suggestions?q=${query}`)
                .then(res => res.json())
                .then(data => {
                    suggestionsBox.innerHTML = "";
                    if (data.length > 0) {
                        suggestionsBox.style.display = "block";
                        data.forEach(city => {
                            const div = document.createElement("div");
                            div.classList.add("suggestion-item");
                            div.innerText = city;
                            div.addEventListener("click", () => {
                                cityInput.value = city;
                                suggestionsBox.style.display = "none";
                                // Trigger search
                                cityInput.closest("form").submit();
                            });
                            suggestionsBox.appendChild(div);
                        });
                    } else {
                        suggestionsBox.style.display = "none";
                    }
                })
                .catch(err => console.error("Error fetching suggestions:", err));
        }, 300);
    });

    // Hide suggestions when clicking outside
    document.addEventListener("click", (e) => {
        if (!cityInput.contains(e.target) && !suggestionsBox.contains(e.target)) {
            suggestionsBox.style.display = "none";
        }
    });

    // --- Image Slider ---
    function fetchImages(query) {
        // Queries: "City skyline", "City cityscape"
        const searchQuery = `${query} skyline`;

        fetch(`/api/images?query=${encodeURIComponent(searchQuery)}`)
            .then(res => res.json())
            .then(images => {
                if (images.length > 0) {
                    renderSlider(images);
                } else {
                    renderFallback();
                }
            })
            .catch(err => {
                console.error("Error fetching images:", err);
                renderFallback();
            });
    }

    function renderSlider(images) {
        sliderContainer.innerHTML = "";
        images.forEach((img, index) => {
            const slide = document.createElement("div");
            slide.classList.add("slide");
            if (index === 0) slide.classList.add("active");

            // Image
            const imgEl = document.createElement("img");
            imgEl.src = img.url;
            imgEl.alt = img.alt;

            // Attribution
            const attr = document.createElement("div");
            attr.classList.add("attribution");
            attr.innerHTML = `Photo by <a href="${img.credit_url}?utm_source=weather_app&utm_medium=referral" target="_blank">${img.credit}</a> on <a href="https://unsplash.com/?utm_source=weather_app&utm_medium=referral" target="_blank">Unsplash</a>`;

            slide.appendChild(imgEl);
            slide.appendChild(attr);
            sliderContainer.appendChild(slide);
        });

        startSlider();
    }

    function renderFallback() {
        sliderContainer.innerHTML = `<div class="slide active"><div class="fallback-text">Weather Vibes</div></div>`;
    }

    let searchInterval;
    function startSlider() {
        if (searchInterval) clearInterval(searchInterval);
        const slides = document.querySelectorAll(".slide");
        if (slides.length <= 1) return;

        let currentSlide = 0;
        searchInterval = setInterval(() => {
            slides[currentSlide].classList.remove("active");
            currentSlide = (currentSlide + 1) % slides.length;
            slides[currentSlide].classList.add("active");
        }, 5000); // 5 seconds
    }

    // Initial load
    if (weatherCity) {
        fetchImages(weatherCity);
    } else {
        // Default nature query
        fetchImages("Nature landscape");
    }
});
