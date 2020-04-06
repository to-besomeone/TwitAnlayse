let today = new Date();

let year = today.getFullYear();
let month = today.getMonth()+1;
let date = today.getDate();

today = year+'-'+month+'-'+date;
let minday = today.getDate()-7;

document.getElementById("udate").setAttribute("max", today);
document.getElementById("sdate").setAttribute("min", minday);

function dateValidate(){
    let maxdate = document.getElementById("udate");
    let mindate = document.getElementById("sdate");

    if(maxdate > today) return false;
    if(mindate < minday) return false;

    return true;
}
