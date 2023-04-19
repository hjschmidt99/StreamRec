// get/set parameters of html elements with 'save' attribute

function getParams() {
  var x = {
    "x": window.screenLeft,
    "y": window.screenTop,
    "w": window.outerWidth,
    "h": window.outerHeight,
  };

  document.querySelectorAll("[save='value']").forEach(function(item) {
    x[item.id] = item.value;
  });
  document.querySelectorAll("[save='checked']").forEach(function(item) {
    x[item.id] = item.checked;
  });
  document.querySelectorAll("[save='select']").forEach(function(item) {
    var values = Array.from(item.options).map(e => e.value);
    x[item.id + "_values"] = values;
    x[item.id] = item.value;
  });
  document.querySelectorAll("[save='mru']").forEach(function(item) {
    var values = Array.from(item.options).map(e => e.value);
    x[item.id] = values;
  });

  return x;
}

function setParams(x) {
  document.querySelectorAll("[save='value']").forEach(function(item) {
    if (item.id in x) item.value = x[item.id];
  });
  document.querySelectorAll("[save='checked']").forEach(function(item) {
    if (item.id in x) item.checked = x[item.id];
  });
  document.querySelectorAll("[save='select']").forEach(function(item) {
    if (item.id + "_values" in x)
    {
      while (item.options.length > 0) { item.remove(item.options.length - 1); }
      x[item.id + "_values"].forEach(function(v) {
        var opt = document.createElement('option');
        opt.text = v;
        opt.value = v;
        item.add(opt, null);
      });
    } 
    if (item.id in x) item.value = x[item.id];
  });
  document.querySelectorAll("[save='mru']").forEach(function(item) {
    if (item.id in x)
    {
      while (item.options.length > 0) { item.remove(item.options.length - 1); }
      x[item.id].forEach(function(v) {
        var opt = document.createElement('option');
        opt.text = v;
        opt.value = v;
        item.add(opt, null);
      });
    } 
  });
}


// a textbox can have a selectbox mru list with the id postfix _mru

var mrumax = 10

function addMru(item) {
  var mru = document.getElementById(item.id + "_mru");
  v = item.value;
  
  var opts = mru.options;
  for (var i = 0; i < opts.length; i++) {
    if (opts[i].value == v) {
        mru.removeChild(opts[i]);
        i--;
    }
  }

  var opt = document.createElement('option');
  opt.text = v;
  opt.value = v;
  mru.add(opt, 0);

  while (opts.length > mrumax) 
    mru.removeChild(opts[opts.length - 1]);
}

function useMru(item) {
  var txt = document.getElementById(item.id.replace("_mru", ""));
  txt.value = item.value;
}


//  drag and drop support

window.ondragover = function(ev) {
  ev.stopPropagation();
  ev.preventDefault();
  ev.dataTransfer.dropEffect = 'copy';
}

window.ondrop = function(ev) {
  ev.stopPropagation();
  ev.preventDefault();
  var s = event.dataTransfer.getData("text/plain");
  ev.target.value = s;
}


// there can be a textarea txta for logging
// with autoscroll and text limit

var prmax = 20000;

function pr(text) {
  var s = txta.value + text;
  var l = s.length;
  if (l > prmax) s = s.substring(l - prmax);
  txta.value = s;
  txta.scrollTop = txta.scrollHeight;
}

eel.expose(prl)
function prl(text) {
  pr(text + "\n");
}


// toggle visibility
      
function toggleShow(id) {
  let x = document.getElementById(id).style;
  x.display = x.display == "none" ? "inline" : "none";
  resize()
}
