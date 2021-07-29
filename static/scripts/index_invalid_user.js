/**
* Start the script, and display an abstract.
*/
function start() {
    var id_ = document.getElementById("textfield").value;
    if (id_ === undefined || id_ === '') {
      return ;
    } else {
      post("/start/", {"userid": id_})
    }
}

// So you can press enter and it will continue.
function keyPress(e){
  var x = e || window.event;
  var key = (x.keyCode || x.which);
  if(key == 13 || key == 3){
   document.getElementById("start-but").click();
  }
}

document.onkeypress = keyPress; // actually submit when the enter is pressed.

// When you click the start button, call the "start" function.
$("#start-but").click(start);
