$(document).ready(function () {
  $(".cancel-delete").on("click", function () {
    $(".confirm-delete").hide();
  });
  const contextMenu = document.querySelector(".wrapper");
  function hideContextMenu() {
    contextMenu.style.visibility = "hidden";
    contextMenu.style.display = "none";
  }
  $(document).on("click", function () {
    hideContextMenu();
  });
});
function setMenuPos(e, menu) {
  let x = e.pageX,
    y = e.pageY,
    winWidth = window.innerWidth,
    winHeight = window.innerHeight,
    cmWidth = menu.offsetWidth,
    cmHeight = menu.offsetHeight;
  x = x > winWidth - cmWidth ? winWidth - cmWidth - 5 : x;
  y = y > winHeight - cmHeight ? winHeight - cmHeight - 5 : y;
  menu.style.left = `${x}px`;
  menu.style.top = `${y}px`;
  menu.style.visibility = "visible";
  menu.style.display = "block";
}
function showContextMenu(e, menu, id, name) {
  setMenuPos(e, menu);
  // Store the folder id in the context me
  menu.dataset.Id = id;
  menu.dataset.Name = name;
}
