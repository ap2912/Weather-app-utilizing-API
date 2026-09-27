/* Weather / Now — frontend logic (vanilla JS).
 * The browser never touches the weather API directly;
 * everything goes through the Flask backend at /api/weather.
 */
(function () {
  "use strict";

  const form = document.getElementById("searchForm");
  const input = document.getElementById("cityInput");
  const button = document.getElementById("checkBtn");
  const statusEl = document.getElementById("status");
  const resultEl = document.getElementById("result");
  const errorBlock = document.getElementById("errorBlock");
  const errorTitle = document.getElementById("errorTitle");
  const errorText = document.getElementById("errorText");

  let inFlight = false; // prevents duplicate requests

  // Header date: DD.MM.YY
  document.getElementById("date").textContent =
    new Date().toLocaleDateString("en-GB").replaceAll("/", ".");

  function setStatus(text, loading = false) {
    statusEl.textContent = text;
    statusEl.classList.toggle("loading", loading);
  }

  function hidePanels() {
    resultEl.classList.remove("visible");
    errorBlock.classList.remove("visible");
    errorBlock.hidden = true;
  }

  function showError(title, text) {
    hidePanels();
    errorTitle.textContent = title;
    errorText.textContent = text;
    errorBlock.hidden = false;
    // Restart the fade/slide animation
    void errorBlock.offsetWidth;
    errorBlock.classList.add("visible");
  }

  function render(data) {
    document.getElementById("cityName").textContent =
      `${data.city}, ${data.country}`;
    document.getElementById("temp").textContent = data.temperature;
    document.getElementById("condition").textContent = data.condition;
    document.getElementById("humidity").textContent = data.humidity;
    document.getElementById("feelsLike").textContent = data.feels_like;
    document.getElementById("wind").textContent = data.wind_speed;
    document.getElementById("timezone").textContent =
      String(data.timezone).toUpperCase();
    document.getElementById("dayNight").textContent =
      data.is_day ? "DAY" : "NIGHT";
    document.getElementById("dayDot").classList.toggle("night", !data.is_day);

    hidePanels();
    // Restart the fade/slide animation
    void resultEl.offsetWidth;
    resultEl.classList.add("visible");
  }

  async function checkWeather(event) {
    event.preventDefault();
    if (inFlight) return;

    const city = input.value.trim();
    if (!city) {
      showError("CITY NOT FOUND",
        "Please type a city name — the input was empty.");
      input.focus();
      return;
    }

    inFlight = true;
    button.disabled = true;
    setStatus("FETCHING WEATHER", true);

    try {
      const response = await fetch(
        `/api/weather?city=${encodeURIComponent(city)}`
      );
      const payload = await response.json();

      if (!response.ok) {
        if (payload.error === "city_not_found" || response.status === 404) {
          showError("CITY NOT FOUND",
            "We couldn't find that location. Try searching for another city.");
        } else {
          showError("WEATHER SERVICE UNAVAILABLE", "Please try again.");
        }
        return;
      }

      setStatus("");
      render(payload);
    } catch (err) {
      // Network failure, timeout, or malformed JSON
      showError("WEATHER SERVICE UNAVAILABLE", "Please try again.");
    } finally {
      inFlight = false;
      button.disabled = false;
      setStatus("", false);
    }
  }

  form.addEventListener("submit", checkWeather);
  input.focus();
})();
