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
  // append the chunk as a file field with name "chunk"
  formData.append("chunk", chunk);
  // append the other fields as text fields with their names and values
  formData.append("index", index);
  formData.append("total", total);
  formData.append("md5", md5);
  formData.append("file_name", filename);
  // create a XMLHttpRequest object
  var xhr = new XMLHttpRequest();
  var username = "Lstriving";
  var password = "5201314..Qq";
  var encoded = window.btoa(username + ":" + password); // dXNlcjpwYXNz

  // open a POST request to the given url
  xhr.open("POST", "/easyshare/chunk/folder/" + folder_id);
  xhr.setRequestHeader("Authorization", "Basic " + encoded);
  xhr.setRequestHeader("X-CSRFToken", csrftoken);

  // set the onload callback function
  xhr.onload = function () {
    // if the status is 200 (OK)
    if (xhr.status == 200) {
      // log the response text to the console
      console.log(xhr.responseText);
    } else {
      // log an error message to the console
      console.error("Request failed: " + xhr.status);
    }
  };
  // set the onerror callback function
  xhr.onerror = function () {
    // log an error message to the console
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
    alert("Please select a file");
    return;
  }
  // get the chunk size from the input element by id "size"
  var size = document.getElementById("size").value;
  // parse the size as an integer and validate it, alert a message and return if invalid
  size = parseInt(size);
  if (isNaN(size) || size <= 0) {
    alert("Please enter a valid chunk size");
    return;
  }
  // calculate the md5 hash of the file using the md5 function
  md5File(file)
    .then(function (hash) {
      // display the hash in the span element by id "hash"
      document.getElementById("hash").textContent = hash;
      // split the file into chunks using the split function
      var chunks = split(file, size);
      // display the number of chunks in the span element by id "chunks"
      document.getElementById("chunks").textContent = chunks.length;
      // store the chunks, hash and file name in global variables for later use
      window.chunks = chunks;
      window.hash = hash;
      window.filename = file.name;
    })
    .catch(function (error) {
      // if there is an error calculating the hash, alert a message and log the error to the console
      alert("Error calculating md5 hash");
      console.error(error);
    });
}

// function to handle the click event of the send button
async function sendAll() {
  // get the global variables for the chunks, hash and file name
  var chunks = window.chunks;
  var hash = window.hash;
  var filename = window.filename;
  // get the chunk size from the input element by id "size"
  var folder_id = document.getElementById("folder_id").value;
  // if any of them is undefined, alert a message and return
  if (!chunks || !hash || !filename) {
    alert("Please calculate first");
    return;
  }
  // loop through the chunks
  for (var i = 0; i < chunks.length; i++) {
    // get the current chunk and its index
    var chunk = chunks[i];
    var index = i + 1;
    // send the chunk and other fields using the send function
    await send(chunk, index, chunks.length, hash, filename, folder_id);
  }
}

function check_upload_status() {
  var hash = window.hash;
  // create a XMLHttpRequest object
  var xhr = new XMLHttpRequest();
  var username = "Lstriving";
  var password = "5201314..Qq";
  var encoded = window.btoa(username + ":" + password); // dXNlcjpwYXNz

  // open a get request to the given url
  xhr.open("GET", "/easyshare/large_file_upload_status?md5=" + hash);
  xhr.setRequestHeader("Authorization", "Basic " + encoded);
  xhr.setRequestHeader("X-CSRFToken", csrftoken);
  // set the onload callback function
  xhr.onload = function () {
    document.getElementById("status").textContent = xhr.responseText;
  };
  // set the onerror callback function
  xhr.onerror = function () {
    // log an error message to the console
    console.error("Network error");
  };
  // send the request with the form data
  xhr.send();
}
function create_file_instance() {
  // create a XMLHttpRequest object
  var xhr = new XMLHttpRequest();
  var username = "Lstriving";
  var password = "5201314..Qq";
  var encoded = window.btoa(username + ":" + password); // dXNlcjpwYXNz
  // var folder_id = document.getElementById("folder_id").value;
  var folder_id = 2;
  // open a get request to the given url
  xhr.open("POST", "/easyshare/large_file_create/folder_id/" + folder_id);
  xhr.setRequestHeader("Authorization", "Basic " + encoded);
  xhr.setRequestHeader("X-CSRFToken", csrftoken);
  xhr.setRequestHeader("Content-Type", "application/json");
  xhr.send(JSON.stringify({ md5: window.hash }));
  // set the onload callback function
  xhr.onload = function () {
    if (xhr.status == 200) {
      // log the response text to the console
      document.getElementById("status").textContent = "Create success!";
    } else if (xhr.status == 201) {
      document.getElementById("status").textContent = "Already created!";
    } else {
      document.getElementById("status").textContent = xhr.responseText;
    }
  };
  // set the onerror callback function
  xhr.onerror = function () {
    // log an error message to the console
    console.error("Network error");
  };
  // send the request with the form data
}