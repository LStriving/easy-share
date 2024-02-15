// static/js/folder.js
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
      url: `/easyshare/folder/user?page=${currentPage}`, // Replace with your actual DRF endpoint
      method: "GET",
      success: function (data) {
        $("#folder-list").empty();
        data.results.forEach(function (folder) {
          $("#folder-list").append(
            '<div class="folder">' +
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
});
