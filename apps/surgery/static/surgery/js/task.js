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
          $("#task-body").append("<p>No tasks</p>");
        }
        //append the result to the table
        result.forEach(function (item) {
          $("#task-body").after(`
          <div class="row">
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
              <span class="cell" data-label="task_status">
              <i class="material-icons icon-${getIconName(item.task_status)}">
              ${getIconName(item.task_status)}</i>
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
});
