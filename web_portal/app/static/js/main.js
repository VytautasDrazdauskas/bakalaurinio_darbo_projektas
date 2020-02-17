function selectElement(id, valueToSelect) {
  let element = document.getElementById(id);
  element.value = valueToSelect;
}

//Klaidos ir informaciniai pranešimai
function fadeIn(el) {
  var steps = 0;
  document.body.appendChild(el);
  var timer = setInterval(function() {
    steps++;
    el.style.opacity = 0.05 * steps;
    if (steps >= 20) {
      clearInterval(timer);
      timer = undefined;
    }
  }, 20);
}

function fadeOut(el) {
  var steps = 20;
  var timer = setInterval(function() {
    steps--;
    el.style.opacity = 0.05 * steps;
    if (steps == 0) {
      clearInterval(timer);
      timer = undefined;
      el.parentNode.removeChild(el);
    }
  }, 20);
}

function createLoader() {
  if (!$("#loader-div")[0]) {
    var el = document.createElement("div");
    el.setAttribute("class", "loader");
    el.setAttribute("id", "loader-div");
    //fadeIn(el);
    document.body.appendChild(el);
    el.style.opacity = 1;

    //uztemdom ekrana
    var overlay = document.createElement("div");
    overlay.setAttribute("class", "overlay");
    document.body.appendChild(overlay);
    overlay.style.opacity = 1;
    //fadeIn(overlay);
  }
}

function removeLoader() {
  var elements = document.getElementsByClassName("loader");
  for (var i = 0; i < elements.length; i++) {
    //fadeOut(elements[i]);
    elements[i].style.opacity = 0;
    elements[i].parentNode.removeChild(elements[i]);
  }
  //atstatom ekrana
  var overlays = document.getElementsByClassName("overlay");
  for (var i = 0; i < overlays.length; i++) {
    //fadeOut(overlays[i]);
    overlays[i].style.opacity = 0;
    overlays[i].parentNode.removeChild(overlays[i]);
  }
}

function notification(msg, duration) {
  var el = document.createElement("div");
  el.setAttribute("class", "notification-box");

  var text = document.createElement("h1");
  text.setAttribute("class", "otification-textnotification-text");

  text.innerHTML = msg;
  el.appendChild(text);
  el.style.opacity = 0;

  setTimeout(function() {
    fadeOut(el);
  }, duration);
  fadeIn(el);
}

function notificationDanger(msg, duration) {
  var el = document.createElement("div");
  el.setAttribute("class", "notification-box-danger");

  var text = document.createElement("h1");
  text.setAttribute("class", "otification-textnotification-text");

  text.innerHTML = msg;
  el.appendChild(text);

  setTimeout(function() {
    fadeOut(el);
  }, duration);
  fadeIn(el);
}

function getResponseMessage(response) {
  var success = JSON.parse(response).success;
  var message = JSON.parse(response).message;
  if (success != null && message != null)
    if (success) {
      notification(message, 2000);
    } else {
      notificationDanger(message, 5000);
    }
  else {
    notificationDanger(response.rensponseText, 5000);
  }
}

function getErrorMessage(response) {
  var message = response.responseText;
  var code = response.status;
  notificationDanger("Klaidos: " + message, 5000);
}

function GetBoolean(data) {
  if (data == "True" || data == "1" || data == "Yes" || data == "yes") {
    return true;
  } else {
    return false;
  }
}

function ControlDevice(device_id, command) {
  createLoader();
  $.ajax({
    url: "/device-action",
    type: "POST",
    data: {
      device_id: device_id,
      command: command
    },
    success: function(response) {
      removeLoader();
      getResponseMessage(response);
    },
    error: function(error) {
      removeLoader();
      getErrorMessage(error);
    }
  });
}

function ConfigDevice(device_id, type, data) {
  createLoader();
  $.ajax({
    url: "/configure-device",
    type: "POST",
    data: {
      device_id: device_id,
      type: type,
      data: data
    },
    success: function(response) {
      removeLoader();
      getResponseMessage(response);
    },
    error: function(error) {
      removeLoader();
      getErrorMessage(error);
    }
  });
}

$(document).ready(function() {
  //Submit mygtuko veiksmai
  $("form").submit(function(e) {
    createLoader();
  });

  $("#refresh-btn").on("click", function() {
    createLoader();
  });
});

function getKeys(obj) {
  var keys = [];
  for (var key in obj) {
    if (key != "id" && key != "date") {
      keys.push(key);
    }
  }
  keys = keys.reverse();
  return keys;
}

function drawGraph(data) {
  var keys = getKeys(data[0]);

  //naikinam anksciau sugeneruotus childus
  const mainNode = document.getElementById("main-chart-wrap");
  while (mainNode.firstChild) {
    mainNode.removeChild(mainNode.firstChild);
  }

  const secNode = document.getElementById("sec-chart-wrap");
  while (secNode.firstChild) {
    secNode.removeChild(secNode.firstChild);
  }

  var mainGraph = true;
  for (let key of keys) {
    var labels = [];
    var values = [];

    for (var i = 0; i < data.length; i++) {
      labels.push(data[i].date);
      values.push(data[i][key]);
    }

    var chartTitle = key.toUpperCase();

    let config = {
      type: "line",
      data: {
        labels: labels,
        datasets: [
          {
            backgroundColor: "#ecfdf6b0",
            borderColor: "#b7f0da",
            pointBackgroundColor: "#70c0b5",
            data: values
          }
        ]
      },
      options: {
        legend: {
          display: false
        },
        title: {
          display: true,
          text: chartTitle
        }
      }
    };

    var chartId = "chart-" + key;
    var windowWidth = $(window).width();

    let chart = document.createElement("canvas");

    chart.setAttribute("id", chartId);

    if (mainGraph) {
      $("#main-chart-wrap").append(chart);
      chart.width = windowWidth * 0.6;
      chart.height = windowWidth * 0.3;
      mainGraph = false;
    } else {
      let column = document.createElement("div");
      column.setAttribute("class", "form-value-column");
      chart.width = windowWidth * 0.2;
      chart.height = windowWidth * 0.3;
      column.append(chart);
      $("#sec-chart-wrap").append(column);
    }

    new Chart(chart.getContext("2d"), config);
  }
}

//https://stackoverflow.com/questions/9050763/format-date-in-jquery
function formatDate(d) {
  // padding function
  var s = function(a, b) {
    return (1e15 + a + "").slice(-b);
  };

  // default date parameter
  if (typeof d === "undefined") {
    d = new Date();
  }

  // return ISO datetime
  return (
    d.getFullYear() +
    "-" +
    s(d.getMonth() + 1, 2) +
    "-" +
    s(d.getDate(), 2) +
    " " +
    s(d.getHours(), 2) +
    ":" +
    s(d.getMinutes(), 2) +
    ":" +
    s(d.getSeconds(), 2)
  );
}

function formatJsonDate(d) {
  // padding function
  var s = function(a, b) {
    return (1e15 + a + "").slice(-b);
  };

  // default date parameter
  if (typeof d === "undefined") {
    d = new Date();
  }

  // return ISO datetime
  return (
    d.getFullYear() +
    "-" +
    s(d.getMonth() + 1, 2) +
    "-" +
    s(d.getDate(), 2) +
    "T" +
    s(d.getHours(), 2) +
    ":" +
    s(d.getMinutes(), 2) +
    ":" +
    s(d.getSeconds(), 2)
  );
}
