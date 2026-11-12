const button = document.querySelector(".menu-button");
const sidebar = document.querySelector(".sidebar");
const backdrop = document.querySelector(".backdrop");

function setMenu(open) {
  sidebar.classList.toggle("open", open);
  backdrop.hidden = !open;
  button.setAttribute("aria-expanded", String(open));
  document.body.classList.toggle("menu-open", open);
}

button.addEventListener("click", () => setMenu(!sidebar.classList.contains("open")));
backdrop.addEventListener("click", () => setMenu(false));
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape") setMenu(false);
});
