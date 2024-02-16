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
        displayPagination(data, folderId, page);
      },
      error: function (error) {
        console.error(error);
      },
    });
  }
  function displayPagination(data, folderId, currentPage) {
    var totalPages = parseInt(data.count / 10);
    if (data.count % 10) {
      totalPages += 1;
    }
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
    //blur the website except the upload file div
    $("body div:not(#upload-file)").css("filter", "blur(6px)");
  });

  // Cancel upload on button click
  $("#cancel-upload-btn").on("click", function () {
    // hide the #upload-file div
    document.getElementById("upload-file").style.display = "none";
    $("body div:not(#upload-file)").css("filter", "blur(0px)");
  });
});
