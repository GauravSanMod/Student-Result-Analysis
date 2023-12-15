function valid_password(){
    var passInput = document.getElementById('password')
    var passError = document.getElementById('pass_error')

    if(/^(?=.*[\d])(?=.*[A-Z])(?=.*[a-z])(?=.*[!@#$%^&*+?~]).{8,}$/.test(passInput.value)){
        passError.textContent="";
    }
    else{
        passError.textContent="Password should contain(lower and uppercase,digit,special_char) length=8+";
    }
}
function valid_email(){
    var email_input=document.getElementById('email')
    var email_error = document.getElementById("email_error")

    if(/^[a-zA-Z]\w*[@][a-z]+[.][a-z]{1,5}$/.test(email_input.value)){
        email_error.textContent='';
    }
    else{
        email_error.textContent='Invalid Email Address check(eg:test@gmail.com)';
    }
}
function valid_name(){
    var name_input = document.getElementById("name")
    var name_error = document.getElementById('name_error')
    if (/[a-zA-Z]+/.test(name_input.value)){
        name_error.textContent = '';
    }
    else{
        name_error.textContent = "Invalid Name it should has[a-zA-Z]";
    }
}