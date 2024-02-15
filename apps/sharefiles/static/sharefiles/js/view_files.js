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
            "<div class=folder> " +
              '<i class="material-icons">video_file</i><li>' +
              file.name +
              "</li></div>"
          );
        });
        // Display pagination links
        displayPagination(data, page);
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
    console.log(totalPages, currentPage);
    $("#pagination-links").empty();
    if (currentPage < totalPages) {
      $("#pagination-links").append(
        '<a href="?" class="pagination-link" page="' +
          (currentPage + 1) +
          '">Next</a>'
      );
    }
    if (currentPage > 1) {
      $("#pagination-links").append(
        '<a href="?" class="pagination-link" page="' +
          (currentPage - 1) +
          '">Previous</a>'
      );
    }

    // Handle pagination link clicks
    $(".pagination-link").on("click", function (e) {
      e.preventDefault();
      var nextPage = $(this).data("page");
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
  $("#upload-file-btn").on("click", function () {
    var fileInput = document.getElementById("file-upload");
    var file = fileInput.files[0];
    if (file) {
      var formData = new FormData();
      formData.append("file", file);

      $.ajax({
        url: `/api/files/?folder=${folderId}`,
        method: "POST",
        data: formData,
        processData: false,
        contentType: false,
        beforeSend: function (xhr, settings) {
          xhr.setRequestHeader("X-CSRFToken", getCSRFToken());
        },
        success: function () {
          loadFiles(folderId, page); // Reload files after upload
        },
        error: function (error) {
          console.error(error);
        },
      });
    }
  });
});
