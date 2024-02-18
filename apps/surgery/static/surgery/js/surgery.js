const actionNames = [
  "Carbachol injection",
  "OVDs injection",
  "Gonioscopy",
  "Goniotomy",
  "OVDs irrigation/aspiration",
  "Would closure",
  "Corneal incision by 3.2 mm keratome",
  "Corneal incision by 15 degree keratome",
  "Idle",
];

const idx_map = [
  [0, 7],
  [1, 6],
  [2, 0],
  [3, 1],
  [4, 2],
  [5, 3],
  [6, 4],
  [7, 5],
  [8, 8],
];
// Function to create speaker icon
function createSpeakerIcon() {
  const icon = document.createElement("div");
  icon.className = "fas fa-volume-up speaker-icon";
  return icon;
}

// Function to play background audio
function playAlarm(alarm_id) {
  const audioElement = document.getElementById(alarm_id);
  if (audioElement.paused) {
    audioElement.play();
  }
}

document.addEventListener("DOMContentLoaded", function () {
  // Get elements
  const report_actions = document.querySelectorAll(".report-cls .time");
  const phase_actions_target = document.querySelectorAll(".recog-cls .target");
  const phase_actions_bar = document.querySelectorAll(".recog-cls .prob .bar");
  const videoElement = document.getElementById("surgeryVideo");

  // Function to update predictions based on current video time
  function updatePredictions(pred, currentTime, duration) {
    pred_sorted = [];
    pred = pred.split(" ");
    for (let i = 0; i < idx_map.length; i++) {
      pred_sorted.push(parseFloat(pred[idx_map[i][1]]));
    }
    for (let i = 0; i < pred_sorted.length; i++) {
      let target = phase_actions_target[i];
      let bar = phase_actions_bar[i];
      let prob = pred_sorted[i];

      if (prob > 0.5) {
        target.style.backgroundColor = "green";
      } else {
        target.style.backgroundColor = "red";
      }
      bar.style.width = `${prob * 100}%`;
    }
  }
  // Function to fetch data from file, parse it, and store in the provided array
  function fetchAndStoreData(filePath) {
    return fetch(filePath)
      .then((response) => response.text())
      .then((data) => {
        return parseFrames(data); // Return frames
      })
      .catch((error) =>
        console.error(`Error reading file ${filePath}:`, error)
      );
  }
  function fetchAndStorePred(filePath) {
    return fetch(filePath)
      .then((response) => response.text())
      .then((data) => {
        return parsePred(data); // Return frames
      })
      .catch((error) =>
        console.error(`Error reading file ${filePath}:`, error)
      );
  }

  Promise.all([
    fetchAndStoreData("/media/demo/interact_1_345.txt"),
    fetchAndStoreData("/media/demo/interact_8_910.txt"),
    fetchAndStorePred("/media/demo/new4.txt"),
    fetchAndStorePred("/media/demo/pred_videos_dur.txt"),
  ]).then((results) => {
    const data1 = results[0];
    const data2 = results[1];
    const pred = results[2];
    const pred_dur = results[3];

    // Check if metadata is already loaded
    if (videoElement.readyState >= 2) {
      // Metadata is already loaded, add event listener for timeupdate immediately
      registerTimeUpdateListener();
    } else {
      // Add event listener to handle when the video metadata is loaded
      videoElement.addEventListener("loadedmetadata", function () {
        console.log("Video metadata loaded");
        registerTimeUpdateListener();
      });
    }

    // Function to register timeupdate event listener
    function registerTimeUpdateListener() {
      // Add event listener for updating predictions during video playback
      videoElement.addEventListener("timeupdate", function () {
        var cur_dur = getCurrent(
          pred_dur,
          videoElement.currentTime,
          videoElement.duration
        );
        var cur_pre = getCurrent(
          pred,
          videoElement.currentTime,
          videoElement.duration
        );
        // Update summary report
        updateSummaryReport(
          cur_dur,
          videoElement.currentTime,
          pred_dur.length / videoElement.duration
        );
        updatePredictions(
          cur_pre,
          videoElement.currentTime,
          videoElement.duration
        );
        updatePredictionOnVideo(
          data1,
          data2,
          cur_pre,
          cur_dur,
          videoElement.currentTime,
          pred_dur.length / videoElement.duration
        );
        updateTimeline(cur_pre, pred.length);
      });
    }
  });

  const surgeryForm = document.getElementById("surgeryForm");
  surgeryForm.addEventListener("submit", function (event) {
    event.preventDefault(); // prevent the form from submitting normally

    // get the values of the form fields
    var surgeon = document.getElementById("surgeon").value;
    var patientID = document.getElementById("patientID").value;
    var name = document.getElementById("name").value;
    var age = document.getElementById("age").value;
    var gender = document.getElementById("gender").value;

    // create a div to hold the case information
    var caseInfoDiv = document.getElementById("caseInfoDiv");

    // increase the line height for readability
    // create a p element to hold the time info
    var timeInfo = document.createElement("p");
    timeInfo.id = "timeInfo";
    caseInfoDiv.appendChild(timeInfo);

    caseInfoDiv.innerHTML = `
          <p id="timeInfo"></p>
          <p><strong>surgeon:</strong> ${surgeon}</p>
          <p><strong>Patient ID:</strong> ${patientID}</p>
          <p><strong>Name:</strong> ${name}</p>
          <p><strong>Age:</strong> ${age}</p>
          <p><strong>Gender:</strong> ${gender}</p>
          `;

    caseInfoDiv.style.display = "block";

    // add the case information div to the video div
    var videoDiv = document.querySelector(".video");
    videoDiv.appendChild(caseInfoDiv);
    var now = new Date();
    document.getElementById("timeInfo").innerHTML =
      "<strong>CurrentTime:</strong> " +
      now.toLocaleDateString() +
      " " +
      now.toLocaleTimeString();

    // update the time info every second
    setInterval(function () {
      var now = new Date();
      document.getElementById("timeInfo").innerHTML =
        "<strong>CurrentTime:</strong> " +
        now.toLocaleDateString() +
        " " +
        now.toLocaleTimeString();
    }, 1000);
  });

  const colorBar = document.querySelector(".color-bar");
  colorBar.style.background = `linear-gradient(to right, rgb(${item_color[0][0]}, ${item_color[0][1]}, ${item_color[0][2]}), rgb(${item_color[1][0]}, ${item_color[1][1]}, ${item_color[1][2]}))`;

  const info_btn = document.querySelector(".case-btn");
  info_btn.addEventListener("click", function () {
    if (surgeryForm.style.display == "none") {
      surgeryForm.style.display = "block";
      info_btn.innerHTML = "Hide";
    } else {
      info_btn.innerHTML = "Show";
      surgeryForm.style.display = "none";
    }
  });

  // Function to update summary report based on current video time
  function updateSummaryReport(pred_dur, currentTime, ratio) {
    // Calculate durations for the whole process and different actions
    const wholeProcessDuration = formatDuration(currentTime);
    var current_dur = pred_dur;
    var current_dur_array = current_dur.split(" ");
    var current_dur_array_float = [];
    var current_dur_array_float_sorted = [];
    for (var i = 0; i < current_dur_array.length; i++) {
      current_dur_array_float.push(
        formatDuration(parseFloat(current_dur_array[i]) / ratio)
      );
    }
    // current_dur_array_float_sorted[0] = current_dur_array_float[7];
    current_dur_array_float_sorted[1] = current_dur_array_float[7];
    current_dur_array_float_sorted[2] = current_dur_array_float[6];
    current_dur_array_float_sorted[3] = current_dur_array_float[0];
    current_dur_array_float_sorted[4] = current_dur_array_float[1];
    current_dur_array_float_sorted[5] = current_dur_array_float[2];
    current_dur_array_float_sorted[6] = current_dur_array_float[3];
    current_dur_array_float_sorted[7] = current_dur_array_float[4];
    current_dur_array_float_sorted[8] = current_dur_array_float[5];

    for (let i = 1; i < report_actions.length; i++) {
      let m = report_actions[i].querySelector("#minu");
      let s = report_actions[i].querySelector("#sec");
      m.innerHTML = current_dur_array_float_sorted[i][0];
      s.innerHTML = current_dur_array_float_sorted[i][1];
    }
    report_actions[0].querySelector("#minu").innerHTML =
      wholeProcessDuration[0];
    report_actions[0].querySelector("#sec").innerHTML = wholeProcessDuration[1];
  }
});

