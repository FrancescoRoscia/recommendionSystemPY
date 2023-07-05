function clickButton(){
    var button = document.getElementById("buttonSave");
    button.click();
}


function btnSureDelete(){
    var check = document.getElementById("checkSure");
    var sendBtn = document.getElementById("btnDelete");

    if(check.checked){
        sendBtn.disabled = false;
    }else{
        sendBtn.disabled = true;
    }
}

function checkPassword(){
    var oldPass = document.getElementById("oldPassword");
    var newPass = document.getElementById("newPassword");
    var changeBtn = document.getElementById("btnChangePass");

    if (oldPass.value.length >= 4 && newPass.value.length >= 4){
        changeBtn.disabled = false;
    }else{
        changeBtn.disabled = true;
    }
}

function checkUsername(){
    var username = document.getElementById("username");
    var changeBtn = document.getElementById("btnChangeUsername");

    if (username.value.length >= 3){
        changeBtn.disabled = false;
    }else{
        changeBtn.disabled = true;
    }
}