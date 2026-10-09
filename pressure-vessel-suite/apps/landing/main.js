const APP_URL = "https://pv-suite-app.vercel.app";

document.querySelectorAll("[data-app-link]").forEach((link) => {
  link.href = APP_URL;
});

const menuButton = document.querySelector(".menu-toggle");
const nav = document.querySelector("#main-nav");
if (menuButton && nav) {
  menuButton.addEventListener("click", () => {
    const open = menuButton.getAttribute("aria-expanded") !== "true";
    menuButton.setAttribute("aria-expanded", String(open));
    nav.classList.toggle("open", open);
  });
  nav.addEventListener("click", (event) => {
    if (event.target.closest("a")) {
      menuButton.setAttribute("aria-expanded", "false");
      nav.classList.remove("open");
    }
  });
}

document.querySelectorAll("[data-year]").forEach((node) => {
  node.textContent = String(new Date().getFullYear());
});
