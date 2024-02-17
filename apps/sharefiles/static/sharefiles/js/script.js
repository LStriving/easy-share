const CHUNK_FREE = 1;
const DONE = 2;
const CHUNK_SIZE = 5;
const WAIT_MERGE = 3;
var uploaded_chunks_num = {};

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

$(document).ready(function () {
  $("form input").change(function () {
    $("form p").text(this.files.length + " file(s) selected");
  });
});

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
const csrftoken = getCookie("csrftoken");
// Define a function to calculate MD5 hash of a file
function md5File(file) {
  // Create a promise to return the result
  var promise = new Promise(function (resolve, reject) {
    // Create a FileReader object
    var reader = new FileReader();
    // Read the file as an array buffer
    reader.readAsArrayBuffer(file);
    // When the file is loaded
    reader.onload = function () {
      // Get the array buffer from the reader
      var buffer = reader.result;
      // Calculate the MD5 hash using the js-md5 library
      var hash = md5(buffer);
      // Resolve the promise with the hash
      resolve(hash);
    };
    // If there is an error reading the file
    reader.onerror = function () {
      // Reject the promise with the error
      reject(reader.error);
    };
  });
  // Return the promise
  return promise;
}
// function to split a file into chunks of a given size
function split(file, size) {
  // create an array to store the chunks
  var chunks = [];
  // get the file size in bytes
  var fileSize = file.size;
  // calculate the number of chunks
  size *= 1048576;
  var numChunks = Math.ceil(fileSize / size);
  // loop through the chunks
  for (var i = 0; i < numChunks; i++) {
    // get the start and end byte positions of the chunk
    var start = i * size;
    var end = Math.min(start + size, fileSize);
    // slice the file into a chunk
    var chunk = file.slice(start, end);
    // push the chunk to the array
    chunks.push(chunk);
  }
  // return the array of chunks
  return chunks;
}

// function to send a multipart/form-data request with a chunk and other fields
async function send(chunk, index, total, md5, filename, folder_id) {
  // create a FormData object
  var formData = new FormData();
  formData.append("chunk", chunk);
  formData.append("index", index);
  formData.append("total", total);
  formData.append("md5", md5);
  formData.append("file_name", filename);
  // create a XMLHttpRequest object
  var xhr = new XMLHttpRequest();

  // open a POST request to the given url
  xhr.open("POST", "/easyshare/chunk/folder/" + folder_id);
  xhr.setRequestHeader("X-CSRFToken", csrftoken);

  // set the onload callback function
  xhr.onload = function () {
    if (xhr.status == 200) {
      if (uploaded_chunks_num[md5] === undefined) {
        uploaded_chunks_num[md5] = 1;
      } else {
        uploaded_chunks_num[md5] += 1;
      }
      updateProgress(
        ((uploaded_chunks_num[md5] / total) * 100).toFixed(2),
        md5
      );
    } else {
      // log an error message to the console
      console.error(
        "upload chunks failed: " + xhr.status + " " + xhr.responseText
      );
    }
  };
  // set the onerror callback function
  xhr.onerror = function () {
    console.error("Network error");
  };
  // send the request with the form data
  xhr.send(formData);
}

// function to handle the click event of the calculate button
function calculate() {
  // get the input element by id "file"
  var input = document.getElementById("file");
  // get the first file from the input element's files property
  var file = input.files[0];
  // if there is no file selected, alert a message and return
  if (!file) {
    showNotification("error", "Error", "Please select a file");
    return Promise.reject("No file selected");
  }

  // return a promise for the asynchronous operations
  return new Promise((resolve, reject) => {
    // calculate the md5 hash of the file using the md5File function
    md5File(file)
      .then(function (hash) {
        // display the hash in the span element by id "hash"
        // document.getElementById("hash").textContent = hash;
        // split the file into chunks using the split function
        var chunks = split(file, CHUNK_SIZE);
        // display the number of chunks in the span element by id "chunks"
        // document.getElementById("chunks").textContent = chunks.length;
        // store the chunks, hash, and file name in global variables for later use
        window.chunks = chunks;
        window.hash = hash;
        window.filename = file.name;
        resolve(hash);
      })
      .catch(function (error) {
        // if there is an error calculating the hash, alert a message and log the error to the console
        showNotification("error", "Error", "Error calculating MD5 hash");
        console.error(error);
        reject(error);
      });
  });
}

