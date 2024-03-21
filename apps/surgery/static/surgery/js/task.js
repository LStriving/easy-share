$(document).ready(function () {
  // request to server to get the task list and show it in the table
  function getTaskList(page = 1) {
    $.ajax({
      url: `/surgery/task_list?page=${page}`,
      type: "GET",
      success: function (data) {
        //get `result` from data
        var result = data.results;
        //clear the table
        $(".row").empty();
        if (result.length === 0) {
          $("#task-body").append(
            `<div class="row"><input type="radio" name="expand" /><span class="cell" data-label="task_result_url">No tasks</span></div>`
          );
        }
        //append the result to the table
        result.forEach(function (item) {
          $("#task-body").after(`
          <div class="row" data-task-id="${item.id}">
              <input type="radio" name="expand" />
              <span class="cell primary" data-label="file">${item.file}</span>
              <span class="cell" data-label="task_name">${
                item.task_name || " "
              }</span>
              <span class="cell" data-label="task_created_time">${
                formatDateTime(item.task_created_time) || " "
              }</span>
              <span class="cell" data-label="task_result_url">${
                item.task_result_url || " "
              }</span>
              <span class="cell icon-${getIconName(
                item.task_status
              )}" data-label="task_status">
              <span class="material-icons">
              ${getIconName(item.task_status)}</span>
              ${item.task_status}</span>
          </div>
          `);
        });
        //display pagination links
        displayPagination(data, page);
      },
      error: function (error) {
        showNotification("error", "Error", "An error occurred");
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
      getTaskList(parseInt(nextPage));
    });
  }
  function formatDateTime(time) {
    var date = new Date(time);
    var time = date.toLocaleTimeString();
    return date.toLocaleDateString() + " " + time;
  }
  function getIconName(status) {
    if (status === "doing" || status === "executing") {
      return "rocket_launch";
    } else if (status === "extracting frames") {
      return "auto_awesome_motion";
    } else if (status === "SEG inferring" || status === "OAD inferring") {
      return "online_prediction";
    } else return status;
  }
  //get the task list
  getTaskList();
  //refresh the task list every 10 seconds
  //   setInterval(getTaskList, 10000);
  function appendContextMenuItems(id, icon, text) {
    if (document.getElementById(id)) {
      return;
    }
    $("#delete-task").after(
      `<li class="item" id="${id}">
      <span class="material-icons w3-xlarge">${icon}</span>
      <span>${text}</span>
    </li>`
    );
    $("#retry-task").on("click", function () {
      var taskId = contextMenu.dataset.Id;
      console.log("Retry task: ", taskId);
      $.ajax({
        url: `/surgery/retry_task/${taskId}`,
        method: "GET",
        beforeSend: function (xhr, settings) {
          xhr.setRequestHeader("X-CSRFToken", getCSRFToken());
        },
        statusCode: {
          200: function () {
            showNotification("success", "Success", "Task retried");
            getTaskList();
          },
          400: function () {
            showNotification(
              "warning",
              "Warning",
              "Unable to retry a launching task"
            );
          },
          404: function () {
            showNotification("error", "Error", "Task not found");
          },
          403: function () {
            showNotification("error", "Error", "Permission denied");
          },
          500: function () {
            showNotification("error", "Error", "An error occurred");
          },
        },
        error: function (error) {
          console.error(error);
          showNotification("error", "Error", "An error occurred");
        },
      });
    });
  }
  const contextMenu = document.querySelector(".wrapper");
  // Handle right-click events
  $(document).on("contextmenu", ".row", function (e) {
    e.preventDefault();
    // get the task id and task name from data-label
    var task_id = $(this).data("task-id");
    var task_name = $(this).find("[data-label=task_name]").text();
    var task_status = $(this).find("[data-label=task_status]").text();
    if (task_status.includes("error")) {
      appendContextMenuItems("retry-task", "replay", "Retry");
    }
    console.log("Right-clicked on task name: ", task_name);
    showContextMenu(e, contextMenu, task_id, task_name);
  });

  const confirmDialog = document.getElementsByClassName("confirm-delete")[0];
  $("#delete-task").on("click", function () {
    // display the confirm dialog
    confirmDialog.style.display = "block";
    var taskName = contextMenu.dataset.Name;
    const taskNameElement = document.getElementById("delete-task-name");
    taskNameElement.innerHTML = taskName;
  });

  $("#confirm-delete-btn").on("click", function () {
    var taskId = contextMenu.dataset.Id;
    // Implement the logic to delete the file with fileId
    $.ajax({
      url: `/surgery/remove_task/${taskId}`,
      method: "DELETE",
      beforeSend: function (xhr, settings) {
        xhr.setRequestHeader("X-CSRFToken", getCSRFToken());
      },
      statusCode: {
        204: function () {
          confirmDialog.style.display = "none";
          showNotification("success", "Success", "Task deleted");
          getTaskList();
        },
        400: function () {
          confirmDialog.style.display = "none";
          showNotification(
            "warning",
            "Warning",
            "Unable to delete a launching task"
          );
        },
        404: function () {
          confirmDialog.style.display = "none";
          showNotification("error", "Error", "Task not found");
        },
        500: function () {
          confirmDialog.style.display = "none";
          showNotification("error", "Error", "An error occurred");
        },
      },
      error: function (error) {
        confirmDialog.style.display = "none";
        console.error(error);
        showNotification("error", "Error", "An error occurred");
      },
    });
  });
});
