const socket = io();

let username =
document.querySelector(".profile h4").innerText;

let currentRoom = "General";

// JOIN DEFAULT ROOM
socket.emit("join_room", {
    username: username,
    room: currentRoom
});

// SEND MESSAGE
function sendMessage(){

    let input =
    document.getElementById("message");

    let msg = input.value;

    if(msg.trim() === "") return;

    let time = new Date().toLocaleTimeString([], {

        hour:'2-digit',
        minute:'2-digit'

    });

    socket.emit("send_message", {

        username: username,
        message: msg,
        room: currentRoom,
        time: time

    });

    input.value = "";
}

// RECEIVE MESSAGE
socket.on(
    "receive_message",
    function(data){

    let messages =
    document.getElementById("messages");

    let div =
    document.createElement("div");

    div.classList.add("message");

    if(data.username === username){

        div.classList.add("sent");

    }else{

        div.classList.add("received");
    }

    div.innerHTML = `
        <strong>${data.username}</strong><br>
        ${data.message}
        <div class="time">${data.time}</div>
    `;

    messages.appendChild(div);

    messages.scrollTo({

        top: messages.scrollHeight,
        behavior: "smooth"

    });
});

// JOIN ROOM
function joinRoom(room){

    currentRoom = room;

    document.getElementById(
        "room-name"
    ).innerText = room;

    document.getElementById(
        "messages"
    ).innerHTML = "";

    socket.emit("join_room", {

        username: username,
        room: room

    });
}

// TYPING
function typing(){

    socket.emit("typing", {

        username: username,
        room: currentRoom

    });
}

// SHOW TYPING
socket.on("show_typing", function(msg){

    document.getElementById(
        "typing"
    ).innerText = msg;

    setTimeout(() => {

        document.getElementById(
            "typing"
        ).innerText = "";

    },1000);
});

// NOTIFICATION
socket.on("notification", function(msg){

    let messages =
    document.getElementById("messages");

    let div =
    document.createElement("div");

    div.classList.add("notify");

    div.innerHTML = msg;

    messages.appendChild(div);
});

// EMOJI
function addEmoji(emoji){

    let input =
    document.getElementById("message");

    input.value += emoji;
}

// SEARCH
function searchChats(){

    let input =
    document.getElementById(
        "searchInput"
    ).value.toLowerCase();

    let contacts =
    document.querySelectorAll(".contact");

    contacts.forEach(contact => {

        let text =
        contact.innerText.toLowerCase();

        if(text.includes(input)){

            contact.style.display = "block";

        }else{

            contact.style.display = "none";
        }

    });
}

// MOBILE SIDEBAR
function toggleSidebar(){

    document.getElementById(
        "sidebar"
    ).classList.toggle("active");
}