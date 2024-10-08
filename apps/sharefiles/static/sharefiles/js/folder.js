$(document).ready(function () {
  var crr_page = 1;
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
              " title=" +
              folder.name +
              ">" +
              `<a href="/easyshare/file_list/${folder.id}">` +
              '<span class="material-icons">folder</span></a><li>' +
              folder.name +
              //update the href to the folder detail page
              "</li></div>"
          );
        });
        // Display pagination links
        displayPagination(data, currentPage);
        return currentPage;
      },
      error: function (error) {
        //get status code from error
        if (error.status === 403) {
          window.location.href = "/user/login";
        }
        console.error(error);
      },
    });
  }
  function displayPagination(data, currentPage) {
    showPageButton(data, currentPage);

    // Handle pagination link clicks
    $(".pagination-link").on("click", function (e) {
      e.preventDefault();
      var nextPage = $(this).attr("page");
      crr_page = loadFolders(parseInt(nextPage));
    });
  }

  var folderId = window.location.pathname.split("/").pop();
  var page = 1; // Default to the first page
  // Load folders on page load
  crr_page = loadFolders(page);

  // Show create folder modal on button click
  $("#create-folder-btn").on("click", function () {
    $("#create-folder-modal").show();
  });

  // Hide create folder modal on cancel button click
  $("#cancel-folder").on("click", function () {
    $("#create-folder-modal").hide();
  });

  // Submit new folder on button click or enter key press
  $("#submit-folder").on("click", function () {
    var folderName = $("#folder-name").val();
    createFolder(folderName);
  });

  $("#folder-name").on("keypress", function (e) {
    if (e.which === 13) {
      var folderName = $("#folder-name").val();
      createFolder(folderName);
    }
  });

  function createFolder(folderName) {
    if (folderName) {
      // get current page
      $.ajax({
        url: "/easyshare/folder/user", // Replace with your actual DRF endpoint
        method: "POST",
        data: { name: folderName, password: "123" },
        beforeSend: function (xhr, settings) {
          xhr.setRequestHeader("X-CSRFToken", getCSRFToken());
        },
        statusCode: {
          200: function () {
            crr_page = loadFolders(crr_page);
            showNotification(
              "success",
              "Success",
              "Folder created successfully"
            );
          },
          201: function () {
            showNotification(
              "info",
              "Info",
              "Folder name exists, please choose another name"
            );
          },
          400: function () {
            showNotification("error", "Error", "Folder name cannot be empty");
          },
          403: function () {
            showNotification(
              "error",
              "Error",
              "You are not authorized to create a folder"
            );
            window.location.href = "/";
          },
        },
        error: function (error) {
          showNotification("error", "Error", "An error occurred");
          console.error(error);
        },
        complete: function () {
          $("#create-folder-modal").hide();
        },
      });
    }
  }

  const contextMenu = document.querySelector(".wrapper");
  // Handle right-click events
  $(document).on("contextmenu", ".folder", function (e) {
    e.preventDefault();
    var folder_id = $(this).data("folder-id");
    var folder_name = $(this).data("folder-name");
    console.log("Right-clicked on folder name: ", folder_name);
    showContextMenu(e, contextMenu, folder_id, folder_name);
  });

  // delete folder
  const confirmDialog = document.getElementsByClassName("confirm-delete")[0];
  $("#delete-folder").on("click", function () {
    // display the confirm dialog
    confirmDialog.style.display = "block";
    var folderName = contextMenu.dataset.Name;
    const folderNameElement = document.getElementById("delete-folder-name");
    folderNameElement.innerHTML = folderName;
  });

  $("#confirm-delete-btn").on("click", function () {
    var folderId = contextMenu.dataset.Id;
    // Implement the logic to delete the file with fileId
    $.ajax({
      url: `/easyshare/folder_remove/${folderId}`,
      method: "DELETE",
      beforeSend: function (xhr, settings) {
        xhr.setRequestHeader("X-CSRFToken", getCSRFToken());
      },
      success: function () {
        confirmDialog.style.display = "none";
        crr_page = loadFolders(crr_page); // After deletion, reload the files
        showNotification("success", "Success", "Folder deleted successfully");
      },
      error: function (error) {
        console.error(error);
        showNotification("error", "Error", "An error occurred");
      },
    });
  });

  // rename folder
  const renameFolderModal = document.getElementById("rename-folder-modal");
  $("#rename-folder").on("click", function () {
    renameFolderModal.style.display = "block";
  });

  function renameFolder() {
    var folderName = $("#new-folder-name").val();
    var folderId = contextMenu.dataset.Id;
    if (folderName) {
      $.ajax({
        url: `/easyshare/folder_rename/${folderId}`,
        method: "GET",
        data: { name: folderName },
        beforeSend: function (xhr, settings) {
          xhr.setRequestHeader("X-CSRFToken", getCSRFToken());
        },
        success: function () {
          renameFolderModal.style.display = "none";
          crr_page = loadFolders(crr_page); // After renaming, reload the files
          showNotification("success", "Success", "Folder renamed successfully");
        },
        error: function (error) {
          console.error(error);
          showNotification("error", "Error", "An error occurred");
        },
      });
    }
  }

  $("#confirm-rename-folder").on("click", function () {
    renameFolder();
  });

  $("#cancel-rename-btn").on("click", function () {
    renameFolderModal.style.display = "none";
  });

  $("#new-folder-name").on("keypress", function (e) {
    if (e.which === 13) {
      renameFolder();
    }
  });
});
