// static/js/view_files.js
$(document).ready(function () {
  //function to get folder name
  function getFolderName(folderId) {
    $.ajax({
      url: `/easyshare/folder/${folderId}`,
      method: "GET",
      success: function (data) {
        $("#folder-name").text(data.name);
      },
      error: function (error) {
        console.error(error);
      },
    });
  }
  // Function to load files
  function loadFiles(folderId, page = 1) {
    $.ajax({
      url: `/easyshare/folder_detail/${folderId}?page=${page}`,
      method: "GET",
      success: function (data) {
        $("#file-list").empty();
        // if it is empty, display a message
        if (data.results.length === 0) {
          $("#file-list").append("<p>No files in this folder</p>");
        }
        data.results.forEach(function (file) {
          $("#file-list").append(
            `<div class=folder data-file-id=${file.id} data-file-name=${file.name}>` +
              '<i class="material-icons">video_file</i><li>' +
              file.name +
              "</li></div>"
          );
        });
        // Display pagination links
        displayPagination(data, folderId, page);
      },
      error: function (error) {
        console.error(error);
      },
    });
  }
  function displayPagination(data, folderId, currentPage) {
    showPageButton(data, currentPage);
    // Handle pagination link clicks
    $(".pagination-link").on("click", function (e) {
      e.preventDefault();
      var nextPage = $(this).attr("page");
      loadFiles(folderId, parseInt(nextPage));
    });
  }

  // Load files on page load
  var folderId = window.location.pathname.split("/").pop();
  var page = 1;
  getFolderName(folderId);
  loadFiles(folderId, page);

  // Go back to folders on button click
  $("#go-back-btn").on("click", function () {
    window.location.href = "/easyshare/folder_list";
  });

  // Upload new file on button click
  $("#upload-btn").on("click", function () {
    // display the #upload-file div
    document.getElementById("upload-file").style.display = "block";
    // place the z-index of the #upload-file div above all other divs and elements
    document.getElementById("upload-file").style.zIndex = "100";
    //blur the website except the upload file div
    $("body div:not(#upload-file)").css("filter", "blur(6px)");
  });

  // Cancel upload on button click
  $("#cancel-upload-btn").on("click", function () {
    // hide the #upload-file div
    document.getElementById("upload-file").style.display = "none";
    $("body div:not(#upload-file)").css("filter", "blur(0px)");
  });

  const contextMenu = document.querySelector(".wrapper");
  // Handle right-click events
  $(document).on("contextmenu", ".folder", function (e) {
    e.preventDefault();
    var file_id = $(this).data("file-id");
    var file_name = $(this).data("file-name");
    console.log("Right-clicked on file name: ", file_name);
    showContextMenu(e, contextMenu, file_id, file_name);
  });

  const confirmDialog = document.getElementsByClassName("confirm-delete")[0];
  // menu actions
  // delete file
  $("#delete-file").on("click", function () {
    var fileName = contextMenu.dataset.Name;
    confirmDialog.style.display = "block";
    const fileNameElement = document.getElementById("delete-file-name");
    fileNameElement.innerHTML = fileName;
  });
  $(".confirm-delete-btn").on("click", function () {
    var fileId = contextMenu.dataset.Id;
    $.ajax({
      url: `/easyshare/large_file_remove`,
      method: "DELETE",
      data: { file_id: fileId },
      beforeSend: function (xhr, settings) {
        xhr.setRequestHeader("X-CSRFToken", getCSRFToken());
      },
      success: function () {
        confirmDialog.style.display = "none";
        loadFiles(folderId, page);
        showNotification("success", "Success", "File deleted successfully");
      },
      error: function (error) {
        confirmDialog.style.display = "none";
        console.error(error);
        showNotification("error", "Error", "An error occurred");
      },
    });
  });
  // preview file
  $("#preview-file").on("click", function () {
    var name = contextMenu.dataset.Name;
    // get folder name
    var folderName = $("#folder-name").text();
    url = `/media/uploads/${folderName}/${name}`;
    window.open(url, "_blank");
  });
});