function check_upload_status(hash) {
  return new Promise((resolve, reject) => {
    // create a XMLHttpRequest object
    var xhr = new XMLHttpRequest();

    // open a GET request to the given URL
    xhr.open("GET", "/easyshare/large_file_upload_status?md5=" + hash);
    xhr.setRequestHeader("X-CSRFToken", csrftoken);

    xhr.onreadystatechange = async function () {
      if (xhr.readyState == 4) {
        if (xhr.status == 201) {
          resolve(DONE);
        } else if (xhr.status == 202) {
          resolve(WAIT_MERGE);
        } else if (xhr.status == 200) {
          const merge_status = await mergeChunks(hash);
          if (merge_status === DONE) {
            resolve(DONE);
          } else if (merge_status === WAIT_MERGE) {
            resolve(WAIT_MERGE);
          } else {
            resolve(parsePartialResponse(merge_status));
          }
        } else if (xhr.status == 500 || xhr.status == 503) {
          showNotification("error", "Server error", "Please try again later");
          reject(new Error("Server error"));
        } else if (xhr.status == 206) {
          // parse the response for uploaded chunks
          var uploaded_chunks = parsePartialResponse(xhr.responseText);
          resolve(uploaded_chunks);
        } else if (xhr.status == 404) {
          resolve(null);
        } else {
          // log an error message to the console
          console.log("Request failed: " + xhr.status);
          console.log(xhr.responseText);
          reject(new Error("Request failed: " + xhr.status));
        }
      }
    };

    // set the onload callback function
    xhr.onload = function () {
      document.getElementById("loading-msg").textContent = xhr.responseText;
    };

    // set the onerror callback function
    xhr.onerror = function () {
      // log an error message to the console
      console.error("Network error");
      reject(new Error("Network error"));
    };

    // send the request with the form data
    try {
      xhr.send();
      return xhr.status;
    } catch (error) {
      console.log(error);
      return null;
    }
  });
}

function parsePartialResponse(responseText) {
  var response = JSON.parse(responseText);
  var uploaded = response.message;
  var uploaded_chunks = uploaded
    .split("Index")[1]
    .split("are")[0]
    .split("{")[1]
    .split("}")[0];
  var uploaded_chunks = uploaded_chunks.split(",");
  uploaded_chunks = uploaded_chunks.map((x) => parseInt(x));
  return uploaded_chunks;
}

function mergeChunks(hash) {
  return new Promise((resolve, reject) => {
    //send a request to merge the chunks when the upload is complete
    var xhr = new XMLHttpRequest();
    xhr.open("GET", "/easyshare/merge_chunks?md5=" + hash);
    xhr.setRequestHeader("X-CSRFToken", csrftoken);
    xhr.onload = function () {
      if (xhr.status == 200) {
        console.log("Chunks merged successfully");
        resolve(DONE);
      } else if (xhr.status == 202) {
        console.log("Chunks are merging");
        resolve(WAIT_MERGE);
      } else if (xhr.status == 206) {
        console.log(xhr.responseText);
        resolve(xhr.responseText);
      } else {
        console.error("Chunks merged failed");
        reject(new Error("Chunks merged failed"));
      }
    };
    xhr.onerror = function () {
      console.error("Network error");
      reject(new Error("Network error"));
    };
    xhr.send();
  });
}

function create_file_instance(hash) {
  return new Promise((resolve, reject) => {
    var xhr = new XMLHttpRequest();
    var folder_id = window.location.pathname.split("/").pop();

    xhr.open("POST", "/easyshare/large_file_create/folder_id/" + folder_id);
    xhr.setRequestHeader("X-CSRFToken", csrftoken);
    xhr.setRequestHeader("Content-Type", "application/json");

    xhr.onload = function () {
      if (xhr.status == 200) {
        document.getElementById("loading-msg").textContent = "Create success!";
        resolve(DONE);
      } else if (xhr.status == 201) {
        document.getElementById("loading-msg").textContent = "Already created!";
        resolve(DONE);
      } else if (xhr.status == 500 || xhr.status == 503) {
        showNotification(
          "error",
          "Server error",
          "Server error, please try again later"
        );
        reject(new Error("Server error"));
      } else if (xhr.status == 303) {
        showNotification("error", "Error", "Chunks merged failed");
        resolve(null);
      } else {
        document.getElementById("loading-msg").textContent = xhr.responseText;
        showNotification("error", "Error", xhr.responseText);
        reject(new Error(xhr.responseText));
      }
    };

    xhr.onerror = function () {
      console.error("Network error");
      reject(new Error("Network error"));
    };

    xhr.send(JSON.stringify({ md5: hash }));
  });
}

$(document).ready(function () {
  $("#upload-file input").change(function () {
    $("#upload-file p").text(this.files.length + " file(s) selected");
  });
});

function updateProgress(percentage, md5) {
  percentage = Math.max(percentage, 100);
  document.getElementById("progress-data-" + md5).innerHTML = percentage + "%";
  document.getElementById("progress-data-" + md5).style.width =
    percentage + "%";
}