function getCurrent(pred, currentTime, duration) {
  var total_len = pred.length;
  var ratio = total_len / duration;
  var current_index = Math.floor(currentTime * ratio);
  current_index = Math.min(current_index, total_len - 1);
  return pred[current_index];
}

// Function to format duration in hours, minutes, and seconds
function formatDuration(seconds) {
  const minutes = Math.floor((seconds % 3600) / 60);
  const remainingSeconds = Math.floor(seconds % 60);

  return [minutes, remainingSeconds];
}

// function to get the current phase
function getPhase(pred) {
  //parse the pred data first
  var current_pred = pred;
  // split by space and get the index larger than 0.5
  var current_pred_array = current_pred.split(" ");
  var current_phase = [];
  for (var i = 0; i < current_pred_array.length; i++) {
    if (parseFloat(current_pred_array[i]) > 0.5) {
      current_phase.push(i);
    }
  }
  var indexes = [];
  for (let i = 0; i < current_phase.length; i++) {
    indexes.push(current_phase[i]);
  }
  // format the phase
  if (current_phase.length == 1) {
    current_phase[0] = actionNames[current_phase[0]];
  } else if (current_phase.length >= 2) {
    current_phase[0] =
      actionNames[current_phase[0]] + " \\ " + actionNames[current_phase[1]];
  } else {
    current_phase[0] = "Idle";
    indexes = [8];
  }
  return [current_phase[0], indexes];
}

