const img = document.getElementById("img");
const imageForm = document.getElementById("imageForm");
const submitButton = document.getElementById("submitButton");
const apiURL = (window.location.hostname === "dev.darim.dev") ? "https://imagebuilder.onrender.com" : "http://localhost:5000";


function enableElement(element) {
    element.disabled = false;
    element.classList.remove("noHover");
}

function disableElement(element) {
    element.disabled = true;
    element.classList.add("noHover");
}

async function apiImageFetch(endpoint, formData, callback) {
    try {
        const response = await fetch(`${apiURL}/${endpoint}`, {
            method: "POST",
            body: formData
        });
        if (response.headers.get("content-type").startsWith("image/")) {
            const blob = await response.blob();
            img.src = URL.createObjectURL(blob);
        } else if (response.headers.get("content-type") === "application/json") {
            const data = await response.json();
            alert(`Error: ${data.error}`);
        } else
            alert("Please wait before sending more requests");
    } catch(e) {
        console.error("Error:", e);
        alert("An error occurred. Please try again.");
    }
    callback();
}

function addFormListener(formObjectTypes, endpoint) {
    imageForm.addEventListener("submit", (event) => {
        event.preventDefault();
        const formData = new FormData();
        
        for (id in formObjectTypes) {
            if (formObjectTypes[id] === "files") {
                const files = document.getElementById(id).files;
                for (var i = 0; i < files.length; i++)
                    formData.append(id, files[i]);
            } else if (formObjectTypes[id] === "value")
                formData.append(id, document.getElementById(id).value);
        }

        img.src = "images/loading.gif";
        disableElement(submitButton);
        apiImageFetch(endpoint, formData, () => {
            if (img.src.indexOf("images/loading.gif") !== -1)
                img.src = "";
            enableElement(submitButton);
        });
    });
}