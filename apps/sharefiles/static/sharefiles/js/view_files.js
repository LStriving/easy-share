// static/js/view_files.
function visit(url) {
  window.open(url, "_blank");
}
function toggleLang(language) {
  if (language === "en") {
    document.getElementById("en-hints").style.display = "block";
    document.getElementById("zh-hints").style.display = "none";
  } else if (language === "zh") {
    document.getElementById("en-hints").style.display = "none";
    document.getElementById("zh-hints").style.display = "block";
  }
}
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
            `<div onclick=visit('${file.upload}'); class=folder data-file-id=${file.id} data-file-name=${file.name} data-url=${file.upload} title=${file.name}>` +
              '<span class="material-icons">video_file</span><li>' +
              file.name +
              "</li></div>"
          );
        });
        // Display pagination links
        displayPagination(data, folderId, page);
      },
      error: function (error) {
        showNotification("error", "Error", "An error occurred");
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
    $("body div:not(#upload-file,.upload-hints)").css("filter", "blur(6px)");
  });

  // Cancel upload on button click
  $("#cancel-upload-btn").on("click", function () {
    // hide the #upload-file div
    document.getElementById("upload-file").style.display = "none";
    $("body div:not(#upload-file,.upload-hints)").css("filter", "blur(0px)");
  });

  const contextMenu = document.querySelector(".wrapper");
  // Handle right-click events
  $(document).on("contextmenu", ".folder", function (e) {
    e.preventDefault();
    var file_id = $(this).data("file-id");
    var file_name = $(this).data("file-name");
    console.log("Right-clicked on file name: ", file_name);
    showContextMenu(e, contextMenu, file_id, file_name);
    contextMenu.dataset.url = $(this).data("url");
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
      url: `/easyshare/large_file_remove?folder_id=${folderId}`,
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
    //get url from the div's onlick
    var url = contextMenu.dataset.url;
    visit(url);
  });
  // add task
  $("#add-task").on("click", function () {
    $("#add-task-modal").show();
  });
  // close the modal
  $("#cancel-add-task").on("click", function () {
    $("#add-task-modal").hide();
    $("#task-name").val("");
  });
  function createTask() {
    // send a post request to the server to add a task
    var fileId = contextMenu.dataset.Id;
    // get task name from the input field
    var taskName = $("#task-name").val();
    // send request
    $.ajax({
      url: "/surgery/add_task",
      method: "POST",
      data: { file_id: fileId, task_name: taskName },
      beforeSend: function (xhr, settings) {
        xhr.setRequestHeader("X-CSRFToken", getCSRFToken());
      },
      statusCode: {
        201: function (data) {
          showNotification("info", "Info", "Task already exists");
        },
        200: function (data) {
          showNotification("success", "Success", "Task added successfully");
        },
        400: function () {
          showNotification("error", "Error", "Bad request");
        },
        403: function () {
          showNotification("error", "Error", "You do not have permission");
        },
      },
      error: function (error) {
        // Handle other error scenarios
        console.error(error);
        showNotification("error", "Error", "An error occurred");
      },
      // clear the input field and hide the modal
      complete: function () {
        $("#task-name").val("");
        $("#add-task-modal").hide();
      },
    });
  }
  // add task button
  $("#add-task-btn").on("click", function () {
    createTask();
  });
  // keypress event for the task name input field
  $("#task-name").on("keypress", function (e) {
    if (e.which === 13) {
      createTask();
    }
  });
});