function getComment(data1, data2, currentTime) {
  var currentFrame = Math.floor(currentTime * 25);
  if (data1[currentFrame] || data2[currentFrame]) {
    if (data1[currentFrame]) {
      playAlarm("alarm-1");
    } else {
      playAlarm("alarm-2");
    }
    return "Critical Operating Area";
  } else return "N/A";
}

// Function to parse frames from data
function parseFrames(data) {
  return data.split("\n").map((line) => line.trim() === "1");
}

function parsePred(data) {
  return data.split("\n").map((line) => line.trim());
}

// function to update the prediction on the video
function updatePredictionOnVideo(
  data1,
  data2,
  pred,
  cur_dur,
  currentTime,
  ratio
) {
  /*=================================
              Phase information
      ==================================*/
  //get the current phase
  var res = getPhase(pred);
  var phase = res[0];
  var phase_index = res[1];
  // map cur_dur to the current time (minute and second)
  durs = cur_dur.split(" ");
  var phase_dur = "";
  // get the current phase duration
  if (phase_index.length == 1) {
    phase_dur = formatDuration(parseFloat(durs[phase_index[0]]) / ratio);
    phase_dur = phase_dur[0] + " min " + phase_dur[1] + " s";
  } else if (phase_index.length >= 2) {
    phase_dur1 = formatDuration(parseFloat(durs[phase_index[0]]) / ratio);
    phase_dur = phase_dur1[0] + " min " + phase_dur1[1] + " s\\";
    phase_dur2 = formatDuration(parseFloat(durs[phase_index[1]]) / ratio);
    phase_dur += phase_dur2[0] + " min " + phase_dur2[1] + " s";
  }

  var phaseInfoDiv = document.getElementById("phaseInfoDiv");
  phaseInfoDiv.innerHTML = `
        <p id="phaseInfo"></p>
        <p><strong>Current Phase:</strong> ${phase}</p>
        <p><strong>Phase Duration:</strong>  ${phase_dur}</p>
        <p><strong>Total Duration:</strong>  
        ${formatDuration(currentTime)[0]} min ${
    formatDuration(currentTime)[1]
  } s
        </p>
        <p id="comment"></p>
        `;
  phaseInfoDiv.style.display = "block";
  // add the case information div to the video div
  /*=================================
       Comment information(speaker icon)
      ==================================*/
  document.getElementById("comment").innerHTML =
    '<strong>Comment: </strong><span id="commentText"></span>';
  var comment = getComment(data1, data2, currentTime);
  var commentElement = document.getElementById("commentText");
  commentElement.innerHTML = comment;

  const iconContainer = document.getElementById("icon-container");
  // remove all children of the icon container
  while (iconContainer.firstChild) {
    iconContainer.removeChild(iconContainer.firstChild);
  }
  // change the color to red if the comment is not "N/A"
  if (comment !== "N/A") {
    commentElement.style.color = "red";
    //bold
    commentElement.style.fontWeight = "bold";
    const icon = createSpeakerIcon();
    iconContainer.appendChild(icon);
  } else {
    commentElement.style.color = "white"; // change color back to white if comment is "N/A"
  }
}

const item_color = [
  [255, 255, 255],
  [8, 55, 117],
];

function prob2color(prob) {
  var color = [];
  for (let i = 0; i < 3; i++) {
    color.push(
      Math.round(
        item_color[0][i] + (item_color[1][i] - item_color[0][i]) * prob
      )
    );
  }
  return `rgb(${color[0]}, ${color[1]}, ${color[2]})`;
}

// function to update the timeline
function updateTimeline(pred, vid_len) {
  const timeline_blocks = document.querySelectorAll(
    ".timeline-box .cls-line .blocks"
  );
  pred = pred.split(" ");
  pred_sorted = [];

  for (let i = 0; i < idx_map.length; i++) {
    pred_sorted.push(parseFloat(pred[idx_map[i][1]]));
  }
  for (let i = 0; i < pred_sorted.length; i++) {
    let block = timeline_blocks[i];
    let prob = pred_sorted[i];
    let item = createBlockItem(prob2color(prob));
    block.appendChild(item);
  }
}

function createBlockItem(color) {
  const block = document.createElement("div");
  block.className = "block-item";
  block.style.backgroundColor = color;
  return block;
}

function playPause(video) {
  if (video.paused) {
    video.play();
  } else {
    video.pause();
  }
}
