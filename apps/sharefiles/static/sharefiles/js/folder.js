$(document).ready(function () {
  // Function to get CSRF token from cookies
  function getCSRFToken() {
    var csrfToken = null;
    var cookies = document.cookie.split(";");
    for (var i = 0; i < cookies.length; i++) {
      var cookie = cookies[i].trim();
      if (cookie.startsWith("csrftoken=")) {
        csrfToken = cookie.substring("csrftoken=".length, cookie.length);
        break;
      }
    }
    return csrfToken;
  }
  // Function to load folders
  function loadFolders(currentPage = 1) {
    $.ajax({
      url: `/easyshare/folder/user?page=${currentPage}`,
      method: "GET",
      success: function (data) {
        $("#folder-list").empty();
        data.results.forEach(function (folder) {
          $("#folder-list").append(
            '<div class="folder" data-folder-id=' +
              folder.id +
              " data-folder-name=" +
              folder.name +
              ">" +
              `<a href="/easyshare/file_list/${folder.id}">` +
              '<i class="material-icons">folder</i></a><li>' +
              folder.name +
              //update the href to the folder detail page
              "</li></div>"
          );
        });
        // Display pagination links
        displayPagination(data, currentPage);
      },
      error: function (error) {
        console.error(error);
      },
    });
  }
  function displayPagination(data, currentPage) {
    var totalPages = parseInt(data.count / 10);
    if (data.count % 10) {
      totalPages += 1;
    }

    $("#pagination-links").empty();
    if (currentPage > 1) {
      $("#pagination-links").append(
        '<a href="?" class="pagination-link" page="' +
          (currentPage - 1) +
          '">Previous</a>'
      );
    }
    if (currentPage < totalPages) {
      $("#pagination-links").append(
        '<a href="?" class="pagination-link" page="' +
          (currentPage + 1) +
          '">Next</a>'
      );
    }

    // Handle pagination link clicks
    $(".pagination-link").on("click", function (e) {
      e.preventDefault();
      var nextPage = $(this).attr("page");
      loadFolders(parseInt(nextPage));
    });
  }

  var folderId = window.location.pathname.split("/").pop();
  var page = 1; // Default to the first page
  // Load folders on page load
  loadFolders(page);

  // Show create folder modal on button click
  $("#create-folder-btn").on("click", function () {
    $("#create-folder-modal").show();
  });

  // Hide create folder modal on cancel button click
  $("#cancel-folder").on("click", function () {
    $("#create-folder-modal").hide();
  });

  // Submit new folder on button click
  $("#submit-folder").on("click", function () {
    var folderName = $("#folder-name").val();
    if (folderName) {
      $.ajax({
        url: "/easyshare/folder/user", // Replace with your actual DRF endpoint
        method: "POST",
        data: { name: folderName, password: "123" },
        beforeSend: function (xhr, settings) {
          xhr.setRequestHeader("X-CSRFToken", getCSRFToken());
        },
        success: function () {
          $("#create-folder-modal").hide();
          loadFolders(); // Reload folders after creation
        },
        error: function (error) {
          console.error(error);
        },
      });
    }
  });

  const contextMenu = document.querySelector(".wrapper");
  // Handle right-click events
  $(document).on("contextmenu", ".folder", function (e) {
    e.preventDefault();
    var folder_id = $(this).data("folder-id");
    var folder_name = $(this).data("folder-name");
    console.log("Right-clicked on folder name: ", folder_name);
    showContextMenu(e, folder_id, folder_name);
  });

  // Close context menu on click outside
  $(document).on("click", function () {
    hideContextMenu();
  });
  // Context menu functions
  function showContextMenu(e, folderId, folderName) {
    let x = e.pageX,
      y = e.pageY,
      winWidth = window.innerWidth,
      winHeight = window.innerHeight,
      cmWidth = contextMenu.offsetWidth,
      cmHeight = contextMenu.offsetHeight;
    x = x > winWidth - cmWidth ? winWidth - cmWidth - 5 : x;
    y = y > winHeight - cmHeight ? winHeight - cmHeight - 5 : y;
    contextMenu.style.left = `${x}px`;
    contextMenu.style.top = `${y}px`;
    contextMenu.style.visibility = "visible";
    contextMenu.style.display = "block";
    // Store the folder id in the context me
    contextMenu.dataset.folderId = folderId;
    contextMenu.dataset.folderName = folderName;
  }

  function hideContextMenu() {
    contextMenu.style.visibility = "hidden";
    contextMenu.style.display = "none";
  }

  $("#delete-folder").on("click", function () {
    var folderId = contextMenu.dataset.folderId;
    var folderName = contextMenu.dataset.folderName;
    console.log("Delete folder with id: ", folderId);
    // display the confirm dialog
    const confirmDialog = document.getElementById("confirm-delete");
    confirmDialog.style.display = "block";
    const folderNameElement = document.getElementById("delete-folder-name");
    folderNameElement.innerHTML = folderName;

    $("#confirm-delete-btn").on("click", function () {
      // Implement the logic to delete the file with fileId
      $.ajax({
        url: `/easyshare/folder_remove/${folderId}`,
        method: "DELETE",
        beforeSend: function (xhr, settings) {
          xhr.setRequestHeader("X-CSRFToken", getCSRFToken());
        },
        success: function () {
          confirmDialog.style.display = "none";
          loadFolders(page); // After deletion, reload the files
        },
        error: function (error) {
          console.error(error);
        },
      });
      // After deletion, reload the files
      loadFolders(page);
    });
  });

  $("#cancel-delete").on("click", function () {
    $("#confirm-delete").hide();
  });
});
