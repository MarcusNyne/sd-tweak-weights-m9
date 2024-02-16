function m9_tweak_weights_tolower(str) {
  if (typeof str === "string")
    return str.toLowerCase();
  return "";
}

function m9_tweak_weights_find_child(ele, tag, cls=null) {
  tag = m9_tweak_weights_tolower(tag);
  // console.log ("Parent: "+String(ele));
  for (let i = 0; i < ele.childNodes.length; i++) {
    // console.log(String(i)+": "+String(ele.childNodes[i])+" > "+m9_tweak_weights_tolower(ele.childNodes[i].tagName));
    // console.log(String(i)+": "+String(ele.childNodes[i])+" # "+String(ele.childNodes[i].classList));
    if (m9_tweak_weights_tolower(ele.childNodes[i].tagName)==tag &&
          (cls === null || ele.childNodes[i].classList.contains(cls)))
      return ele.childNodes[i];
  }
  return null;
}

m9_tweak_weights_accordion_element = null;
m9_tweak_weights_check_element = null;

function m9_tweak_weights_update_enabled(event) {
  // console.log("checked: " + String(m9_tweak_weights_check_element.checked))
  if (m9_tweak_weights_check_element!=null) {
    if (m9_tweak_weights_check_element.checked)
      m9_tweak_weights_accordion_element.classList.add("enabled");
    else
      m9_tweak_weights_accordion_element.classList.remove("enabled");
  }
}

function m9_tweak_weights_loaded() {
  // alert ('loaded')
  let m9_tweak_weights_accordion = document.getElementById("m9-tweak-weights-accordion")
  let m9_tweak_weights_enabled = document.getElementById("m9-tweak-weights-enabled")

  if (m9_tweak_weights_accordion==null || m9_tweak_weights_enabled==null)
    setTimeout(() => { m9_tweak_weights_loaded() }, 500);
  else
  {
    // console.log("got both")
    m9_tweak_weights_accordion_element = m9_tweak_weights_find_child(m9_tweak_weights_accordion, "div", "label-wrap");
    // console.log("m9_tweak_weights_accordion_element: "+String(m9_tweak_weights_accordion_element));
    
    ele = m9_tweak_weights_find_child(m9_tweak_weights_enabled, "label");
    if (ele!=null) {
      m9_tweak_weights_check_element = m9_tweak_weights_find_child(ele, "input");
      if (m9_tweak_weights_check_element!=null){
        // console.log("Found: "+String(m9_tweak_weights_check_element)+" > "+String(m9_tweak_weights_check_element.tagName));
        m9_tweak_weights_check_element.addEventListener("click", m9_tweak_weights_update_enabled);
        m9_tweak_weights_update_enabled(null);
      }
    }
  }
}

document.addEventListener("DOMContentLoaded", function() {
  setTimeout(() => {  m9_tweak_weights_loaded() }, 500);
});
