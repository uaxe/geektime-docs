// Apply theme colors based on dark/light mode
const applyTheme = (isDark) => {
  document.body.setAttribute(
    "data-md-color-scheme",
    isDark ? "slate" : "default",
  );
  document.body.setAttribute(
    "data-md-color-primary",
    isDark ? "black" : "indigo",
  );
};

// Check and apply appropriate theme based on system/user preference
const checkTheme = () => {
  const palette = JSON.parse(localStorage.getItem(".__palette") || "{}");
  if (palette.index === 0) {
    // Auto mode is selected
    applyTheme(window.matchMedia("(prefers-color-scheme: dark)").matches);
  }
};

// Watch for system theme changes
window
  .matchMedia("(prefers-color-scheme: dark)")
  .addEventListener("change", checkTheme);

// Initialize theme handling on page load
document.addEventListener("DOMContentLoaded", () => {
  // Watch for theme toggle changes
  document
    .getElementById("__palette_1")
    ?.addEventListener(
      "change",
      (e) => e.target.checked && setTimeout(checkTheme),
    );
  // Initial theme check
  checkTheme();
});

// Inkeep --------------------------------------------------------------------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
  const enableSearchBar = true;

  const inkeepScript = document.createElement("script");
  inkeepScript.src = "https://unpkg.com/@inkeep/uikit-js@0.3.18/dist/embed.js";
  inkeepScript.type = "module";
  inkeepScript.defer = true;
  document.head.appendChild(inkeepScript);

  if (enableSearchBar) {
    const containerDiv = document.createElement("div");
    containerDiv.style.transform = "scale(0.7)";
    containerDiv.style.transformOrigin = "left center";

    const inkeepDiv = document.createElement("div");
    inkeepDiv.id = "inkeepSearchBar";
    containerDiv.appendChild(inkeepDiv);

    const headerElement = document.querySelector(".md-header__inner");
    const searchContainer = headerElement.querySelector(".md-header__source");

    if (headerElement && searchContainer) {
      headerElement.insertBefore(containerDiv, searchContainer);
    }
  }

});