// Configure XMLHttpRequest for progress tracking
async function handleUpload() {
  // get the input element by id "file"
  var input = document.getElementById("file");
  // get the first file from the input element's files property
  var file = input.files[0];
  // if there is no file selected, alert a message and return
  if (!file) {
    showNotification("error", "Error", "Please select a file");
    return;
  }
  // check if the file is not video
  if (!file.type.includes("video")) {
    showNotification("error", "Error", "Please select a video file");
    return;
  }
  //unblur_preloader the background
  document.getElementById("upload-file").style.display = "none";
  $("body div:not(#upload-file)").css("filter", "blur(0px)");

  // get folder id from the url
  let folder_id = window.location.pathname.split("/").pop();

  // display the preparing message
  $("body div:not(#preloader)").css("filter", "blur(5px)");
  document.getElementById("spinner").style.filter = "blur(0px)";
  document.getElementById("preloader").style.display = "block";
  document.getElementById("loading-msg").textContent = "Preparing Upload";

  calculate()
    .then(async (md5_value) => {
      document.getElementById("loading-msg").textContent =
        "Calculated MD5 hash";
      // display progress bar
      await insertUploadFileDiv(md5_value, file.name);
      // Successfully calculated MD5 hash, proceed with the next steps
      console.log("MD5 hash calculated:", md5_value);
      $("upload-file-name").textContent = file.name;
      var current_status = await check_upload_status(md5_value);

      document.getElementById("preloader").style.display = "none";
      $("body div:not(#preloader)").css("filter", "blur(0px)");
      showNotification("info", "Info", "Start uploading");
      // partially uploaded
      let uploaded_chunks = [];
      var result = null;
      while (current_status !== DONE && current_status !== WAIT_MERGE) {
        uploaded_chunks = [];
        if (current_status != null) {
          uploaded_chunks = current_status;
        }
        uploaded_chunks_num[md5_value] = uploaded_chunks.length;

        // split the file into chunks using the split function
        let chunks = split(file, CHUNK_SIZE);

        // loop through the chunks
        for (var i = 0; i < chunks.length; i++) {
          if (uploaded_chunks.includes(i + 1)) {
            console.log("chunk " + (i + 1) + " already uploaded");
            continue;
          }

          var chunk = chunks[i];
          var index = i + 1;

          await send(
            chunk,
            index,
            chunks.length,
            md5_value,
            file.name,
            folder_id
          );
        }
        result = await mergeChunks(md5_value);
        if (result !== DONE && result !== WAIT_MERGE) {
          // partially uploaded
          continue;
        }
        if (result === DONE) {
          current_status = DONE;
        }

        current_status = await check_upload_status(md5_value);
      }

      if (current_status === DONE) {
        const status = await create_file_instance(md5_value);
        if (status === DONE) {
          updateProgress(100, md5_value);
          document.getElementById("loading-msg").textContent =
            "file instance created";
          // show success message
          showNotification("success", "Success!", "Upload Success!");
          // reload the page
          location.reload();
        } else {
          document.getElementById("loading-msg").textContent =
            "File instance creation failed";
        }
        // endProgressBar(md5_value);
        unblur_preloader();
        document.getElementById("preloader").style.display = "none";
      } else if (current_status == WAIT_MERGE) {
        // send merge request time to time
        showNotification(
          "warning",
          "Message",
          "Merging chunks, please refresh the page later"
        );
      } else {
        console.error("Unknown error, please try again later.");
      }
      endProgressBar(md5_value);
    })
    .catch((error) => {
      $("body div:not(#preloader)").css("filter", "blur(0px)");
      document.getElementById("preloader").style.display = "none";
      showNotification(
        "error",
        "Error",
        "Upload failed, please try again later" + error
      );
      // Handle errors during MD5 calculation
      console.error("Error during MD5 calculation:", error);
    });
}

function unblur_preloader() {
  $("body div:not(#preloader)").css("filter", "blur(0px)");
}

function insertUploadFileDiv(md5, filename) {
  if (document.getElementById(`progress-data-${md5}`)) {
    return;
  }
  var uploadWrapper = document.getElementById("upload-wrapper");

  // Check if the element is found before proceeding
  if (uploadWrapper) {
    // Define the HTML code you want to insert
    var newHtmlCode =
      `<div class="uploaded" id=${md5}>` +
      '<i class="material-icons" id="upload-icon">video_file</i>' +
      '<div class="file">' +
      '<div class="file__name">' +
      `<p>${filename}</p>` +
      '<i class="fas fa-times"></i>' +
      "</div>" +
      '<div class="w3-light-grey w3-round" id="bar">' +
      `<div class="w3-container w3-round w3-green" style="width: 0%" id="progress-data-${md5}">` +
      "0%" +
      "</div>" +
      "</div>" +
      "</div>" +
      "</div>";

    // Insert the new HTML code into the #upload-wrapper element
    uploadWrapper.innerHTML += newHtmlCode;
  } else {
    console.error("#upload-wrapper element not found");
  }
}

function removeEleNChildren(ele) {
  //remove the element and all its children
  var element = document.getElementById(ele);
  while (element.firstChild) {
    element.removeChild(element.firstChild);
  }
  element.remove();
}

function endProgressBar(md5) {
  removeEleNChildren(md5);
}
